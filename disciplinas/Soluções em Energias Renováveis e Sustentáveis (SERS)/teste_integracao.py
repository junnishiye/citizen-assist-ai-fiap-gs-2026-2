"""
Testes da integracao com um cliente OpenAI FALSO (sem rede, sem chave).
Provam o formato das ferramentas e o laco de chamadas; NAO provam o
comportamento do modelo real, que precisa ser testado com a API de verdade.

Rodar: python3 -m unittest discover -p "teste_*.py" -v
"""
import json
import re
import unittest
from types import SimpleNamespace as NS

import integracao_openai as io


def chamada(id_, nome, argumentos):
    return NS(id=id_, function=NS(name=nome, arguments=json.dumps(argumentos)))


class ClienteFalso:
    def __init__(self, mensagens):
        self.mensagens = list(mensagens)
        self.chamadas = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kw):
        self.chamadas.append(dict(kw, messages=list(kw["messages"])))
        return NS(choices=[NS(message=self.mensagens.pop(0))])


def texto(conteudo):
    return NS(content=conteudo, tool_calls=None)


def com_chamadas(*chamadas):
    return NS(content=None, tool_calls=list(chamadas))


class TestFormato(unittest.TestCase):
    def test_tres_ferramentas_no_formato_openai(self):
        ferr = io.ferramentas_openai()
        self.assertEqual(len(ferr), 3)
        for f in ferr:
            self.assertEqual(f["type"], "function")
            self.assertEqual(f["function"]["parameters"]["type"], "object")
            self.assertTrue(f["function"]["name"])

    def test_prompt_sem_numeros(self):
        self.assertIsNone(re.search(r"\d", io.PROMPT_SISTEMA))


class TestLaco(unittest.TestCase):
    ARGS_BENEFICIO = dict(
        consumo_total_kwh_mes=95, tipo_ligacao="monofasico", beneficio="tarifa_social",
        cadunico_atualizado=False, municipio_igual_conta=True, titular_da_conta=True,
    )

    def test_resposta_direta(self):
        cli = ClienteFalso([texto("Oi!")])
        t, hist = io.responder(cli, [{"role": "user", "content": "oi"}], modelo="m")
        self.assertEqual(t, "Oi!")
        self.assertEqual(hist[-1], {"role": "assistant", "content": "Oi!"})
        self.assertEqual(cli.chamadas[0]["messages"][0]["role"], "system")

    def test_chamada_de_ferramenta_e_volta_ao_modelo(self):
        cli = ClienteFalso([
            com_chamadas(chamada("c1", "verificar_beneficio_energia", self.ARGS_BENEFICIO)),
            texto("Seu cadastro esta desatualizado."),
        ])
        t, _ = io.responder(cli, [{"role": "user", "content": "meu desconto esta em risco?"}], modelo="m")
        self.assertEqual(t, "Seu cadastro esta desatualizado.")
        segunda = cli.chamadas[1]["messages"]
        self.assertEqual(segunda[-2]["role"], "assistant")
        self.assertEqual(segunda[-2]["tool_calls"][0]["id"], "c1")
        self.assertEqual(segunda[-1]["role"], "tool")
        self.assertEqual(segunda[-1]["tool_call_id"], "c1")
        saida = json.loads(segunda[-1]["content"])
        self.assertEqual(saida["pendencias"][0]["regra"], "cadunico_atualizado")
        self.assertGreater(saida["valor_em_risco_rs_mes"], 0)
        self.assertTrue(saida["avisos"])   # aviso de parametro provisorio (PIS/Cofins)

    def test_erro_volta_ao_modelo_sem_quebrar(self):
        cli = ClienteFalso([
            com_chamadas(chamada("c1", "impacto_bandeira_energia", {"consumo_total_kwh_mes": 100})),
            texto("Qual e o tipo de ligacao?"),
        ])
        t, _ = io.responder(cli, [{"role": "user", "content": "x"}], modelo="m")
        self.assertEqual(t, "Qual e o tipo de ligacao?")
        saida = json.loads(cli.chamadas[1]["messages"][-1]["content"])
        self.assertIn("erro", saida)

    def test_argumentos_invalidos_viram_erro(self):
        c = NS(id="c9", function=NS(name="impacto_bandeira_energia", arguments="{nao e json"))
        msgs = io.executar_chamadas([c])
        self.assertIn("erro", json.loads(msgs[0]["content"]))

    def test_limite_de_voltas(self):
        args = dict(consumo_total_kwh_mes=100, tipo_ligacao="monofasico")
        cli = ClienteFalso([com_chamadas(chamada("c%d" % i, "impacto_bandeira_energia", args)) for i in range(10)])
        t, _ = io.responder(cli, [{"role": "user", "content": "x"}], modelo="m", max_voltas=3)
        self.assertIn("Nao consegui", t)
        self.assertEqual(len(cli.chamadas), 3)

    def test_sem_modelo_levanta_erro(self):
        import os
        os.environ.pop("OPENAI_MODEL", None)
        with self.assertRaises(ValueError):
            io.responder(ClienteFalso([]), [])


if __name__ == "__main__":
    unittest.main()
