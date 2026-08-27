import importlib.util
from pathlib import Path
import unittest
from datetime import datetime, timezone


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_release.py"
SPEC = importlib.util.spec_from_file_location("lux_radar_builder", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class BuilderTests(unittest.TestCase):
    def record(self, *, status="UNKNOWN", title="Call de sustentabilidade"):
        return {
            "opportunity_id": "candidate-1",
            "canonical_key": "url:https://example.org/call",
            "title": title,
            "organization": "Example Foundation",
            "status": status,
            "source_id": "source-a",
            "evidence": ["evidence-1"],
            "provenance": {"observation_ids": ["observation-1"], "limitations": []},
            "first_seen_at": "2026-08-25T10:00:00Z",
            "last_seen_at": "2026-08-25T10:00:00Z",
            "updated_at": "2026-08-25T10:00:00Z",
        }

    def test_dedupe_merges_sources_and_evidence(self):
        left = self.record()
        right = self.record()
        right["source_id"] = "source-b"
        right["evidence"] = ["evidence-2"]
        right["provenance"] = {"observation_ids": ["observation-2"], "limitations": []}
        merged = MODULE.dedupe([left, right])
        self.assertEqual(len(merged), 1)
        self.assertEqual(set(merged[0]["evidence"]), {"evidence-1", "evidence-2"})
        self.assertEqual(set(merged[0]["provenance"]["observation_ids"]), {"observation-1", "observation-2"})

    def test_opportunity_identity_and_navigation_filters_are_distinct(self):
        self.assertIsNotNone(MODULE.OPPORTUNITY_TITLE.search("Manifestação de Interesse 04/2026"))
        self.assertIsNotNone(MODULE.NOT_OPPORTUNITY_TITLE.fullmatch("Ações e Programas"))
        self.assertIsNotNone(MODULE.NOT_OPPORTUNITY_TITLE.fullmatch("Projetos e Parcerias"))

    def test_non_sustainability_record_is_retained_and_classified_from_content(self):
        record = self.record(status="CANDIDATE", title="Edital de cultura e educação comunitária")
        record["source_domains"] = ["sustainability"]
        classified = MODULE.reclassify_domains([record], [{"id": "source-a", "domain": ["sustainability"]}])[0]
        self.assertIn("culture", classified["domains"])
        self.assertIn("education", classified["domains"])
        self.assertNotIn("sustainability", classified["domains"])
        self.assertNotIn("sustainability", classified["lens_matches"])
        self.assertIn("sustainability", classified["source_domains"])

    def test_unknown_is_not_current(self):
        lifecycle, experience, current = MODULE.classify_experience(self.record(status="UNKNOWN"), datetime(2026, 8, 26, tzinfo=timezone.utc))
        self.assertEqual((lifecycle, experience, current), ("SIGNAL", "SIGNAL", False))

    def test_open_future_deadline_is_current(self):
        record = self.record(status="OPEN")
        record["deadline"] = "2026-09-30T23:59:59Z"
        lifecycle, experience, current = MODULE.classify_experience(record, datetime(2026, 8, 26, tzinfo=timezone.utc))
        self.assertEqual((lifecycle, experience, current), ("UPCOMING", "OPPORTUNITY", True))

    def test_expired_verified_is_historical(self):
        record = self.record(status="VERIFIED")
        record["deadline"] = "2026-08-20T23:59:59Z"
        lifecycle, experience, current = MODULE.classify_experience(record, datetime(2026, 8, 26, tzinfo=timezone.utc))
        self.assertEqual((lifecycle, experience, current), ("HISTORICAL", "HISTORICAL", False))

    def test_history_marks_update(self):
        old = self.record()
        new = self.record(status="OPEN", title="Call de sustentabilidade atualizada")
        database, stats = MODULE.merge_history([new], [old], "2026-08-26T10:00:00Z")
        self.assertEqual(stats["updated"], 1)
        self.assertEqual(database[0]["status"], "OPEN")
        self.assertEqual(database[0]["history"][-1]["event"], "updated")

    def test_signal_view_contains_source_and_record_without_promoting_source(self):
        record = self.record(status="OPEN")
        record.update({"experience_type": "OPPORTUNITY", "lifecycle_state": "ACTIVE", "current_view": True, "change_type": "NEW", "official_url": "https://example.org/call"})
        observation = {
            "observation_id": "observation-api",
            "source_id": "source-a",
            "source_url": "https://example.org/api",
            "observed_at": "2026-08-27T10:00:00Z",
            "fetch": {"status": "success", "http_status": 200},
            "content": {"content_hash": "sha256:abc", "media_type": "application/json"},
            "claims": [
                {"path": "api.item_count", "value": 2},
                {"path": "api.identifier_keys", "value": ["id"]},
                {"path": "api.preview", "value": [{"id": "1", "name": "Um"}, {"id": "2", "name": "Dois"}]},
            ],
            "evidence_ids": ["evidence-api"],
            "collector": {"name": "test-api"},
            "limitations": [],
        }
        signals, changes = MODULE.build_signal_views([record], [observation], [{"id": "source-a", "name": "API teste", "url": "https://example.org/api", "domain": ["territory"], "source_role": "primary", "signal_type": "territorial_data"}], [], observation["observed_at"])
        self.assertEqual(len(signals), 2)
        source_signal = next(item for item in signals if item["canonical_key"] == "source:source-a")
        record_signal = next(item for item in signals if item["canonical_key"].startswith("record:"))
        self.assertEqual(source_signal["signal_type"], "territorial_data")
        self.assertEqual(source_signal["change_type"], "NEW")
        self.assertEqual(source_signal["observed_item_count"], 2)
        self.assertEqual(record_signal["signal_type"], "opportunity")
        self.assertTrue(record_signal["current_view"])
        self.assertEqual(changes, [])

    def test_source_profile_maps_access_method_to_observation_enum(self):
        self.assertEqual(MODULE.source_profile_for({"access_method": "rest_api", "source_type": "public_api"}), "api")
        self.assertEqual(MODULE.source_profile_for({"access_method": "html", "source_type": "government"}), "html")
        self.assertEqual(MODULE.source_profile_for({"access_method": "html", "source_type": "public_portal"}), "portal")

    def test_source_change_detects_added_removed_and_updated_items(self):
        previous = {"content_hash": "sha256:old", "observed_items": [{"key": "a", "label": "Antes"}, {"key": "b", "label": "Saiu"}]}
        change_type, changes = MODULE._source_change(previous, "sha256:new", [{"key": "a", "label": "Depois"}, {"key": "c", "label": "Entrou"}], "success")
        self.assertEqual(change_type, "UPDATED")
        self.assertEqual({item["kind"] for item in changes}, {"item_added", "item_removed", "item_updated"})


if __name__ == "__main__":
    unittest.main()
