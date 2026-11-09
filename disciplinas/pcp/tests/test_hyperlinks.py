import unittest

try:
    from interface import identificar_links
except ModuleNotFoundError as erro:
    if erro.name not in ("tkinter", "_tkinter"):
        raise
    raise unittest.SkipTest("Tkinter indisponível para testar os links da interface.") from None


class TesteHyperlinks(unittest.TestCase):
    def test_nome_sem_url_do_exemplo_reportado(self):
        texto = "1. Abra o Meu SUS Digital e entre com a conta gov.br."
        links = identificar_links(texto)
        self.assertIn((texto.index("Meu SUS Digital"), texto.index("Meu SUS Digital") + 15,
                       "https://meususdigital.saude.gov.br"), links)

    def test_url_completa_nao_recebe_link_interno_para_gov_br(self):
        texto = "Acesse https://meususdigital.saude.gov.br ou Meu SUS Digital."
        links = identificar_links(texto)
        self.assertEqual(len(links), 2)
        self.assertEqual([url for _, _, url in links], ["https://meususdigital.saude.gov.br"] * 2)
        self.assertLessEqual(links[0][1], links[1][0])

    def test_nome_quebrado_repetido_e_variacao_de_caixa(self):
        texto = "Meu SUS\nDigital e meu sus digital; depois Meu INSS."
        links = identificar_links(texto)
        self.assertEqual([url for _, _, url in links],
                         ["https://meususdigital.saude.gov.br"] * 2 + ["https://meu.inss.gov.br"])
        self.assertEqual(texto[links[0][0]:links[0][1]], "Meu SUS\nDigital")

    def test_menu_interno_e_nome_parcial_nao_viram_link(self):
        self.assertEqual(identificar_links("Minha Saúde > Vacinas. Meu SUS Digitalizado."), [])


if __name__ == "__main__":
    unittest.main()
