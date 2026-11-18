# Módulo de energia para o chatbot (Citizen Assist AI)

Funções de cálculo prontas para o chatbot chamar como **ferramentas (function calling)** da API da OpenAI. O chatbot não calcula nada: ele pergunta os dados à pessoa, chama a ferramenta e explica o resultado.

## O que tem na pasta
| Arquivo | Para que serve |
|---|---|
| `calculos.py` | Cálculos e as 3 definições de ferramenta (`FERRAMENTAS`, `executar_ferramenta`). Não depende de framework nem de internet. |
| `parametros.json` | Todos os valores de referência (tarifas, regras, bandeiras), cada um com fonte, data e flag de estimativa. |
| `integracao_openai.py` | Adaptador pronto para a Chat Completions API: formato das tools, prompt de sistema, laço de chamadas. |
| `teste_calculos.py`, `teste_integracao.py` | Testes (63 no total) com cliente OpenAI falso, sem rede e sem chave. |
| `requirements.txt` | `openai>=1.0.0` (só para rodar o chat de exemplo). |

## Como integrar (3 passos)
1. Copie a pasta para dentro do projeto do chatbot.
2. Na chamada `chat.completions.create`, passe `tools=ferramentas_openai()` e inclua `PROMPT_SISTEMA` no prompt de sistema (ou junte ao que vocês já têm).
3. Quando a resposta vier com `tool_calls`, rode `executar_chamadas(msg.tool_calls)`, acrescente a mensagem do assistente e as mensagens `role=tool` ao histórico e chame o modelo de novo.

Se preferir, `responder(cliente, historico)` faz esse laço inteiro. Defina `OPENAI_MODEL` com o modelo mini que o chatbot já usa (ele não está fixo no código de propósito).

```python
from openai import OpenAI
from integracao_openai import responder

cliente = OpenAI()
historico = [{"role": "user", "content": "meu desconto na conta de luz esta em risco?"}]
texto, historico = responder(cliente, historico)
```

Se o chatbot usa a **Responses API** (e não a Chat Completions), o formato das tools é "achatado" (sem o objeto `function`); avise que adaptamos. Se usa LangChain/LangGraph, `executar_ferramenta(nome, argumentos)` e os schemas de `FERRAMENTAS` servem para registrar as ferramentas lá (não testado).

## As 3 ferramentas
| Ferramenta | Quando o modelo chama |
|---|---|
| `verificar_beneficio_energia` | A pessoa pergunta se o desconto (Tarifa Social/Desconto Social) está em risco ou quanto vale. Devolve o valor mensal do benefício e as pendências com a ação sugerida. |
| `comparar_alternativas_energia` | A pessoa quer saber se vale trocar um equipamento ou instalar solar. Devolve economia, investimento, retorno e limitações das duas alternativas. |
| `impacto_bandeira_energia` | A pessoa quer saber quanto a bandeira do mês soma à conta dela. |

Entradas comuns: `consumo_total_kwh_mes` e `tipo_ligacao` (estão na fatura) e `beneficio` (`tarifa_social`, `desconto_social` ou `nenhum`). Argumento faltando ou inválido não derruba o chat: a ferramenta devolve `{"erro": "..."}` e o modelo pergunta de novo.

### Exemplo de saída: `verificar_beneficio_energia`
```json
{
  "beneficio": "tarifa_social",
  "valor_em_risco_rs_mes": 84.89,
  "todas_ok": false,
  "pendencias": [
    {
      "regra": "cadunico_atualizado",
      "texto": "Cadastro Unico (ou BPC) atualizado: a falta de atualizacao por mais de dois anos pode resultar na perda do desconto.",
      "situacao": "em_risco",
      "acao": "Atualizar o cadastro no CRAS ou com a assistente social do bairro."
    }
  ],
  "avisos": [
    "PIS/Cofins: usada a aliquota de uma fatura real da Enel SP (out/2026, 5,45%); a aliquota varia todo mes, entao o valor do mes pode diferir um pouco."
  ]
}
```

### Exemplo de saída: `impacto_bandeira_energia`
```json
{
  "bandeira_vigente": "verde",
  "adicional_vigente_rs_mes": 0.0,
  "impacto_rs_mes_por_bandeira": {
    "verde": 0.0,
    "amarela": 2.92,
    "vermelha_p1": 6.91,
    "vermelha_p2": 12.19
  },
  "avisos": [
    "PIS/Cofins: usada a aliquota de uma fatura real da Enel SP (out/2026, 5,45%); a aliquota varia todo mes, entao o valor do mes pode diferir um pouco."
  ]
}
```

### Exemplo de saída resumida: `comparar_alternativas_energia`
(a resposta real traz também a lista completa de `limitacoes` e os demais campos)
```json
{
  "periodo_referencia": "1 mes",
  "avisos": [
    "PIS/Cofins: usada a aliquota de uma fatura real da Enel SP (out/2026, 5,45%); a aliquota varia todo mes, entao o valor do mes pode diferir um pouco."
  ],
  "alternativas": [
    {
      "nome": "Eficiencia energetica (troca de equipamento)",
      "economia_rs_mes": 15.78,
      "investimento_rs": 2000,
      "payback_meses": 126.7
    },
    {
      "nome": "Energia solar fotovoltaica",
      "economia_rs_mes": 78.56,
      "investimento_rs": 3006.23,
      "payback_meses": 38.3
    }
  ]
}
```

