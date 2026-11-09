import csv
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from assistente import Assistente
from base_conhecimento import BaseConhecimento, normalizar
from orientacao import Orientacao

RAIZ = Path(__file__).resolve().parents[1]


class TesteConsultas(unittest.TestCase):
    def setUp(self):
        self.base = BaseConhecimento(RAIZ / "data" / "base_conhecimento.json")
        self.assertTrue(self.base.carregar())
        self.assistente = Assistente("Teste", self.base)

    def test_base_nacional_completa(self):
        self.assertEqual(len(self.base.orientacoes), 10)
        self.assertEqual(len(self.base.categorias()), 5)
        for categoria in self.base.categorias():
            self.assertEqual(len(self.assistente.navegar(categoria)), 2)

    def test_acentos_pontuacao_e_maiusculas(self):
        self.assertEqual(normalizar("  VACINAÇÃO, saúde?! "), " vacinacao saude ")
        ids1 = [item.id for _, item in self.assistente.perguntar("VACINAÇÃO?!")]
        ids2 = [item.id for _, item in self.assistente.perguntar("vacinacao")]
        self.assertEqual(ids1, ids2)
        self.assertEqual(ids1[0], 4)

    def test_historico_das_minhas_doses_encontra_vacinas(self):
        resultados = self.assistente.perguntar("Como vejo o histórico das minhas doses?")
        pontos, orientacao = resultados[0]
        self.assertEqual((pontos, orientacao.id), (3, 4))
        self.assertEqual(self.assistente.confianca(pontos), "MÉDIA")

    def test_pontuacao_do_exemplo_do_enunciado(self):
        dados = vars(self.base.orientacoes[0]).copy()
        dados.update(titulo="Fazer o Cartão Nacional de Saúde (Cartão SUS)",
                     palavras_chave=["cartao sus", "cartao do sus", "sus", "cns"])
        item = Orientacao(dados)
        self.assertEqual(self.base.pontuar("Como faço o cartão do SUS?", item), 7)

    def test_bloqueia_dados_antes_de_buscar(self):
        def busca_proibida(pergunta):
            self.fail("Dados pessoais não podem chegar à busca.")
        self.base.buscar = busca_proibida
        for pergunta in ["meu cpf 123.456.789-00", "1 2 3 4 5 6 7 8", "alguem@exemplo.com"]:
            with self.subTest(pergunta=pergunta), self.assertRaises(ValueError):
                self.assistente.perguntar(pergunta)
        self.assertEqual(self.assistente.historico, [])

    def test_entrada_invalida(self):
        for pergunta in ["", "   ", "?!...", "a" * 1001]:
            with self.subTest(pergunta=pergunta), self.assertRaises(ValueError):
                self.assistente.perguntar(pergunta)

    def test_nao_encontrado(self):
        self.assertEqual(self.assistente.perguntar("Como matricular meu cachorro?"), [])

    def test_limites_de_confianca(self):
        for pontos, resultado in [(2, "NÃO ENCONTRADA"), (3, "MÉDIA"), (5, "MÉDIA"), (6, "ALTA")]:
            self.assertEqual(self.assistente.confianca(pontos), resultado)

    def test_palavra_nao_casa_com_parte_de_outra(self):
        item = self.base.orientacoes[9]
        self.assertEqual(self.base.pontuar("bpcabc", item), 0)

    def test_resultados_ordenados_e_ate_tres(self):
        resultados = self.assistente.perguntar("cpf vacinas aposentadoria bpc extrato")
        self.assertEqual(len(resultados), 3)
        self.assertTrue(all(isinstance(item, tuple) for item in resultados))
        pontos = [p for p, _ in resultados]
        self.assertEqual(pontos, sorted(pontos, reverse=True))
        todos = self.base.buscar("palavra desconhecida")
        self.assertEqual([item.id for _, item in todos], list(range(1, 11)))

    def test_resposta_mostra_fonte_data_aviso(self):
        for item in self.base.orientacoes:
            texto = item.exibir()
            self.assertIn(item.fonte, texto)
            self.assertIn(item.verificado_em, texto)
            self.assertIn("este assistente não é canal oficial", texto)

    def test_erros_do_json_e_recuperacao(self):
        dados = json.loads((RAIZ / "data/base_conhecimento.json").read_text(encoding="utf-8"))
        sem_campo = [dict(dados[0])]
        del sem_campo[0]["resposta"]
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "base.json"
            base = BaseConhecimento(caminho)
            self.assertFalse(base.carregar())
            for texto in ["{invalido", "{}", "[]", json.dumps(sem_campo), json.dumps([dados[0], dados[0]])]:
                caminho.write_text(texto, encoding="utf-8")
                self.assertFalse(base.carregar())
                self.assertEqual(base.orientacoes, [])
                self.assertTrue(base.erro)
            caminho.write_text(json.dumps(dados), encoding="utf-8")
            self.assertTrue(base.carregar())
            self.assertEqual(base.erro, "")

    def test_terminal_funciona_fora_da_pasta_do_projeto(self):
        with tempfile.TemporaryDirectory() as pasta:
            projeto = Path(pasta) / "projeto"
            shutil.copytree(RAIZ, projeto, ignore=shutil.ignore_patterns(
                "__pycache__", "historico.json", "avaliacoes.json", "atendimentos.csv", "*.tmp"
            ))
            processo = subprocess.run(
                [sys.executable, str(projeto / "main.py"), "--terminal"],
                input=("x\n1\n\n123.456.789-00\nComo matricular meu cachorro?\n"
                       "Como consultar minhas vacinas?\ntalvez\ns\n0\n2\n1\n1\nn\n0\n0\n"
                       "1\nComo matricular meu cachorro?\n0\n4\n5\n0\n9\n4\n"),
                text=True, capture_output=True, cwd=pasta, timeout=10)
            historico = (projeto / "data/historico.json").read_text(encoding="utf-8")
            notas = json.loads((projeto / "data/avaliacoes.json").read_text(encoding="utf-8"))
            with (projeto / "data/atendimentos.csv").open(encoding="utf-8-sig", newline="") as arquivo:
                exportados = list(csv.DictReader(arquivo))
        self.assertEqual(processo.returncode, 0, processo.stderr)
        self.assertIn("Digite um número", processo.stdout)
        self.assertIn("Não informe CPF", processo.stdout)
        self.assertIn("Consultar vacinas", processo.stdout)
        self.assertIn("Digite s para sim, n para não ou 0 para pular.", processo.stdout)
        self.assertIn("Solicitar aposentadoria", processo.stdout)
        self.assertNotIn("123.456.789-00", processo.stdout)
        self.assertNotIn("123.456.789-00", historico)
        self.assertIn("Resposta encontrada: 66.7%", processo.stdout)
        self.assertIn("Taxa de acerto (ajudou): 33.3%", processo.stdout)
        self.assertIn("CSV exportado", processo.stdout)
        self.assertEqual(notas, [4])
        self.assertEqual(len(exportados), 3)
        self.assertEqual(exportados[0]["pergunta"], "Como consultar minhas vacinas?")
        self.assertEqual(exportados[-1]["tempo_encontro_segundos"], "")
        busca, categoria, sem_resposta = json.loads(historico)
        self.assertEqual((busca["origem"], busca["id_orientacao"], busca["tentativas"]), ("pergunta", 4, 2))
        self.assertTrue(busca["ajudou"])
        self.assertGreaterEqual(busca["tempo_segundos"], 0)
        self.assertEqual(categoria["origem"], "categoria")
        self.assertFalse(categoria["ajudou"])
        self.assertFalse(sem_resposta["encontrou"])
        self.assertIsNone(sem_resposta["id_orientacao"])

    def test_indicadores_aceitam_historico_anterior_e_avaliacao_pulada(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "historico.json"
            caminho.write_text(json.dumps([
                {"pergunta": "Como achar meu CPF?", "encontrou": True, "ajudou": None,
                 "tentativas": 1, "tempo_segundos": 20.0},
                {"pergunta": "Como consultar minhas vacinas?", "encontrou": True, "ajudou": True,
                 "tentativas": 3, "tempo_segundos": 60.0, "tempo_encontro_segundos": 7.0},
            ]), encoding="utf-8")
            assistente = Assistente("Teste", self.base, caminho)
            assistente.registrar_facilidade(3)
            assistente.registrar_facilidade(4)
            dados = Assistente("Teste", self.base, caminho).indicadores()
            self.assertEqual(dados["encontrada_pct"], 100)
            self.assertEqual((dados["avaliados"], dados["ajudou_pct"]), (1, 100))
            self.assertEqual((dados["tempos_medidos"], dados["tempo_medio"]), (1, 7))
            self.assertEqual(dados["tentativas_media"], 2)
            self.assertEqual(dados["facilidade_media"], 3.5)
            self.assertEqual(dados["sem_solucao"], [])

    def test_preserva_historico_corrompido_e_permite_repetir_gravacao(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "historico.json"
            caminho.write_text("{incompleto", encoding="utf-8")
            assistente = Assistente("Teste", self.base, caminho)
            assistente.perguntar("Como consultar minhas vacinas?")
            with self.assertRaises(OSError):
                assistente.registrar(True)
            self.assertEqual(caminho.read_text(encoding="utf-8"), "{incompleto")
            caminho.write_text("[]", encoding="utf-8")
            self.assertTrue(assistente.registrar())
            self.assertFalse(assistente.registrar())
            reaberto = Assistente("Teste", self.base, caminho)
            self.assertEqual(len(reaberto.historico), 1)
            self.assertTrue(reaberto.historico[0]["ajudou"])


if __name__ == "__main__":
    unittest.main()
