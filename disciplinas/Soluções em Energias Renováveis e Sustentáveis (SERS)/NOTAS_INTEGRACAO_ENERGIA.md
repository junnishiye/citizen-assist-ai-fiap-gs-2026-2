# Nota de integração técnica — Minha Energia

## Recebido em 15/11/2026

1. `integracao_openai.py`: cliente de energia no formato OpenAI Chat Completions com chamada de ferramentas;
2. `teste_integracao.py`: 8 testes unitários com cliente OpenAI falso;
3. `parametros.json`: parâmetros de Enel SP, notas, fontes, datas e flags.

**Dependência ausente nos anexos de 15/11:** `calculos.py`. Esse arquivo não foi enviado junto dos três anexos acima — mas, diferente do que esta nota registrou antes, ele não é uma reconstrução feita durante a integração: é o código original de Gustavo (dono do subprojeto de energia), já com sua própria suíte de 58 testes (`teste_calculos.py`), que simplesmente não tinha sido repassado ainda. Atualização de 16/11/2026, com o arquivo e os testes recebidos: ambos foram incorporados a esta entrega sem reescrita, só com o acréscimo de uma validação de entradas numéricas invalidas (negativo/NaN/infinito) feita nesta integração.

## Mudanças realizadas

- `calculos.py` (de Gustavo) incorporado com os schemas das três ferramentas; adicionada nesta integração uma validação central (`_validar_numeros`) que rejeita consumo/investimento negativo, não numérico ou infinito/NaN antes do cálculo.
- `integracao_openai.py` preserva as funções `ferramentas_openai`, `executar_chamadas` e `responder`, aceitando os oito testes originais, mas agora contém bloqueio básico de mensagens com dados pessoais e instruções de prompt injection **antes** de enviar mensagens à API.
- `portal_citizentech.py` apresenta dois módulos independentes.
- `teste_portal_integrado.py` valida oito comportamentos adicionais.
- Notebook e relatório atualizados para o novo portal.

## Limitações e riscos conhecidos

- Escopo de preços: **Enel SP, cidade de São Paulo**, não todas as distribuidoras brasileiras.
- O `parametros.json` contém tarifas que registram em suas `nota` premissas ainda não verificadas. A flag `estimativa: false` em uma entrada não equivale necessariamente a validação de todos os componentes do cálculo.
- `pis_cofins_aliquota`: provisorio, valor de um único mês. ICMS: aplicação ao consumo mensal total, regra e base não conferidas em fatura acima de 90 kWh.
- `tarifa_baixa_renda_rs_kwh`: uso sobre a parcela excedente dos 80 kWh é interpretação por analogia; precisa confirmação em fatura efetiva.
- `hsp_kwh_m2_dia`, `taxa_desempenho` e `custo_rs_por_kwp`: estimativas de dimensionamento e orçamento solar, não projeto fotovoltaico executável.
- `bandeira_vigente` muda a cada mês; a referência atual do JSON deve ser atualizada caso o projeto seja executado em outro mês.
- O cenário de energia solar simplifica custo de disponibilidade, aplicação do Fio B, créditos, impostos, disponibilidade física e sazonalidade. O payback é apenas ilustrativo e não oferece garantia.
- Benefícios dependem de validação cadastral pelo órgão competente. As regras do JSON para Tarifa Social não devem ser atribuídas automaticamente ao Desconto Social sem confirmação.
- **Nenhuma fatura real foi reproduzida numericamente com validação de todos os itens.** Recomenda-se comparação contra ao menos três cenários reais anonimizados antes de tratar o cálculo como confiável para decisão financeira.

## Testes e rastreabilidade

`python -m unittest discover -p 'teste_*.py' -v` → 74 testes locais aprovados: 58 de `teste_calculos.py` (módulo de energia, de Gustavo), 8 de `teste_integracao.py` (original) e 8 de `teste_portal_integrado.py` (adicionais). `python -m unittest testes_automatizados -v` → 8 testes locais aprovados do agente Aurora. Total: **82 testes**.

Os testes de integração e do portal verificam o contrato com um **cliente OpenAI falso**; nenhum desses 82 testes prova a qualidade de uma resposta do modelo real. O pipeline de LLM juiz de 52 avaliações depende de execução remota e revisão manual.

## Critério acadêmico de isolamento

A disciplina de Prompt and IA utiliza apenas o material fictício FC-01 a FC-07 para os **26 casos de documentos de Aurora**. O módulo Minha Energia é uma extensão separada do produto CitizenTech, não fonte suplementar para essas respostas. O fluxo escolhe a origem antes de qualquer consulta; não há RAG misturado entre as duas fontes.
