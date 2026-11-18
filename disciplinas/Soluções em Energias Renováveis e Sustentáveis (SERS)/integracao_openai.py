"""
Integracao do modulo "Minha energia" com a API da OpenAI (function calling).

Usa o formato da Chat Completions API. Requisitos:
    pip install openai
    variaveis de ambiente: OPENAI_API_KEY e OPENAI_MODEL (o mesmo modelo mini que o
    chatbot ja usa; nao e definido aqui de proposito).

Uso minimo dentro do chatbot existente:
    from integracao_openai import ferramentas_openai, executar_chamadas, PROMPT_SISTEMA
    # 1) tools=ferramentas_openai() na chamada de chat.completions.create
    # 2) incluir PROMPT_SISTEMA no prompt de sistema (ou juntar ao que ja existe)
    # 3) quando a resposta tiver tool_calls, rodar executar_chamadas(tool_calls) e
    #    devolver as mensagens role=tool ao modelo

Ou, para um chat completo, usar responder(cliente, historico).
"""
import json
import os

from calculos import FERRAMENTAS, executar_ferramenta

# Regra do projeto: NENHUM numero de referencia aparece neste prompt. Todo numero
# que o assistente falar deve vir de uma ferramenta (um teste garante isso).
PROMPT_SISTEMA = """Voce e o assistente de energia do app de servicos publicos. Ajuda familias a entender e reduzir a conta de luz, a nao perder descontos sociais e a decidir se vale a pena agir.

Regras obrigatorias:
- Todo numero (R$, kWh, prazo de retorno, impacto de bandeira, valor de beneficio) deve vir do resultado de uma ferramenta. Nunca calcule, estime ou invente numeros por conta propria.
- Antes de chamar uma ferramenta, confirme com a pessoa os dados que faltam: consumo mensal em kWh e tipo de ligacao (ambos estao na fatura) e qual beneficio a familia recebe (Tarifa Social, Desconto Social ou nenhum). Para comparar equipamentos, peca tambem o consumo mensal do equipamento atual, o do equipamento novo (etiqueta Procel/Inmetro) e o preco do novo. Se uma ferramenta devolver erro, explique o que falta e pergunte de novo.
- Use verificar_beneficio_energia quando a pessoa perguntar se o desconto esta em risco ou quanto ele vale. Pergunte se o CadUnico foi atualizado nos ultimos dois anos, se o municipio do CadUnico e o mesmo da conta e se o beneficiario e o titular da conta. Para cada pendencia, diga a acao sugerida pela ferramenta. Fale em risco; nunca afirme que o beneficio sera perdido.
- Use comparar_alternativas_energia para comparar eficiencia energetica e energia solar. Se o resultado mostrar que nenhuma alternativa se paga ou que nao reduz a conta, diga isso com clareza. Nao force uma recomendacao.
- Use impacto_bandeira_energia para dizer quanto a bandeira do mes soma a conta da familia. Se o impacto for pequeno, diga que e pequeno.
- Sempre inclua, em linguagem simples, os avisos e limitacoes que a ferramenta devolver (por exemplo, que os valores sao estimativas e quais premissas ainda sao provisorias). Financiamento so pode ser citado como possibilidade sujeita a aprovacao de credito.
- Os valores se aplicam somente a Enel SP (Sao Paulo capital). Se a pessoa for de outra distribuidora, avise que os valores podem nao se aplicar.
- Nao peca nem repita dados pessoais (nome, CPF, endereco, numero da instalacao). Voce nao e consultor financeiro nem juridico: nao garanta economia.
- Responda em portugues simples e curto."""


def ferramentas_openai():
    """Converte as definicoes (input_schema) para o formato da Chat Completions API."""
    return [
        {
            "type": "function",
            "function": {
                "name": f["name"],
                "description": f["description"],
                "parameters": f["input_schema"],
            },
        }
        for f in FERRAMENTAS
    ]


def executar_chamadas(tool_calls):
    """Executa os tool_calls devolvidos pelo modelo e monta as mensagens role=tool.

    Erros (argumento faltando, valor invalido) voltam ao modelo como {"erro": ...}
    para ele perguntar ao usuario, em vez de derrubar o chat.
    """
    mensagens = []
    for chamada in tool_calls:
        try:
            argumentos = json.loads(chamada.function.arguments or "{}")
            resultado = executar_ferramenta(chamada.function.name, argumentos)
        except Exception as erro:  # noqa: BLE001 - o erro e devolvido ao modelo
            resultado = {"erro": str(erro)}
        mensagens.append({
            "role": "tool",
            "tool_call_id": chamada.id,
            "content": json.dumps(resultado, ensure_ascii=False),
        })
    return mensagens


def _mensagem_do_assistente(msg):
    return {
        "role": "assistant",
        "content": msg.content,
        "tool_calls": [
            {
                "id": c.id,
                "type": "function",
                "function": {"name": c.function.name, "arguments": c.function.arguments},
            }
            for c in msg.tool_calls
        ],
    }


def responder(cliente, historico, modelo=None, max_voltas=4):
    """Responde a ultima mensagem do usuario, chamando ferramentas quando preciso.

    historico: lista de {"role": "user"/"assistant", "content": ...} SEM o prompt de
    sistema. Devolve (texto, historico_atualizado).
    """
    modelo = modelo or os.environ.get("OPENAI_MODEL")
    if not modelo:
        raise ValueError("Defina OPENAI_MODEL (o modelo mini que o chatbot ja usa).")
    mensagens = [{"role": "system", "content": PROMPT_SISTEMA}] + list(historico)
    for _ in range(max_voltas):
        resposta = cliente.chat.completions.create(
            model=modelo, messages=mensagens, tools=ferramentas_openai()
        )
        msg = resposta.choices[0].message
        if not msg.tool_calls:
            return msg.content, list(historico) + [{"role": "assistant", "content": msg.content}]
        mensagens.append(_mensagem_do_assistente(msg))
        mensagens.extend(executar_chamadas(msg.tool_calls))
    texto = "Nao consegui concluir o calculo agora. Tente de novo em instantes."
    return texto, list(historico) + [{"role": "assistant", "content": texto}]


if __name__ == "__main__":
    from openai import OpenAI  # importado aqui para os testes nao exigirem o pacote

    cliente = OpenAI()
    historico = []
    print("Assistente de energia (Ctrl+C para sair)")
    while True:
        historico.append({"role": "user", "content": input("> ")})
        texto, historico = responder(cliente, historico)
        print(texto)
