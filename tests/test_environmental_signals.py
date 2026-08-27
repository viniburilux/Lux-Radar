from __future__ import annotations

import importlib.util
from unittest.mock import patch
import unittest

import requests


SCRIPT = __import__("pathlib").Path(__file__).resolve().parents[1] / "scripts" / "environmental_signals.py"
SPEC = importlib.util.spec_from_file_location("lux_radar_environmental", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class EnvironmentalSignalTests(unittest.TestCase):
    def response(self, url: str, body: str, content_type: str, status: int = 200) -> requests.Response:
        response = requests.Response()
        response.status_code = status
        response.url = url
        response.headers["content-type"] = content_type
        response._content = body.encode("utf-8")
        return response

    def source(self, source_id: str, signal_type: str, url: str = "https://example.org/source") -> dict:
        return {
            "id": source_id,
            "name": source_id,
            "url": url,
            "domain": ["sustainability", "territory"],
            "environmental_signal_type": signal_type,
            "record_mode": "signal_only",
        }

    def observation(self, source_id: str, signal_type: str, items: list[dict], observed_at: str = "2026-08-27T20:00:00Z") -> dict:
        return {
            "observation_id": f"{source_id}:success:200",
            "source_id": source_id,
            "source_url": f"https://example.org/{source_id}",
            "observed_at": observed_at,
            "source_profile": "api",
            "fetch": {"status": "success", "method": "rest_api", "http_status": 200, "content_type": "application/json"},
            "content": {"media_type": "application/json", "content_hash": f"sha256:{source_id}", "byte_size": 10},
            "claims": [
                {"path": "environmental.signal_type", "value": signal_type},
                {"path": "environmental.entity_key", "value": "key"},
                {"path": "environmental.entity_items", "value": items},
                {"path": "environmental.metrics", "value": {"entity_count": len(items)}},
            ],
            "evidence_ids": [f"evidence:{source_id}"],
            "limitations": [],
            "collector": {"name": source_id, "version": "test"},
        }

    def test_entity_diff_finds_added_removed_changed_and_unchanged(self):
        previous = [{"key": "a", "value": 1}, {"key": "b", "value": 1}, {"key": "c", "value": 1}]
        current = [{"key": "a", "value": 2}, {"key": "b", "value": 1}, {"key": "d", "value": 1}]
        _, buckets = MODULE.entity_diff(previous, current)
        self.assertEqual({item["key"] for item in buckets["ADDED"]}, {"d"})
        self.assertEqual({item["key"] for item in buckets["REMOVED"]}, {"c"})
        self.assertEqual({item["key"] for item in buckets["CHANGED"]}, {"a"})
        self.assertEqual({item["key"] for item in buckets["UNCHANGED"]}, {"b"})

    def test_inpe_parser_reads_comma_csv_and_stable_ids(self):
        source = self.source("inpe-queimadas", "FIRE_ACTIVITY", "https://example.org/inpe/")
        directory = self.response(source["url"], '<a href="focos_diario_br_20260827.csv">focos</a>', "text/html")
        csv_body = "id,lat,lon,data_hora_gmt,satelite,municipio,estado,pais,municipio_id,estado_id,pais_id,numero_dias_sem_chuva,precipitacao,risco_fogo,bioma,frp\n"
        csv_body += "fire-1,-15.8,-47.9,2026-08-27 19:00:00,NPP,Teste,DF,Brasil,5300108,53,BR,5,0.0,0.8,Cerrado,12.5\n"
        csv_body += "fire-2,-15.8,-47.9,2026-08-27 20:00:00,NPP,Teste,DF,Brasil,5300108,53,BR,5,0.0,0.8,Cerrado,8.0\n"
        csv_response = self.response(source["url"] + "focos_diario_br_20260827.csv", csv_body, "text/csv")
        with patch.object(MODULE, "_request", side_effect=[directory, csv_response]):
            observation = MODULE.parse_inpe(source, "2026-08-27T20:00:00Z")
        claims = MODULE.claim_map(observation)
        items = claims["environmental.entity_items"]
        self.assertEqual(observation["fetch"]["status"], "success")
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["key"], "fire-1")
        self.assertEqual(items[0]["municipality_id"], "5300108")
        self.assertEqual(items[0]["occurred_at"], "2026-08-27T19:00:00Z")
        self.assertEqual(claims["environmental.metrics"]["entity_count"], 2)

    def test_composition_produces_three_provenance_preserving_demos(self):
        ibge_items = [{"key": "5300108", "entity_type": "municipality", "municipality_id": "5300108", "municipality": "Brasília", "state": "DF", "state_name": "Distrito Federal", "region": "CO", "region_name": "Centro-Oeste"}]
        fire_items = [{"key": "fire-1", "entity_type": "fire_hotspot", "municipality_id": "5300108", "municipality": "Brasília", "state": "DF", "biome": "Cerrado", "occurred_at": "2026-08-27T19:00:00Z", "location": {"latitude": -15.8, "longitude": -47.9}, "frp": 12.5}]
        biodiversity_items = [{"key": "gbif-1", "entity_type": "biodiversity_occurrence", "municipality": "Brasília", "state": "DF", "scientific_name": "Species test", "license": "CC-BY", "occurred_at": "2026-08-27T18:00:00Z", "location": {"latitude": -15.8, "longitude": -47.9}}]
        climate_items = [{"key": "-15.8|-47.9|2026-08-27T19:00:00", "entity_type": "climate_point", "occurred_at": "2026-08-27T19:00:00Z", "location": {"latitude": -15.8, "longitude": -47.9}, "values": {"temperature_2m": 28.0}, "units": {"temperature_2m": "°C"}, "forecast": True}]
        observations = [
            self.observation("ibge-localidades-api", "TERRITORIAL_CONTEXT", ibge_items),
            self.observation("inpe-queimadas", "FIRE_ACTIVITY", fire_items),
            self.observation("gbif-occurrences", "BIODIVERSITY_OCCURRENCE", biodiversity_items),
            self.observation("open-meteo", "CLIMATE_CONDITION", climate_items),
        ]
        registry = [
            self.source("ibge-localidades-api", "TERRITORIAL_CONTEXT"),
            self.source("inpe-queimadas", "FIRE_ACTIVITY"),
            self.source("gbif-occurrences", "BIODIVERSITY_OCCURRENCE"),
            self.source("open-meteo", "CLIMATE_CONDITION"),
        ]
        signals, changes, demos, stats = MODULE.build_environmental_signal_views(observations, [], registry, {item["source_id"]: item["evidence_ids"] for item in observations}, "2026-08-27T20:00:00Z")
        self.assertEqual(len(demos), 3)
        self.assertEqual(stats["composition_status"], "PROVEN")
        self.assertTrue(any(item["signal_type"] == "COMPOSITE_ENVIRONMENTAL" for item in signals))
        self.assertTrue(all(item["observation_ids"] for item in demos))
        self.assertTrue(all(item["evidence_ids"] for item in demos))
        self.assertTrue(changes)

    def test_source_failure_never_infers_entity_removal(self):
        failed = {
            "observation_id": "nasa-eonet:failed:503",
            "source_id": "nasa-eonet",
            "source_url": "https://example.org/eonet",
            "observed_at": "2026-08-27T20:00:00Z",
            "source_profile": "api",
            "fetch": {"status": "failed", "method": "rest_api", "http_status": 503, "content_type": None},
            "content": {"media_type": "application/octet-stream", "content_hash": None, "byte_size": 0},
            "claims": [],
            "evidence_ids": ["evidence:nasa"],
            "limitations": ["HTTP failure"],
        }
        registry = [self.source("nasa-eonet", "NATURAL_EVENT", "https://example.org/eonet")]
        signals, _, _, stats = MODULE.build_environmental_signal_views([failed], [], registry, {"nasa-eonet": ["evidence:nasa"]}, "2026-08-27T20:00:00Z")
        self.assertEqual(signals[0]["change_type"], "SOURCE_UNAVAILABLE")
        self.assertEqual(signals[0]["entity_diff"]["mode"], "SOURCE_LEVEL_CHANGE_ONLY")
        self.assertEqual(stats["source_level_change_only"], 1)
        self.assertEqual(stats["entity_removed"], 0)


if __name__ == "__main__":
    unittest.main()
