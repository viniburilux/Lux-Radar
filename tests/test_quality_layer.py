import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "quality_layer.py"
SPEC = importlib.util.spec_from_file_location("quality_layer", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class QualityLayerTests(unittest.TestCase):
    def test_deadline_requires_context(self):
        self.assertEqual(MODULE.extract_deadline("Publicado em 10/06/2024 e atualizado em 12/06/2024"), None)
        self.assertEqual(MODULE.extract_deadline("Inscrições até 30/09/2026"), "2026-09-30T23:59:59Z")
        self.assertEqual(MODULE.extract_deadline("deadline: 2026-10-05"), "2026-10-05T23:59:59Z")

    def test_quality_requires_eligibility(self):
        status, _ = MODULE.quality_state("call aberta", deadline="2026-10-05T23:59:59Z", eligibility=[], organization="Foundation", pdf_url=None)
        self.assertEqual(status, "INSUFFICIENT_EVIDENCE")
        status, _ = MODULE.quality_state("call aberta", deadline="2026-10-05T23:59:59Z", eligibility=["Organizações sem fins lucrativos"], organization="Foundation", pdf_url=None)
        self.assertEqual(status, "VERIFIED")

    def test_final_result_signal_blocks_future_irrelevant_date(self):
        status, _ = MODULE.quality_state("resultado final publicado; inscrições encerradas", deadline="2026-12-31T23:59:59Z", eligibility=["Organizações elegíveis"], organization="Foundation", pdf_url=None)
        self.assertEqual(status, "CLOSED")

    def test_curator_internal_detail_without_primary_evidence_is_not_verified(self):
        source = {"source_role": "curator", "url": "https://capitaai.com.br/editais-abertos/meio-ambiente"}
        state, _ = MODULE.enforce_source_quality(source, "https://capitaai.com.br/captacao/example", "VERIFIED", "ok", None)
        self.assertEqual(state, "INSUFFICIENT_EVIDENCE")

    def test_amount_parses_brl(self):
        self.assertEqual(MODULE.extract_amount("Apoio de R$ 1.250.000,00"), {"amount": 1250000.0, "currency": "BRL", "raw": "R$ 1.250.000,00"})


if __name__ == "__main__":
    unittest.main()
