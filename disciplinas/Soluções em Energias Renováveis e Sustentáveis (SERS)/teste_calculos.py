"""
Testes da LOGICA de calculos.py com valores SINTETICOS.
Os numeros abaixo NAO sao dados de referencia: servem so para provar que a
aritmetica (franquia de 80 kWh, disponibilidade, Fio B) esta correta.

Rodar: python3 -m unittest teste_calculos -v
"""
import unittest

import calculos as c

P = {
    "tarifa_rs_kwh": 1.0,
    "tarifa_baixa_renda_rs_kwh": 1.0,
    "fio_b_rs_kwh": 0.1,
    "fio_b_pct_nao_compensado": 0.6,
    "franquia_tarifa_social_kwh": 80,
    "tarifa_desconto_social_rs_kwh": 0.5,
    "franquia_desconto_social_kwh": 120,
    "custo_disponibilidade_kwh_por_ligacao": {
        "monofasico": 30, "bifasico_2_condutores": 30,
        "bifasico_3_condutores": 50, "trifasico": 100,
    },
    "hsp_kwh_m2_dia": 5.0,
    "taxa_desempenho": 0.8,          # => 120 kWh por kWp por mes
    "custo_rs_por_kwp": 3000,
    "fator_emissao_media_kgco2_kwh": 0.05,
    "fator_emissao_margem_operacao_kgco2_kwh": 0.5,
}


def entrada(**kw):
    base = {"consumo_total_kwh_mes": 200, "tipo_ligacao": "monofasico", "tarifa_social": True}
    base.update(kw)
    return base


class TestFaturamento(unittest.TestCase):
    def test_dentro_da_franquia_nao_paga(self):
        self.assertEqual(c.kwh_pagos(60, 30, 80), 0)

    def test_acima_da_franquia(self):
        self.assertEqual(c.kwh_pagos(200, 30, 80), 120)

    def test_sem_tarifa_social(self):
        self.assertEqual(c.kwh_pagos(200, 30, 0), 200)

    def test_trifasico_paga_pelo_minimo(self):
        self.assertEqual(c.kwh_pagos(20, 100, 80), 20)

    def test_ligacao_invalida(self):
        with self.assertRaises(ValueError):
            c.alternativa_solar(entrada(tipo_ligacao="xyz"), P)

    def test_sem_beneficio_informado_assume_nenhum_por_seguranca(self):
        # Sem 'beneficio' e sem o booleano antigo 'tarifa_social': nao deve presumir
        # o cenario mais barato (16/11/2026). kwh_cobrados deve ser o consumo
        # faturado inteiro, sem os 80 kWh gratuitos.
        sem_nada = {"consumo_total_kwh_mes": 200, "tipo_ligacao": "monofasico"}
        self.assertEqual(c._beneficio(sem_nada), "nenhum")
        self.assertEqual(c.kwh_cobrados(200, sem_nada, P), 200)

    def test_booleano_antigo_tarifa_social_ainda_funciona(self):
        antigo = {"consumo_total_kwh_mes": 200, "tipo_ligacao": "monofasico", "tarifa_social": True}
        self.assertEqual(c._beneficio(antigo), "tarifa_social")


class TestEficiencia(unittest.TestCase):
    def test_abaixo_da_franquia_nao_economiza_reais(self):
        r = c.alternativa_eficiencia(
            entrada(consumo_total_kwh_mes=70, consumo_atual_kwh_mes=40,
                    consumo_novo_kwh_mes=20, investimento_rs=400), P)
        self.assertEqual(r["economia_rs_mes"], 0)
        self.assertIsNone(r["payback_meses"])
        self.assertAlmostEqual(r["co2_evitado_kg_mes"], 1.0)  # CO2 conta tudo

    def test_acima_da_franquia(self):
        r = c.alternativa_eficiencia(
            entrada(consumo_atual_kwh_mes=50, consumo_novo_kwh_mes=30,
                    investimento_rs=400), P)
        self.assertAlmostEqual(r["economia_rs_mes"], 20.0)
        self.assertAlmostEqual(r["payback_meses"], 20.0)

    def test_cruza_a_franquia(self):
        # 90 kWh -> 60 kWh: so os 10 kWh acima de 80 reduzem a conta
        r = c.alternativa_eficiencia(
            entrada(consumo_total_kwh_mes=90, consumo_atual_kwh_mes=40,
                    consumo_novo_kwh_mes=10, investimento_rs=100), P)
        self.assertAlmostEqual(r["economia_rs_mes"], 10.0)


