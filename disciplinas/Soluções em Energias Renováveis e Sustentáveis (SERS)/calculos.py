"""
Modulo "Minha energia" - contribuicao de Solucoes em Energias Renovaveis e
Sustentaveis ao Citizen Assist AI.

Compara duas alternativas para a MESMA necessidade (reduzir a conta de luz de
uma residencia de baixa renda) no MESMO periodo de referencia (1 mes):
  A) Eficiencia energetica: trocar um equipamento antigo por um eficiente
  B) Fonte renovavel: energia solar fotovoltaica (geracao distribuida)

Regras de faturamento modeladas (todas com fonte em parametros.json):
  - Tarifa Social: 100% de desconto nos primeiros 80 kWh/mes (Lei 15.235/2025).
    Economizar kWh dentro dessa franquia NAO reduz a conta.
  - Desconto Social: ate 120 kWh por tarifa reduzida; acima, tarifa Residencial
    (REH 3.596/2026, Tabela 2, nota 2).
  - Custo de disponibilidade: 30/50/100 kWh minimos (REN 1000/2021, art. 291).
  - Fio B: em 2026, 60% do Fio B incide sobre a energia compensada (Lei 14.300).
  - Tributos: ICMS por faixa de consumo e PIS/Cofins, combinados de forma
    multiplicativa (PIS/Cofins nao incide sobre o ICMS; pagina de impostos da Enel SP).

REGRA DO PROJETO: nenhum valor de referencia fica fixo no codigo. Tudo vem de
parametros.json, com fonte, data e flag de estimativa.

Uso pelo chatbot:
    from calculos import FERRAMENTAS, executar_ferramenta   # 3 ferramentas para o LLM
"""
import json
import math
from pathlib import Path

CAMINHO_PARAMETROS = Path(__file__).with_name("parametros.json")
LIGACOES = ("monofasico", "bifasico_2_condutores", "bifasico_3_condutores", "trifasico")


