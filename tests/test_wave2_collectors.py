import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "wave2_collectors.py"
SPEC = importlib.util.spec_from_file_location("wave2_collectors", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class FakeResponse:
    def __init__(self, html, url):
        self.content = html.encode("utf-8")
        self.url = url
        self.headers = {"content-type": "text/html; charset=utf-8"}


class Wave2CollectorTests(unittest.TestCase):
    def source(self, source_id, name):
        return {"id": source_id, "name": name, "organization": name, "domain": ["sustainability"], "country": "BR"}

    def test_funbio_emits_detail_links_and_skips_actions(self):
        response = FakeResponse("""
        <h1>Portal de Chamadas FUNBIO</h1>
        <a href='/planos'>Chamada de Projetos 07/2026 Apoio a RPPNs no Paraná</a>
        <a href='/planos'>Saiba Mais</a>
        <a href='https://c3.cerebro.org.br/auth/perguntar'>Submeter Proposta</a>
        """, "https://chamadas.funbio.org.br/")
        items, _ = MODULE.parse_funbio(self.source("funbio-chamadas", "FUNBIO"), response)
        self.assertEqual(len(items), 1)
        self.assertIn("/planos", items[0]["url"])

    def test_bnb_uses_edital_title_text(self):
        response = FakeResponse("""
        <ul><li><a href='/detail/1'>Edital Fundeci 01/2026 Gestão de Resíduos Sólidos</a></li></ul>
        <a href='/detail/2'>Edital Fundo Sustentabilidade 01/2026 Caatinga</a>
        """, "https://bnb.gov.br/web/guest/fundeci/editais")
        items, _ = MODULE.parse_bnb(self.source("bnb-fundeci", "Banco do Nordeste"), response)
        self.assertEqual(len(items), 2)

    def test_embratur_only_emits_official_pdfs(self):
        response = FakeResponse("""
        <a href='https://embratur.com.br/wp-content/uploads/2026/08/Edital-07-2026.pdf'>EDITAL DE CHAMAMENTO PÚBLICO Nº 07/2026</a>
        <a href='/noticias'>Notícia sobre turismo</a>
        """, "https://embratur.my.site.com/expositor/s/editais")
        items, _ = MODULE.parse_embratur(self.source("embratur-editais", "Embratur"), response)
        self.assertEqual(len(items), 1)
        self.assertTrue(items[0]["url"].endswith(".pdf"))

    def test_capta_follows_external_official_edital_link(self):
        response = FakeResponse("""
        <article><h2>Edital de Seleção de Projetos Socioambientais 2026</h2>
        <a href='https://official.example.org/edital'>Edital</a></article>
        """, "https://capta.org.br/fontes-de-financiamento/oportunidades/")
        items, _ = MODULE.parse_capta(self.source("capta-editais", "Capta"), response)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["url"], "https://official.example.org/edital")


if __name__ == "__main__":
    unittest.main()
