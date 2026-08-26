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

    def test_deadline_parses_portuguese_month_name(self):
        self.assertEqual(MODULE.extract_deadline("As inscrições podem ser realizadas até 31 de agosto de 2026, às 18h"), "2026-08-31T23:59:59Z")

    def test_deadline_prefers_submission_window_over_registration_date(self):
        text = "Cadastro da instituição proponente até 19 de novembro de 2026. Período de submissão das propostas de cursos novos de 24 de agosto de 2026 até 18 de dezembro de 2026."
        self.assertEqual(MODULE.extract_deadline(text), "2026-12-18T23:59:59Z")

    def test_explicit_continuous_window_allows_open_with_identity(self):
        status, _ = MODULE.quality_state("Projetos podem ser apresentados a qualquer momento", deadline=None, eligibility=[], organization="Fundo", pdf_url=None, title="Chamada de projetos")
        self.assertEqual(status, "OPEN")

    def test_manifestacao_de_interesse_is_opportunity_identity(self):
        status, _ = MODULE.quality_state("Inscrições até 04/09/2026", deadline="2026-09-04T23:59:59Z", eligibility=[], organization="FUNBIO", pdf_url=None, title="Manifestação de Interesse 04/2026")
        self.assertEqual(status, "OPEN")

    def test_navigation_title_with_temporal_text_is_not_open(self):
        status, _ = MODULE.quality_state("Projetos podem ser apresentados a qualquer momento", deadline=None, eligibility=[], organization="Fundo", pdf_url=None, title="Como apresentar projetos")
        self.assertEqual(status, "INSUFFICIENT_EVIDENCE")

    def test_generic_media_kit_is_not_official_pdf(self):
        soup = MODULE.BeautifulSoup('<a href="/midia-kit.pdf">Midia Kit</a>', "html.parser")
        self.assertIsNone(MODULE.extract_pdf_url("https://example.org/page", soup))

    def test_future_deadline_allows_open_with_partial_enrichment(self):
        status, _ = MODULE.quality_state("call", deadline="2026-10-05T23:59:59Z", eligibility=[], organization="Foundation", pdf_url=None, title="Chamada de apoio")
        self.assertEqual(status, "OPEN")

    def test_explicit_open_status_allows_open_without_deadline(self):
        status, _ = MODULE.quality_state("status: aberto para inscrições", deadline=None, eligibility=[], organization="Foundation", pdf_url=None, title="Edital aberto para inscrições")
        self.assertEqual(status, "OPEN")

    def test_temporal_signal_without_opportunity_identity_is_not_open(self):
        status, _ = MODULE.quality_state("inscrições abertas", deadline="2026-10-05T23:59:59Z", eligibility=[], organization="Foundation", pdf_url=None, title="Resultados")
        self.assertEqual(status, "INSUFFICIENT_EVIDENCE")

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