# ---------------------------------------------------------------- parametros
def _ler_json(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def carregar_parametros(caminho=CAMINHO_PARAMETROS):
    dados = _ler_json(caminho)
    pendentes = [k for k, v in dados["valores"].items() if v["valor"] is None]
    if pendentes:
        raise ValueError(
            "Preencha em parametros.json (com fonte e data): " + ", ".join(pendentes)
        )
    return {k: v["valor"] for k, v in dados["valores"].items()}


def parametros_provisorios(caminho=CAMINHO_PARAMETROS):
    dados = _ler_json(caminho)
    return [k for k, v in dados["valores"].items() if v.get("provisorio")]


AVISOS_POR_PARAMETRO = {
    "pis_cofins_aliquota": (
        "PIS/Cofins: usada a aliquota de uma fatura real da Enel SP (out/2026, 5,45%); "
        "a aliquota varia todo mes, entao o valor do mes pode diferir um pouco."
    ),
}


def avisos_provisorios(caminho=CAMINHO_PARAMETROS):
    """Mensagens para o cidadao sobre parametros provisorios do parametros.json."""
    avisos = []
    for nome in parametros_provisorios(caminho):
        avisos.append(
            AVISOS_POR_PARAMETRO.get(nome)
            or "Parametro provisorio (trocar pela fonte oficial): " + nome
        )
    return avisos


# ---------------------------------------------------------------- faturamento
def aliquota_icms(consumo_kwh, p):
    """Aliquota de ICMS residencial pela faixa do consumo mensal TOTAL.

    PREMISSA NAO VERIFICADA: a aliquota da faixa vale para todo o consumo, nao so
    para os kWh dentro da faixa (uma informacao do grupo neste sentido foi retirada
    em 14/11/2026, sem fonte). Sem icms_faixas_residencial em parametros = 0.
    """
    faixas = p.get("icms_faixas_residencial")
    if not faixas:
        return 0.0
    for faixa in faixas:
        if faixa["ate_kwh"] is None or consumo_kwh <= faixa["ate_kwh"]:
            return faixa["aliquota"]
    return faixas[-1]["aliquota"]


def _fator_tributos(consumo_kwh, p):
    """Fator que leva o preco SEM tributos ao preco COM tributos.

    Segundo a Enel SP, ICMS e PIS/Cofins sao calculados 'por dentro' e o PIS/Cofins
    NAO incide sobre o ICMS. Com P = T + ICMS + PISCofins, ICMS = i x P e
    PISCofins = c x (P - ICMS), resulta P = T / ((1 - i) x (1 - c)).
    Somar as aliquotas (1 / (1 - i - c)) esta errado para este caso.
    """
    pc = p.get("pis_cofins_aliquota", 0.0)
    icms = aliquota_icms(consumo_kwh, p)
    for nome, valor in (("pis_cofins_aliquota", pc), ("aliquota de ICMS", icms)):
        if not 0.0 <= valor < 1.0:
            raise ValueError(nome + " deve estar entre 0 e 1 (exclusive)")
    return 1.0 / ((1.0 - icms) * (1.0 - pc))


BENEFICIOS = ("tarifa_social", "desconto_social", "nenhum")


def _beneficio(entrada):
    """Beneficio tarifario da familia: tarifa_social (TSEE), desconto_social ou nenhum.

    PADRAO SEGURO: sem a chave 'beneficio' e sem o booleano antigo 'tarifa_social',
    assume NENHUM beneficio (decisao de 16/11/2026: um LLM que esquecer de perguntar
    nao deve presumir o cenario mais barato; e melhor superestimar a conta do que
    subestimar). Compatibilidade: o booleano antigo 'tarifa_social', se informado
    explicitamente como True, ainda ativa a Tarifa Social.
    """
    b = entrada.get("beneficio")
    if b is None:
        return "tarifa_social" if entrada.get("tarifa_social", False) else "nenhum"
    if b not in BENEFICIOS:
        raise ValueError("beneficio deve ser um de: " + ", ".join(BENEFICIOS))
    return b


def _adicional_bandeira(entrada, p):
    """Adicional da bandeira (R$/kWh, sem tributos). A cor vem de entrada['bandeira']
    ou, se ausente, de bandeira_vigente."""
    tabela = p.get("bandeiras_adicional_rs_kwh")
    if not tabela:
        return 0.0
    cor = entrada.get("bandeira") or p.get("bandeira_vigente", "verde")
    if cor not in tabela:
        raise ValueError("bandeira deve ser uma de: " + ", ".join(tabela))
    return tabela[cor]


def kwh_pagos(consumo_kwh, disponibilidade_kwh, franquia_kwh):
    """kWh que efetivamente geram cobranca de energia.

    Fatura-se no minimo o custo de disponibilidade; a franquia da Tarifa Social
    (80 kWh) e gratuita. Sem Tarifa Social, franquia_kwh = 0.
    """
    faturado = max(consumo_kwh, disponibilidade_kwh)
    return max(faturado - franquia_kwh, 0.0)


def _contexto(entrada, p):
    tipo = entrada.get("tipo_ligacao")
    if tipo not in LIGACOES:
        raise ValueError("tipo_ligacao deve ser um de: " + ", ".join(LIGACOES))
    disponibilidade = p["custo_disponibilidade_kwh_por_ligacao"][tipo]
    franquia = (
        p["franquia_tarifa_social_kwh"] if _beneficio(entrada) == "tarifa_social" else 0.0
    )
    return disponibilidade, franquia


def kwh_cobrados(consumo_kwh, entrada, p):
    """kWh que geram cobranca de energia (consumo faturado menos a franquia gratuita)."""
    disp, franquia = _contexto(entrada, p)
    return kwh_pagos(consumo_kwh, disp, franquia)


def custo_energia_rs(consumo_kwh, entrada, p):
    """Custo mensal da energia (R$, COM bandeira e tributos) para um consumo.

    - nenhum: tarifa Residencial em todos os kWh faturados.
    - tarifa_social: 80 kWh gratuitos; o restante pela tarifa Baixa Renda.
    - desconto_social: ate 120 kWh pela tarifa Desconto Social; acima, Residencial.
    A economia de qualquer medida e a diferenca entre o custo antes e depois.
    """
    beneficio = _beneficio(entrada)
    extra = _adicional_bandeira(entrada, p)
    fator = _fator_tributos(consumo_kwh, p)
    if beneficio == "desconto_social":
        disp, _ = _contexto(entrada, p)
        faturado = max(consumo_kwh, disp)
        limite = p["franquia_desconto_social_kwh"]
        faixa1 = min(faturado, limite)
        faixa2 = max(faturado - limite, 0.0)
        base = (
            faixa1 * (p["tarifa_desconto_social_rs_kwh"] + extra)
            + faixa2 * (p["tarifa_rs_kwh"] + extra)
        )
        return base * fator
    tarifa = (
        p["tarifa_baixa_renda_rs_kwh"] if beneficio == "tarifa_social" else p["tarifa_rs_kwh"]
    )
    return kwh_cobrados(consumo_kwh, entrada, p) * (tarifa + extra) * fator


def kwh_equipamento_mes(potencia_w, horas_dia, dias=30):
    """Energia (kWh) = potencia (kW) x tempo (h)."""
    return potencia_w / 1000 * horas_dia * dias


# ------------------------------------------------- uso 1: guardiao do beneficio
def valor_beneficio_mensal(entrada, p):
    """R$/mes que o beneficio vale hoje: custo sem beneficio menos custo com ele.

    Usa o consumo e o tipo de ligacao informados; valor com bandeira e tributos
    (aliquota informada; 0 = piso, sem tributos).
    """
    atual = _beneficio(entrada)
    if atual == "nenhum":
        return {"beneficio": "nenhum", "valor_rs_mes": 0.0}
    consumo = entrada["consumo_total_kwh_mes"]
    sem = custo_energia_rs(consumo, dict(entrada, beneficio="nenhum"), p)
    com = custo_energia_rs(consumo, entrada, p)
    return {"beneficio": atual, "valor_rs_mes": round(sem - com, 2)}


def avaliar_manutencao_beneficio(respostas, entrada, p):
    """Lista o que pode fazer a familia perder o beneficio e quanto isso custaria.

    respostas: {id_da_regra: True/False/None}. True = cumpre; False = nao cumpre;
    ausente ou None = nao informado (tambem conta como pendencia).
    """
    pendencias = []
    for regra in p["regras_manter_beneficio"]:
        ok = respostas.get(regra["id"])
        if ok is True:
            continue
        pendencias.append({
            "regra": regra["id"],
            "texto": regra["texto"],
            "situacao": "em_risco" if ok is False else "nao_informado",
            "acao": regra["acao"],
        })
    valor = valor_beneficio_mensal(entrada, p)
    return {
        "beneficio": valor["beneficio"],
        "valor_em_risco_rs_mes": valor["valor_rs_mes"],
        "todas_ok": not pendencias,
        "pendencias": pendencias,
    }


# ------------------------------------------------- uso 5: alerta de bandeira
def impacto_bandeira(entrada, p):
    """Quanto cada bandeira soma a conta de energia (R$/mes, em relacao a verde)
    para o consumo informado. Valores com tributos pela aliquota informada."""
    consumo = entrada["consumo_total_kwh_mes"]
    base = custo_energia_rs(consumo, dict(entrada, bandeira="verde"), p)
    impactos = {
        cor: round(custo_energia_rs(consumo, dict(entrada, bandeira=cor), p) - base, 2)
        for cor in p["bandeiras_adicional_rs_kwh"]
    }
    vigente = entrada.get("bandeira") or p.get("bandeira_vigente", "verde")
    return {
        "bandeira_vigente": vigente,
        "adicional_vigente_rs_mes": impactos[vigente],
        "impacto_rs_mes_por_bandeira": impactos,
    }


# ------------------------------------------------- alternativa A: eficiencia
def alternativa_eficiencia(entrada, p):
    """
    entrada: consumo_total_kwh_mes, consumo_atual_kwh_mes, consumo_novo_kwh_mes,
             investimento_rs, tipo_ligacao, tarifa_social (padrao True)
    A economia em R$ conta so os kWh PAGOS; a reducao de CO2 conta todos os kWh
    deixados de consumir.
    """
    antes = entrada["consumo_total_kwh_mes"]
    reducao = entrada["consumo_atual_kwh_mes"] - entrada["consumo_novo_kwh_mes"]
    depois = max(antes - reducao, 0.0)

    pagos_antes = kwh_cobrados(antes, entrada, p)
    pagos_depois = kwh_cobrados(depois, entrada, p)
    economia_kwh_pagos = pagos_antes - pagos_depois
    economia_rs = custo_energia_rs(antes, entrada, p) - custo_energia_rs(depois, entrada, p)
    payback = entrada["investimento_rs"] / economia_rs if economia_rs > 0 else None

    return {
        "nome": "Eficiencia energetica (troca de equipamento)",
        "reducao_consumo_kwh_mes": round(reducao, 1),
        "economia_kwh_pagos_mes": round(economia_kwh_pagos, 1),
        "economia_rs_mes": round(economia_rs, 2),
        "investimento_rs": entrada["investimento_rs"],
        "payback_meses": round(payback, 1) if payback else None,
        "co2_evitado_kg_mes": round(reducao * p["fator_emissao_media_kgco2_kwh"], 2),
        "co2_limite_superior_kg_mes": round(
            reducao * p["fator_emissao_margem_operacao_kgco2_kwh"], 2
        ),
        "viabilidade": "Baixo investimento inicial; so reduz a conta se o consumo da casa ficar acima da franquia gratuita.",
    }


# ---------------------------------------------------- alternativa B: solar
def geracao_por_kwp_mes(p):
    """kWh gerados por kWp instalado em 30 dias = HSP x taxa de desempenho x 30."""
    return p["hsp_kwh_m2_dia"] * p["taxa_desempenho"] * 30


def dimensionar_kwp(entrada, p):
    """kWp necessario para compensar os kWh que hoje geram cobranca.

    Nao se compensa abaixo do custo de disponibilidade, entao o alvo e o menor
    entre os kWh cobrados e (consumo - disponibilidade); do contrario o sistema
    ficaria superdimensionado para quem nao tem a franquia da Tarifa Social.
    """
    disp, _ = _contexto(entrada, p)
    consumo = entrada["consumo_total_kwh_mes"]
    alvo = min(kwh_cobrados(consumo, entrada, p), max(consumo - disp, 0.0))
    return alvo / geracao_por_kwp_mes(p)


def alternativa_solar(entrada, p):
    """
    entrada: consumo_total_kwh_mes, tipo_ligacao, tarifa_social (padrao True),
             potencia_kwp (opcional; se ausente, dimensiona pelos kWh pagos)

    Simplificacoes (conservadoras, ver LIMITACOES): toda a geracao compensada
    passa pela rede e paga o Fio B, inclusive dentro da franquia gratuita.
    """
    disp, _ = _contexto(entrada, p)
    consumo = entrada["consumo_total_kwh_mes"]
    kwp = entrada.get("potencia_kwp") or dimensionar_kwp(entrada, p)

    geracao = kwp * geracao_por_kwp_mes(p)
    # nao se compensa abaixo do custo de disponibilidade
    compensada = min(geracao, max(consumo - disp, 0.0))
    consumo_liquido = consumo - compensada

    economia_energia = (
        custo_energia_rs(consumo, entrada, p) - custo_energia_rs(consumo_liquido, entrada, p)
    )
    custo_fio_b = (
        compensada * p["fio_b_pct_nao_compensado"] * p["fio_b_rs_kwh"] * _fator_tributos(consumo_liquido, p)
    )
    economia_rs = economia_energia - custo_fio_b

    investimento = kwp * p["custo_rs_por_kwp"]
    payback = investimento / economia_rs if economia_rs > 0 else None

    return {
        "nome": "Energia solar fotovoltaica",
        "potencia_kwp": round(kwp, 2),
        "geracao_estimada_kwh_mes": round(geracao, 1),
        "energia_compensada_kwh_mes": round(compensada, 1),
        "economia_energia_rs_mes": round(economia_energia, 2),
        "custo_fio_b_rs_mes": round(custo_fio_b, 2),
        "economia_rs_mes": round(economia_rs, 2),
        "investimento_rs": round(investimento, 2),
        "payback_meses": round(payback, 1) if payback else None,
        "co2_evitado_kg_mes": round(compensada * p["fator_emissao_media_kgco2_kwh"], 2),
        "co2_limite_superior_kg_mes": round(
            compensada * p["fator_emissao_margem_operacao_kgco2_kwh"], 2
        ),
        "viabilidade": "Investimento alto; exige telhado adequado, sem sombra, e imovel proprio ou geracao compartilhada.",
    }


# ------------------------------------------------------------- comparacao
LIMITACOES = [
    "Valores sao ESTIMATIVAS, nao garantia de economia ou geracao.",
    "A tarifa muda com reajustes anuais, e a bandeira tarifaria muda todo mes (a verde nao tem adicional; amarela e vermelha somam um valor por kWh). Tarifa, adicional e Fio B estao sem tributos e recebem ICMS e PIS/Cofins: o PIS/Cofins pela aliquota efetiva mensal (muda todo mes) e o ICMS pela faixa do consumo mensal total (isento ate 90 kWh, 18% acima; simplificacao do grupo, que superestima o ICMS de 91 a 200 kWh em relacao aos 12% listados pela Enel SP nessa faixa), combinados de forma multiplicativa porque o PIS/Cofins nao incide sobre o ICMS (pagina da Enel SP); o resultado muda junto. Premissa NAO verificada: a aliquota de 18% vale para TODO o consumo acima de 90 kWh, e nao so para os kWh acima de 90; se for marginal, o modulo superestima ainda mais o ICMS nessa faixa. Nao foi verificado se o desconto da Tarifa Social alcanca o adicional de bandeira. Na fatura real o adicional e cobrado proporcional aos dias de cada bandeira e apareceu sem PIS/Cofins nem ICMS; o modulo usa uma bandeira so por mes e aplica tributos sobre o adicional, o que muda centavos em consumos baixos.",
    "Tarifa Social: os primeiros 80 kWh/mes tem desconto de 100% (Lei 15.235/2025); economizar energia dentro dessa faixa nao reduz a conta. Acima de 80 kWh o calculo usa a tarifa da subclasse Baixa Renda, menor que a Residencial (REH 3.596/2026, Tabelas 2 e 3); confirmado por duas fontes oficiais independentes: o texto da REH (Tabelas 2 e 3) e os Dados Abertos da ANEEL (Tarifas de Aplicacao, subclasses 'Tarifa Social - faixa 01/02'); ainda nao visto numa fatura real de Tarifa Social. A elegibilidade (CadUnico) nao foi verificada.",
    "A conta nao zera: ha custo de disponibilidade (30, 50 ou 100 kWh; gratuito ate 80 kWh para a Tarifa Social), contribuicao de iluminacao publica (CIP/COSIP), que continua devida mesmo com consumo ate 80 kWh e nao foi modelada (o valor depende do municipio).",
    "Solar: o custo da energia compensada segue o regime GD II de 2026 (60% do Fio B, REH 3.596/2026, Tabela 4); em 2027 sobe para 75%. Um sistema residencial novo (solicitacao apos 07/01/2023) se enquadra em GD II (REN 1.000/2021, arts. 655-O a 655-Q); sistemas protocolados ate 07/01/2023 sao GD I, com regra mais favoravel que nao foi modelada. O calculo assume que toda a geracao passa pela rede e paga o Fio B, o que e conservador; a regra exata combinada com a Tarifa Social nao foi verificada. O valor do Fio B (TUSD_FioB, B1 Residencial) vem agora dos Dados Abertos da ANEEL (Componentes Tarifarias), nao mais derivado da REH.",
    "A geracao solar varia com clima, temperatura, sombreamento, orientacao e inclinacao do telhado. A taxa de desempenho usada e o piso da faixa de 70% a 80% citada para sistemas residenciais bem ventilados e sem sombra, e a degradacao dos modulos (ate 0,5% ao ano) nao entra no calculo mensal.",
    "Desconto Social (CadUnico acima de 1/2 e ate 1 salario minimo per capita): ate 120 kWh a tarifa e reduzida e ha isencao da CDE; acima disso vale a tarifa Residencial (REH 3.596/2026, Tabela 2, nota 2; pagina da Enel SP). Nao foi verificado se o adicional de bandeira recebe desconto nesse beneficio.",
    "Nao foi verificado sobre qual base ICMS, PIS e Cofins incidem na parcela com 100% de desconto: a Enel SP diz que tributos continuam cobrados mesmo com o desconto. Se incidirem sobre a tarifa cheia, economizar dentro dos 80 kWh gratuitos tambem reduziria tributos, o que este modelo nao captura.",
    "Precos de equipamentos e instalacao variam por regiao e fornecedor; peca orcamentos.",
    "CO2: o valor principal usa o fator medio do SIN; o limite superior usa o metodo marginal (margem de operacao), muito maior. Escolher o metodo muda o resultado em ordem de grandeza.",
]


def comparar_alternativas(entrada, p=None):
    avisos = []
    if p is None:
        p = carregar_parametros()
        avisos = avisos_provisorios()
    return {
        "periodo_referencia": "1 mes",
        "alternativas": [alternativa_eficiencia(entrada, p), alternativa_solar(entrada, p)],
        "limitacoes": LIMITACOES,
        "avisos": avisos,
    }


def _linha_alternativa(alt):
    if alt["economia_rs_mes"] > 0:
        retorno = f"retorno em {alt['payback_meses']} meses"
        financeiro = f"economia estimada de R$ {alt['economia_rs_mes']}/mes"
    else:
        retorno = "sem retorno financeiro estimado"
        financeiro = "nao reduz a conta neste cenario"
    return (
        f"- {alt['nome']}: {financeiro}, investimento R$ {alt['investimento_rs']}, "
        f"{retorno}, CO2 evitado ~{alt['co2_evitado_kg_mes']} kg/mes. {alt['viabilidade']}"
    )


def resumo_para_chatbot(resultado):
    """Texto curto para o LLM usar como base da resposta ao cidadao."""
    linhas = [_linha_alternativa(a) for a in resultado["alternativas"]]
    linhas.append("Limitacoes: " + " ".join(resultado["limitacoes"]))
    linhas.extend(resultado["avisos"])
    return "\n".join(linhas)


# ------------------------ definicao de ferramenta para o LLM (formato generico)
TOOL_SCHEMA = {
    "name": "comparar_alternativas_energia",
    "description": (
        "Compara eficiencia energetica e energia solar para reduzir a conta de luz "
        "de uma residencia. Use quando o cidadao perguntar como economizar energia."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "consumo_total_kwh_mes": {"type": "number", "description": "Consumo mensal da casa em kWh (esta na fatura)"},
            "consumo_atual_kwh_mes": {"type": "number", "description": "Consumo mensal do equipamento atual em kWh"},
            "consumo_novo_kwh_mes": {"type": "number", "description": "Consumo mensal do equipamento eficiente em kWh"},
            "investimento_rs": {"type": "number", "description": "Preco do equipamento novo em R$"},
            "tipo_ligacao": {"type": "string", "enum": list(LIGACOES), "description": "Tipo de ligacao (esta na fatura)"},
            "beneficio": {"type": "string", "enum": list(BENEFICIOS), "description": "Beneficio tarifario: tarifa_social (CadUnico ate 1/2 salario minimo per capita; 80 kWh gratuitos), desconto_social (CadUnico acima de 1/2 e ate 1 salario minimo per capita; tarifa reduzida ate 120 kWh) ou nenhum. Padrao: nenhum (se a familia tiver beneficio, informe; nao presuma)"},
            "potencia_kwp": {"type": "number", "description": "Opcional: potencia do sistema solar em kWp; se omitido, e dimensionado"},
            "bandeira": {"type": "string", "enum": ["verde", "amarela", "vermelha_p1", "vermelha_p2"], "description": "Opcional: bandeira tarifaria do mes; se omitida, usa a vigente em parametros.json"},
        },
        "required": [
            "consumo_total_kwh_mes", "consumo_atual_kwh_mes",
            "consumo_novo_kwh_mes", "investimento_rs", "tipo_ligacao",
        ],
    },
}