class TestSolar(unittest.TestCase):
    def test_dimensiona_pelos_kwh_pagos(self):
        self.assertAlmostEqual(c.dimensionar_kwp(entrada(), P), 1.0)  # 120/120

    def test_solar_com_tarifa_social_e_fio_b(self):
        r = c.alternativa_solar(entrada(), P)
        self.assertAlmostEqual(r["energia_compensada_kwh_mes"], 120.0)
        self.assertAlmostEqual(r["economia_energia_rs_mes"], 120.0)
        self.assertAlmostEqual(r["custo_fio_b_rs_mes"], 7.2)
        self.assertAlmostEqual(r["economia_rs_mes"], 112.8)
        self.assertAlmostEqual(r["investimento_rs"], 3000.0)
        self.assertAlmostEqual(r["co2_evitado_kg_mes"], 6.0)
        self.assertAlmostEqual(r["co2_limite_superior_kg_mes"], 60.0)

    def test_sem_tarifa_social_respeita_disponibilidade(self):
        r = c.alternativa_solar(entrada(tarifa_social=False), P)
        # consumo 200, disp 30: so 170 kWh podem ser compensados
        self.assertAlmostEqual(r["energia_compensada_kwh_mes"], 170.0)
        self.assertAlmostEqual(r["economia_energia_rs_mes"], 170.0)
        self.assertAlmostEqual(r["economia_rs_mes"], 170.0 - 170 * 0.06)

    def test_consumo_dentro_da_franquia_nao_justifica_solar(self):
        r = c.alternativa_solar(entrada(consumo_total_kwh_mes=70), P)
        self.assertEqual(r["economia_rs_mes"], 0)
        self.assertEqual(r["investimento_rs"], 0)
        self.assertIsNone(r["payback_meses"])

    def test_fio_b_pode_anular_a_economia(self):
        p = dict(P, fio_b_rs_kwh=2.0)  # Fio B maior que a tarifa (absurdo, so p/ teste)
        r = c.alternativa_solar(entrada(), p)
        self.assertLess(r["economia_rs_mes"], 0)
        self.assertIsNone(r["payback_meses"])


class TestSubclasse(unittest.TestCase):
    P_S = dict(P, tarifa_baixa_renda_rs_kwh=0.5)

    def test_tarifa_social_usa_tarifa_baixa_renda(self):
        r = c.alternativa_solar(entrada(), self.P_S)
        self.assertAlmostEqual(r["economia_energia_rs_mes"], 120 * 0.5)

    def test_sem_tarifa_social_usa_tarifa_residencial(self):
        r = c.alternativa_solar(entrada(tarifa_social=False), self.P_S)
        self.assertAlmostEqual(r["economia_energia_rs_mes"], 170 * 1.0)

    def test_eficiencia_tarifa_social(self):
        r = c.alternativa_eficiencia(
            entrada(consumo_atual_kwh_mes=50, consumo_novo_kwh_mes=30, investimento_rs=400), self.P_S)
        self.assertAlmostEqual(r["economia_rs_mes"], 20 * 0.5)


