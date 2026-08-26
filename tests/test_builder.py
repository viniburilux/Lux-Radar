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


if __name__ == "__main__":
    unittest.main()