TOOL_BENEFICIO = {
    "name": "verificar_beneficio_energia",
    "description": (
        "Verifica se a familia corre risco de perder a Tarifa Social ou o Desconto Social "
        "de energia e quanto o beneficio vale por mes. Use quando o cidadao perguntar se o "
        "desconto na conta de luz esta em risco ou quanto ele vale."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "consumo_total_kwh_mes": {"type": "number", "description": "Consumo mensal da casa em kWh (esta na fatura)"},
            "tipo_ligacao": {"type": "string", "enum": list(LIGACOES), "description": "Tipo de ligacao (esta na fatura)"},
            "beneficio": {"type": "string", "enum": ["tarifa_social", "desconto_social"], "description": "Beneficio que a familia recebe"},
            "cadunico_atualizado": {"type": "boolean", "description": "O CadUnico foi atualizado nos ultimos 2 anos?"},
            "municipio_igual_conta": {"type": "boolean", "description": "O municipio do CadUnico e o mesmo da conta de energia?"},
            "titular_da_conta": {"type": "boolean", "description": "O beneficiario e o titular da conta de energia?"},
        },
        "required": ["consumo_total_kwh_mes", "tipo_ligacao", "beneficio"],
    },
}

TOOL_BANDEIRA = {
    "name": "impacto_bandeira_energia",
    "description": (
        "Informa quanto cada bandeira tarifaria (amarela, vermelha 1 e 2) soma a conta de "
        "luz da familia, com base no consumo dela. Use para avisar sobre a bandeira do mes."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "consumo_total_kwh_mes": {"type": "number", "description": "Consumo mensal da casa em kWh (esta na fatura)"},
            "tipo_ligacao": {"type": "string", "enum": list(LIGACOES), "description": "Tipo de ligacao (esta na fatura)"},
            "beneficio": {"type": "string", "enum": list(BENEFICIOS), "description": "Beneficio tarifario da familia. Padrao: nenhum (se a familia tiver beneficio, informe; nao presuma)"},
            "bandeira": {"type": "string", "enum": ["verde", "amarela", "vermelha_p1", "vermelha_p2"], "description": "Opcional: bandeira do mes; se omitida, usa a vigente em parametros.json"},
        },
        "required": ["consumo_total_kwh_mes", "tipo_ligacao"],
    },
}