class TestDescontoSocial(unittest.TestCase):
    """Desconto Social: ate 120 kWh a 0,5; acima, tarifa Residencial (1,0)."""

    def test_custo_por_faixa(self):
        e = entrada(beneficio="desconto_social")
        self.assertAlmostEqual(c.custo_energia_rs(100, e, P), 100 * 0.5)
        self.assertAlmostEqual(c.custo_energia_rs(150, e, P), 120 * 0.5 + 30 * 1.0)

    def test_disponibilidade_minima(self):
        e = entrada(beneficio="desconto_social", tipo_ligacao="trifasico")
        self.assertAlmostEqual(c.custo_energia_rs(20, e, P), 100 * 0.5)

    def test_eficiencia_dentro_da_faixa_reduzida(self):
        r = c.alternativa_eficiencia(
            entrada(beneficio="desconto_social", consumo_total_kwh_mes=100,
                    consumo_atual_kwh_mes=50, consumo_novo_kwh_mes=30,
                    investimento_rs=100), P)
        self.assertAlmostEqual(r["economia_rs_mes"], 20 * 0.5)

    def test_eficiencia_cruzando_o_limite(self):
        # 140 -> 110 kWh: 20 kWh a 1,0 (acima de 120) e 10 kWh a 0,5
        r = c.alternativa_eficiencia(
            entrada(beneficio="desconto_social", consumo_total_kwh_mes=140,
                    consumo_atual_kwh_mes=40, consumo_novo_kwh_mes=10,
                    investimento_rs=100), P)
        self.assertAlmostEqual(r["economia_rs_mes"], 20 * 1.0 + 10 * 0.5)

    def test_solar_compensa_primeiro_a_faixa_cara(self):
        # 150 kWh, disponibilidade 30: compensa 120 kWh (1,0 kWp), restam 30 kWh.
        # custo antes = 120*0,5 + 30*1,0 = 90; depois = 30*0,5 = 15; economia = 75
        p = dict(P, fio_b_rs_kwh=0.0)
        r = c.alternativa_solar(entrada(beneficio="desconto_social", consumo_total_kwh_mes=150), p)
        self.assertAlmostEqual(r["potencia_kwp"], 1.0)
        self.assertAlmostEqual(r["economia_energia_rs_mes"], 75.0)

    def test_dimensionamento_nao_passa_da_disponibilidade_sem_franquia(self):
        # sem Tarifa Social: 200 kWh, disponibilidade 30 -> alvo 170 kWh, nao 200
        self.assertAlmostEqual(c.dimensionar_kwp(entrada(tarifa_social=False), P), 170 / 120)

    def test_beneficio_invalido(self):
        with self.assertRaises(ValueError):
            c.custo_energia_rs(100, entrada(beneficio="outro"), P)

    def test_booleano_antigo_continua_valendo(self):
        self.assertAlmostEqual(
            c.custo_energia_rs(200, entrada(tarifa_social=False), P), 200 * 1.0)
        self.assertAlmostEqual(
            c.custo_energia_rs(200, entrada(), P), 120 * P["tarifa_baixa_renda_rs_kwh"])


REGRAS = [
    {"id": "cadunico_atualizado", "texto": "t1", "acao": "a1"},
    {"id": "municipio_igual_conta", "texto": "t2", "acao": "a2"},
    {"id": "titular_da_conta", "texto": "t3", "acao": "a3"},
]
P_G = dict(
    P,
    regras_manter_beneficio=REGRAS,
    bandeira_vigente="verde",
    bandeiras_adicional_rs_kwh={"verde": 0.0, "amarela": 0.02, "vermelha_p1": 0.05, "vermelha_p2": 0.08},
)


