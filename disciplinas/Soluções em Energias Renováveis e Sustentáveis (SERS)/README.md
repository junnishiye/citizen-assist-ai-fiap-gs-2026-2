# Soluções em Energias Renováveis e Sustentáveis (SERS)

## Módulo "Minha Energia" — Citizen Assist AI / CitizenTech

**Global Solution 2026.2**



## Público e problema

Famílias de baixa e média-baixa renda da cidade de São Paulo que têm direito a desconto na conta de luz (Tarifa Social ou Desconto Social) mas podem perdê-lo sem perceber — o cadastro (CadÚnico) precisa continuar atualizado, e a perda costuma só ser notada quando a conta já chegou mais cara. O módulo também ajuda a decidir se vale trocar um equipamento ou instalar energia solar, e avisa quanto a bandeira tarifária do mês pesa na conta.

Este módulo é a peça de energia de um produto maior do grupo, o **CitizenTech** (app `gov.br` unificado). Ele é **independente** do módulo de documentos pessoais (matéria de Prompt and Artificial Intelligence, fichas FC-01 a FC-07) — não compartilha fonte de dados nem altera o golden dataset de 26 perguntas dessa outra matéria.

**Escopo:** só energia elétrica (sem módulo de água), só **Enel SP, cidade de São Paulo**. Os valores não se aplicam a outras distribuidoras ou municípios.

## Funcionalidades (3 ferramentas, chamadas pelo chatbot via function calling da OpenAI)

|Ferramenta|Quando é chamada|
|-|-|
|`verificar\_beneficio\_energia`|A pessoa pergunta se o desconto está em risco ou quanto vale por mês.|
|`comparar\_alternativas\_energia`|A pessoa quer saber se vale trocar um equipamento ou instalar energia solar.|
|`impacto\_bandeira\_energia`|A pessoa quer saber quanto a bandeira do mês soma à conta dela.|

O chatbot nunca calcula nem inventa números: todo valor em R$ ou kWh que ele fala vem de uma dessas ferramentas, e os avisos/limitações que cada uma devolve são sempre repetidos para o usuário.

## Estrutura desta pasta

|Arquivo|Para que serve|
|-|-|
|`calculos.py`|Cálculos e as 3 definições de ferramenta (`FERRAMENTAS`, `executar\_ferramenta`).|
|`parametros.json`|Todos os valores de referência (tarifas, regras, bandeiras), cada um com fonte e data.|
|`integracao\_openai.py`|Adaptador para a Chat Completions API: formato das tools, prompt de sistema, laço de chamadas, e barreira contra dados pessoais/prompt injection.|
|`teste\_calculos.py`, `teste\_integracao.py`|66 testes automatizados (58 + 8), sem rede e sem chave de API.|
|`LEIAME\_INTEGRACAO.md`|Guia técnico de integração para quem incorpora este módulo num chatbot.|
|`NOTAS\_INTEGRACAO\_ENERGIA.md`|Nota de integração com o restante do CitizenTech: o que foi recebido, o que mudou, limitações conhecidas.|
|`referencias.md`|Todas as fontes usadas em `parametros.json`, por parâmetro.|
|`justificativas.md`|Custo, viabilidade e impacto ambiental de cada funcionalidade, e por que as simplificações do modelo foram conservadoras.|
|`requirements.txt`|`openai>=1.0.0` (só para rodar o chat de exemplo).|

## Como testar

```bash
pip install -r requirements.txt
python3 -m unittest discover -p "teste\_\*.py" -v
```

Os testes não provam o comportamento do modelo real (usam um cliente OpenAI falso). Depois de integrar com a API de verdade, confira à mão se o chatbot: (a) pergunta o que falta antes de calcular, (b) chama a ferramenta certa, (c) só fala números vindos de uma ferramenta, e (d) repete os avisos. Exemplos de pergunta estão em `LEIAME\_INTEGRACAO.md`.

## Vídeo técnico

https://youtu.be/IxIRPCE4CBw

Fontes e limitações

Fontes completas em `referencias.md`. Justificativa de custo/viabilidade/impacto ambiental em `justificativas.md`. Principais ressalvas, resumidas:

* PIS/Cofins (5,45%) é **provisório** — varia todo mês; confirmado numa fatura real de outubro/2026.
* ICMS acima de 90 kWh foi **simplificado para 18% sobre todo o consumo** (a Enel SP lista 12% de 91 a 200 kWh), por falta de fatura ou fonte que confirme essa faixa intermediária — escolha conservadora, que superestima o imposto em vez de subestimá-lo.
* A tarifa do excedente da Tarifa Social acima de 80 kWh está confirmada por duas fontes oficiais da ANEEL, mas ainda não foi vista numa fatura real de Tarifa Social.
* O retorno (payback) da energia solar é estimativa, não garantia; depende de telhado, sombreamento e orçamento reais, não verificados pelo módulo.

Detalhes completos de cada premissa, com data e fonte, estão em `parametros.json` e são repetidos nos avisos que as próprias ferramentas devolvem ao chatbot.