FERRAMENTAS = [TOOL_SCHEMA, TOOL_BENEFICIO, TOOL_BANDEIRA]


_CAMPOS_NUMERICOS_NAO_NEGATIVOS = (
    "consumo_total_kwh_mes", "consumo_atual_kwh_mes", "consumo_novo_kwh_mes",
    "investimento_rs", "potencia_kwp",
)


def _validar_numeros(argumentos):
    """Rejeita valor numerico invalido (negativo, nao numerico ou booleano) antes de
    calcular, em vez de devolver um resultado sem sentido (16/11/2026)."""
    for nome in _CAMPOS_NUMERICOS_NAO_NEGATIVOS:
        if nome not in argumentos:
            continue
        valor = argumentos[nome]
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError(nome + " deve ser um numero.")
        if not math.isfinite(valor) or valor < 0:
            raise ValueError(nome + " nao pode ser negativo nem infinito/NaN.")


def executar_ferramenta(nome, argumentos, p=None):
    """Despacha a chamada de ferramenta do LLM (qualquer framework) para o calculo."""
    _validar_numeros(argumentos)
    if nome == "comparar_alternativas_energia":
        r = comparar_alternativas(argumentos, p)
        return dict(r, resumo=resumo_para_chatbot(r))
    avisos = avisos_provisorios() if p is None else []
    p = p or carregar_parametros()
    if nome == "verificar_beneficio_energia":
        respostas = {
            regra["id"]: argumentos.get(regra["id"])
            for regra in p["regras_manter_beneficio"]
        }
        return dict(avaliar_manutencao_beneficio(respostas, argumentos, p), avisos=avisos)
    if nome == "impacto_bandeira_energia":
        return dict(impacto_bandeira(argumentos, p), avisos=avisos)
    raise ValueError("ferramenta desconhecida: " + str(nome))


if __name__ == "__main__":
    # Exemplo de ENTRADA do usuario (nao e dado de referencia). So roda depois de
    # preencher os valores PENDENTES em parametros.json.
    exemplo = {
        "consumo_total_kwh_mes": 200,
        "consumo_atual_kwh_mes": 50,
        "consumo_novo_kwh_mes": 30,
        "investimento_rs": 2000,
        "tipo_ligacao": "monofasico",
        "tarifa_social": True,
    }
    try:
        print(resumo_para_chatbot(comparar_alternativas(exemplo)))
    except ValueError as erro:
        print("PENDENTE:", erro)