class TestGuardiaoBeneficio(unittest.TestCase):
    def test_valor_dentro_da_franquia(self):
        # 60 kWh na Tarifa Social: conta de energia zero; sem o beneficio, 60 x 1,0
        r = c.valor_beneficio_mensal(entrada(consumo_total_kwh_mes=60), P_G)
        self.assertAlmostEqual(r["valor_rs_mes"], 60.0)

    def test_valor_acima_da_franquia(self):
        # 200 kWh: sem beneficio 200; com beneficio 120 -> vale 80 (os 80 kWh gratuitos)
        r = c.valor_beneficio_mensal(entrada(), P_G)
        self.assertAlmostEqual(r["valor_rs_mes"], 80.0)

    def test_valor_usa_tarifa_baixa_renda(self):
        p = dict(P_G, tarifa_baixa_renda_rs_kwh=0.5)
        r = c.valor_beneficio_mensal(entrada(), p)   # 200*1,0 - 120*0,5
        self.assertAlmostEqual(r["valor_rs_mes"], 140.0)

    def test_sem_beneficio_vale_zero(self):
        r = c.valor_beneficio_mensal(entrada(beneficio="nenhum"), P_G)
        self.assertEqual(r["valor_rs_mes"], 0.0)

    def test_valor_desconto_social(self):
        r = c.valor_beneficio_mensal(entrada(beneficio="desconto_social", consumo_total_kwh_mes=100), P_G)
        self.assertAlmostEqual(r["valor_rs_mes"], 100 * 1.0 - 100 * 0.5)

    def test_tudo_certo(self):
        resp = {r["id"]: True for r in REGRAS}
        r = c.avaliar_manutencao_beneficio(resp, entrada(), P_G)
        self.assertTrue(r["todas_ok"])
        self.assertEqual(r["pendencias"], [])
        self.assertAlmostEqual(r["valor_em_risco_rs_mes"], 80.0)

    def test_regra_nao_cumprida_e_nao_informada(self):
        resp = {"cadunico_atualizado": False, "municipio_igual_conta": True}
        r = c.avaliar_manutencao_beneficio(resp, entrada(), P_G)
        situacoes = {x["regra"]: x["situacao"] for x in r["pendencias"]}
        self.assertEqual(situacoes, {"cadunico_atualizado": "em_risco", "titular_da_conta": "nao_informado"})
        self.assertFalse(r["todas_ok"])


class TestImpactoBandeira(unittest.TestCase):
    def test_so_os_kwh_cobrados_pagam_adicional(self):
        # Tarifa Social, 200 kWh: 120 kWh cobrados
        r = c.impacto_bandeira(entrada(), P_G)
        self.assertAlmostEqual(r["impacto_rs_mes_por_bandeira"]["verde"], 0.0)
        self.assertAlmostEqual(r["impacto_rs_mes_por_bandeira"]["amarela"], 120 * 0.02)
        self.assertAlmostEqual(r["impacto_rs_mes_por_bandeira"]["vermelha_p2"], 120 * 0.08)

    def test_sem_beneficio_paga_tudo(self):
        r = c.impacto_bandeira(entrada(beneficio="nenhum", bandeira="vermelha_p1"), P_G)
        self.assertEqual(r["bandeira_vigente"], "vermelha_p1")
        self.assertAlmostEqual(r["adicional_vigente_rs_mes"], 200 * 0.05)

    def test_usa_bandeira_vigente_por_padrao(self):
        r = c.impacto_bandeira(entrada(), dict(P_G, bandeira_vigente="amarela"))
        self.assertAlmostEqual(r["adicional_vigente_rs_mes"], 120 * 0.02)


class TestAvisos(unittest.TestCase):
    def _json_temp(self, valores):
        import json as _json, tempfile, os as _os
        fd, caminho = tempfile.mkstemp(suffix=".json")
        with _os.fdopen(fd, "w", encoding="utf-8") as f:
            _json.dump({"valores": valores}, f)
        self.addCleanup(_os.remove, caminho)
        return caminho

    def test_tributos_provisorio_vira_aviso_claro(self):
        caminho = self._json_temp({"pis_cofins_aliquota": {"valor": 0.053, "provisorio": True}})
        avisos = c.avisos_provisorios(caminho)
        self.assertEqual(len(avisos), 1)
        self.assertIn("PIS/Cofins", avisos[0])

    def test_sem_provisorio_sem_aviso(self):
        caminho = self._json_temp({"pis_cofins_aliquota": {"valor": 0.053}})
        self.assertEqual(c.avisos_provisorios(caminho), [])

    def test_outros_provisorios(self):
        caminho = self._json_temp({"x": {"valor": 1, "provisorio": True}})
        self.assertIn("x", c.avisos_provisorios(caminho)[0])

    def test_ferramentas_devolvem_chave_avisos(self):
        r = c.executar_ferramenta("impacto_bandeira_energia", entrada(), P_G)
        self.assertEqual(r["avisos"], [])