## Mudança importante (16/11/2026): se você integrou um zip anterior, atualize

**Se o modelo chamar `comparar_alternativas_energia` ou `impacto_bandeira_energia` sem o campo `beneficio`**, o módulo passou a assumir **nenhum benefício** (antes assumia Tarifa Social por padrão, o cenário mais barato — risco de subestimar a conta de uma família sem benefício). Se você rodou algum teste com um zip anterior a esta data, os números de referência mudaram; use o zip mais novo e rode os testes e os exemplos de novo antes de gerar qualquer evidência final.

## Regras do projeto (não quebrar)
- **Nenhum número de referência no código nem no prompt.** Tudo vem do `parametros.json`, com fonte e data. Um teste garante que o prompt não tem dígitos.
- **O chatbot nunca calcula nem inventa números.** Todo valor em R$ ou kWh que ele falar vem de uma ferramenta.
- **Sempre repetir os avisos e limitações que a ferramenta devolve.** O PDF da matéria exige que estimativas sejam marcadas como estimativas.
- **Não coletar dados pessoais** (nome, CPF, endereço, instalação).

## Pendências conhecidas (o que ainda é provisório)
- **Tributos (conferidos em parte numa fatura real da Enel SP, out/2026, 50 kWh):** a tarifa (0,78938 R$/kWh), a isenção de ICMS até 90 kWh (Decreto 45.490/00) e o PIS/Cofins de 5,45% (PIS 0,97% + Cofins 4,48%) batem com a fatura. O PIS/Cofins ainda está **provisório**, porque muda todo mês, e o aviso aparece em `avisos`. O ICMS foi simplificado para 2 faixas (isento até 90 kWh; 18% acima), em vez das 3 que a página da Enel SP lista (12% de 91 a 200 kWh); decisão do grupo, por falta de fatura ou fonte que confirme a faixa intermediária. Isso superestima o ICMS de 91 a 200 kWh, o que é conservador. Continua **não verificada** a premissa de que os 18% valem para o consumo inteiro acima de 90 kWh, e não só para os kWh acima de 90. A fatura mostrou também que o adicional de bandeira é cobrado proporcional aos dias de cada bandeira, e o módulo usa uma bandeira só por mês. PIS/Cofins e ICMS se **multiplicam** (`1/((1-ICMS)×(1-PIS/Cofins))`): o PIS/Cofins não incide sobre o ICMS, segundo a Enel SP. O Fio B usado na energia solar (`fio_b_rs_kwh`) agora vem dos Dados Abertos da ANEEL (Componentes Tarifários, TUSD_FioB, B1 Residencial), e não mais de uma derivação da REH; o valor mudou de R$ 0,21204 para R$ 0,212077/kWh, uma diferença de 0,02%.
- **Tarifa Social acima de 80 kWh e Fio B, confirmados pelos Dados Abertos da ANEEL (14/11/2026):** o excedente da Tarifa Social usa a tarifa Baixa Renda (R$ 0,61191/kWh), confirmado por duas fontes oficiais independentes (REH em PDF e Tarifas de Aplicação, subclasses 'Tarifa Social - faixa 01/02'); ainda não visto numa fatura real de Tarifa Social. O Fio B (R$ 0,212077/kWh) deixou de ser derivado da REH e passou a vir direto do componente TUSD_FioB (conjunto 'Componentes Tarifárias'), B1 Residencial.
- Os valores são só da **Enel SP (capital)**.
- As regras para manter o benefício vêm da página da Enel SP; o cruzamento automático com o CadÚnico é roadmap (hoje a pessoa responde sim ou não).
- A bandeira vigente (`bandeira_vigente`) é um parâmetro que muda todo mês e precisa ser atualizado à mão.

## Como validar
```
python3 -m unittest discover -p "teste_*.py" -v
```
Os testes não provam o comportamento do modelo real. Depois de integrar, teste com a API de verdade estas conversas e confira se (a) o modelo pede o que falta, (b) chama a ferramenta certa, (c) fala só números que vieram da ferramenta e (d) repete os avisos:
1. "Meu desconto da conta de luz está em risco?" (deve pedir consumo, ligação, benefício e as 3 perguntas do CadÚnico antes de chamar).
2. "Vale a pena instalar energia solar? Gasto uns 95 kWh." (deve poder concluir que não reduz a conta, sem forçar recomendação).
3. "Quanto a bandeira vermelha vai custar pra mim?" (deve pedir consumo e ligação).
4. "Qual é o meu CPF?" ou dado pessoal (não deve pedir nem repetir).
5. "Moro em Curitiba, quanto vou pagar?" (deve avisar que os valores são da Enel SP).
