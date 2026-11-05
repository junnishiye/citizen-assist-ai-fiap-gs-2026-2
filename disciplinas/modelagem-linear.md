# Modelagem Linear para Aprendizado de Máquina

Fonte: [texto original](../fontes/enunciados/modelagem-linear.txt), itens 01–08. Status: **planejado**. Responsável I2, apoio I1 após núcleo Python, revisor I3.

## Base real

- [ ] Escolher base adequada ao CitizenTech e justificar; indicar procedência, variáveis, unidades e tratamento.
- [ ] Não usar dados artificiais/fictícios. Exemplos sugeridos no enunciado: IBGE, dados.gov.br, Google Dataset Search, Kaggle e awesome-public-datasets.
- [ ] Selecionar variáveis numéricas e alvo binário apropriados. Garantir dados suficientes para amostras n=20 e n=25 e para análises coerentes; não fabricar observações.
- [ ] Se forem usadas medições próprias de usuários, confirmar adequação/aceitação, volume e anonimização antes de depender dessa base. As 15 tarefas de usabilidade não bastam automaticamente.

## Questão 02 — Probabilidade (1 ponto)

- [ ] Sob hipótese Normal, escolher variável e calcular P(X < média dos registros), classificando evento.
- [ ] Calcular P(X > mediana dos registros) e classificar.

## Questão 03 — Hipóteses (1 ponto)

- [ ] Teste unilateral à esquerda: média amostral menor que referência populacional, α=6%, n=20, desvio de referência igual ao populacional dos dados.
- [ ] Teste unilateral à direita: média amostral maior que referência populacional, α=9%, n=25, mesmo critério de desvio.
- [ ] Registrar hipóteses, referência, obtenção das amostras, estatística, critério e interpretação; não manipular dados para forçar conclusão.

## Questão 04 — Bivariada (2 pontos)

- [ ] Duas quantitativas; dispersão com título/eixos e interpretação.
- [ ] Covariância e Pearson com interpretação; gráfico de correlação.
- [ ] Reta no gráfico, equação de regressão simples, R², teste F interpretado e previsão.

## Questão 05 — Multivariada linear (2 pontos)

- [ ] ≥3 quantitativas; dispersão interpretada; matrizes de covariância/Pearson e gráfico de correlação.
- [ ] Equação da regressão múltipla; R² e teste F interpretados.
- [ ] Previsão com ≥2 variáveis explicativas.

## Questão 06 — Logística (2 pontos)

- [ ] Análise com ≥3 variáveis quantitativas conforme enunciado, explicando como representar/obter o desfecho binário real.
- [ ] Equação da regressão logística binária.
- [ ] Matriz de confusão e acurácia interpretadas.
- [ ] Classificação com ≥2 explicativas.
- [ ] Documentar avaliação e evitar vazamento entre treino e teste quando houver separação; justificar escolhas metodológicas.

## Questões 07 e 08 — Relatório e envio

- [ ] Relatório estatístico com tabelas, gráficos, medidas, interpretações e insights úteis para cliente/empresa (2 pontos).
- [ ] Identificação completa/RM dos integrantes.
- [ ] Base em CSV ou XLSX, códigos obrigatoriamente PY e relatório obrigatoriamente PDF.
- [ ] Um representante envia **os arquivos diretamente no Portal**; links não substituem entregáveis.
- [ ] Conferir instruções trabalhadas em aula, prazo e recibo no Portal.

O pipeline de juiz de Prompt e IA pode inspirar indicadores, mas não substitui estas questões. Dados de Aurora e ônibus hipotéticos não são uma base real.