class TestFerramentas(unittest.TestCase):
    def test_ids_das_regras_batem_com_o_schema(self):
        regras = c._ler_json(c.CAMINHO_PARAMETROS)["valores"]["regras_manter_beneficio"]["valor"]
        ids = {r["id"] for r in regras}
        self.assertTrue(ids <= set(c.TOOL_BENEFICIO["input_schema"]["properties"]))

    def test_despacho(self):
        r = c.executar_ferramenta(
            "verificar_beneficio_energia",
            dict(entrada(beneficio="tarifa_social"), cadunico_atualizado=True,
                 municipio_igual_conta=False, titular_da_conta=True), P_G)
        self.assertEqual([x["regra"] for x in r["pendencias"]], ["municipio_igual_conta"])
        r = c.executar_ferramenta("impacto_bandeira_energia", entrada(), P_G)
        self.assertIn("amarela", r["impacto_rs_mes_por_bandeira"])

    def test_ferramenta_desconhecida(self):
        with self.assertRaises(ValueError):
            c.executar_ferramenta("xyz", {}, P_G)

    def test_rejeita_numeros_invalidos(self):
        # 16/11/2026: consumo negativo nao deve produzir um resultado silencioso e
        # sem sentido (o piso de disponibilidade mascarava isso antes da validacao).
        base = entrada()
        for valor in (-3, float("nan"), float("inf"), True, "95"):
            with self.assertRaises(ValueError):
                c.executar_ferramenta(
                    "impacto_bandeira_energia",
                    dict(base, consumo_total_kwh_mes=valor), P_G)

    def test_tres_ferramentas_com_nomes_unicos(self):
        nomes = [f["name"] for f in c.FERRAMENTAS]
        self.assertEqual(len(nomes), 3)
        self.assertEqual(len(set(nomes)), 3)


FAIXAS = [
    {"ate_kwh": 90, "aliquota": 0.0},
    {"ate_kwh": 200, "aliquota": 0.12},
    {"ate_kwh": None, "aliquota": 0.18},
]


class TestTributos(unittest.TestCase):
    ENT = dict(consumo_atual_kwh_mes=50, consumo_novo_kwh_mes=30, investimento_rs=400)

    def test_pis_cofins_por_dentro(self):
        p = dict(P, pis_cofins_aliquota=0.2)  # fator 1/(1-0,2) = 1,25
        r = c.alternativa_eficiencia(entrada(**self.ENT), p)
        self.assertAlmostEqual(r["economia_rs_mes"], 20 * 1.25)

    def test_icms_e_pis_cofins_se_multiplicam(self):
        # exemplo numerico publicado: 500 / ((1 - 0,18) x (1 - 0,05)) = 641,85
        p = dict(P, pis_cofins_aliquota=0.05, icms_faixas_residencial=FAIXAS)
        self.assertAlmostEqual(500 * c._fator_tributos(250, p), 641.85, places=2)
        # somar as aliquotas (erro antigo) daria 649,35
        self.assertGreater(abs(500 * c._fator_tributos(250, p) - 649.35), 5)

    def test_aliquota_icms_por_faixa(self):
        p = dict(P, icms_faixas_residencial=FAIXAS)
        self.assertEqual(
            [c.aliquota_icms(k, p) for k in (50, 90, 91, 200, 201, 500)],
            [0.0, 0.0, 0.12, 0.12, 0.18, 0.18])

    def test_sem_faixas_icms_zero(self):
        self.assertEqual(c.aliquota_icms(300, P), 0.0)

    def test_cruzar_a_faixa_muda_a_conta_inteira(self):
        p = dict(P, icms_faixas_residencial=FAIXAS)
        e = lambda k: entrada(beneficio="nenhum", consumo_total_kwh_mes=k)
        self.assertAlmostEqual(c.custo_energia_rs(201, e(201), p), 201 / 0.82)
        self.assertAlmostEqual(c.custo_energia_rs(200, e(200), p), 200 / 0.88)
        self.assertGreater(c.custo_energia_rs(201, e(201), p), c.custo_energia_rs(200, e(200), p) + 5)

    def test_eficiencia_usa_a_faixa_antes_e_depois(self):
        p = dict(P, icms_faixas_residencial=FAIXAS)
        r = c.alternativa_eficiencia(
            entrada(beneficio="nenhum", consumo_total_kwh_mes=205,
                    consumo_atual_kwh_mes=40, consumo_novo_kwh_mes=30, investimento_rs=100), p)
        self.assertAlmostEqual(r["economia_rs_mes"], 205 / 0.82 - 195 / 0.88, places=2)

    def test_fio_b_tambem_recebe_tributos(self):
        p = dict(P, pis_cofins_aliquota=0.2)
        r = c.alternativa_solar(entrada(), p)
        self.assertAlmostEqual(r["economia_energia_rs_mes"], 120 * 1.25)
        self.assertAlmostEqual(r["custo_fio_b_rs_mes"], 7.2 * 1.25)

    def test_aliquotas_invalidas(self):
        with self.assertRaises(ValueError):
            c.alternativa_eficiencia(entrada(**self.ENT), dict(P, pis_cofins_aliquota=1.0))
        with self.assertRaises(ValueError):
            c.alternativa_eficiencia(
                entrada(**self.ENT),
                dict(P, icms_faixas_residencial=[{"ate_kwh": None, "aliquota": 1.0}]))


class TestBandeira(unittest.TestCase):
    P_B = dict(
        P,
        bandeira_vigente="verde",
        bandeiras_adicional_rs_kwh={"verde": 0.0, "amarela": 0.02, "vermelha_p1": 0.05, "vermelha_p2": 0.08},
    )

    def test_verde_nao_altera(self):
        r = c.alternativa_eficiencia(
            entrada(consumo_atual_kwh_mes=50, consumo_novo_kwh_mes=30, investimento_rs=400), self.P_B)
        self.assertAlmostEqual(r["economia_rs_mes"], 20.0)

    def test_bandeira_soma_ao_kwh(self):
        r = c.alternativa_eficiencia(
            entrada(bandeira="vermelha_p2", consumo_atual_kwh_mes=50,
                    consumo_novo_kwh_mes=30, investimento_rs=400), self.P_B)
        self.assertAlmostEqual(r["economia_rs_mes"], 20 * 1.08)

    def test_bandeira_no_solar(self):
        r = c.alternativa_solar(entrada(bandeira="amarela"), self.P_B)
        self.assertAlmostEqual(r["economia_energia_rs_mes"], 120 * 1.02)

    def test_bandeira_invalida(self):
        with self.assertRaises(ValueError):
            c.alternativa_solar(entrada(bandeira="roxa"), self.P_B)


class TestComparacao(unittest.TestCase):
    def test_estrutura_e_resumo(self):
        r = c.comparar_alternativas(
            entrada(consumo_atual_kwh_mes=50, consumo_novo_kwh_mes=30,
                    investimento_rs=400), P)
        self.assertEqual(len(r["alternativas"]), 2)
        self.assertTrue(r["limitacoes"])
        texto = c.resumo_para_chatbot(r)
        self.assertIn("Limitacoes", texto)


if __name__ == "__main__":
    unittest.main()
