# Teste do Citizen Assist AI

| Integrante | RM |
| --- | --- |
| João Vitor Jun Nishiye de Sousa | 572079 |
| Davi Sinhorini Pacheco | 569487 |
| Gustavo Gamba Zancopé | 569287 |

## Condução do teste

A equipe realizou um teste de uso do assistente voltado a pessoas idosas. Antes de começar, avisou que as perguntas podiam abordar **aposentadoria, benefícios sociais, documentos, saúde e transporte**. Também avisou que corrigiria erros gramaticais quando necessário, preservando o sentido da pergunta.

O registro disponível descreve **12 casos de validação técnica** com perfis de pessoas idosas. As perguntas e as escolhas de menu foram enviadas automaticamente ao terminal para reproduzir os atendimentos. Os tempos e as notas da tabela pertencem a esse roteiro. Para documentar as sessões com pessoas exigidas pelo enunciado, é preciso confirmar quantas pessoas de fora da equipe participaram e registrar os indicadores medidos nessas sessões.

## Resultados registrados antes da melhoria

| Caso | Pergunta ou percurso no menu | ID esperado | Resultado observado |
| --- | --- | ---: | --- |
| C01 | “Onde tiro o novo RG, a identidade?” | 1 | ID 1, confiança alta (7 pontos) |
| C02 | “Como imprimir o comprovante de CPF?” | 2 | ID 2, confiança alta (7 pontos) |
| C03 | “Quero entrar no Conecte SUS.” | 3 | ID 3, confiança média (3 pontos) |
| C04 | “Como vejo a carteira de vacinação?” | 4 | ID 4, confiança alta (6 pontos) |
| C05 | “Tem passe para viajar de um estado para outro?” → “Como peço a carteira do idoso para viagem interestadual?” | 5 | Primeira tentativa sem resultado. ID 5 na segunda, confiança alta (8 pontos) |
| C06 | Transporte → Credencial digital de estacionamento para pessoa idosa | 6 | ID 6, aberto por categoria |
| C07 | “Posso me aposentar por idade?” | 7 | ID 7, confiança média (4 pontos) |
| C08 | “Preciso ver quanto caiu na conta.” → “Onde pego o contracheque do INSS?” | 8 | Primeira tentativa sem resultado. ID 8 na segunda, confiança média (4 pontos) |
| C09 | Benefícios sociais → Fazer ou atualizar o Cadastro Único | 9 | ID 9, aberto por categoria |
| C10 | “Como peço o BPC do idoso?” | 10 | ID 10, confiança média (3 pontos) |
| C11 | “Como vejo o histórico das minhas doses?” | 4 | Nenhuma orientação atingiu o limiar de 3 pontos. O ID 4 recebeu 0 ponto |
| C12 | “Como vejo o pagamento da minha aposentadoria?” | 8 | ID 7, confiança média (4 pontos). O ID 8 recebeu 1 ponto |

### Registros do roteiro técnico

| Caso | Avaliação de ajuda no roteiro | Tentativas | Tempo total (s) | Nota de facilidade simulada (1 a 5) |
| --- | --- | ---: | ---: | ---: |
| C01 | Sim | 1 | 18 | 5 |
| C02 | Sim | 1 | 31 | 4 |
| C03 | Sim | 1 | 27 | 4 |
| C04 | Sim | 1 | 32 | 5 |
| C05 | Sim | 2 | 64 | 3 |
| C06 | Sim | 1 | 38 | 4 |
| C07 | Sim | 1 | 35 | 4 |
| C08 | Sim | 2 | 72 | 3 |
| C09 | Sim | 1 | 45 | 4 |
| C10 | Sim | 1 | 34 | 4 |
| C11 | Não | 1 | 41 | 2 |
| C12 | Não | 1 | 48 | 2 |

### Indicadores do roteiro técnico

| Indicador | Cálculo | Resultado |
| --- | --- | ---: |
| Resposta encontrada | 11 orientações exibidas em 12 atendimentos, incluindo a orientação incorreta do C12 | 91,7% |
| Taxa de acerto (ajudou) | 10 avaliações “Sim” em 12 atendimentos avaliados no roteiro | 83,3% |
| Tentativas por atendimento | 14 buscas ou seleções ÷ 12 atendimentos | 1,2 |
| Tempo total médio | 485 segundos até concluir os 12 atendimentos ÷ 12 | 40,4 s |
| Tempo até a primeira orientação | Exige o intervalo entre a primeira tentativa válida e a primeira orientação encontrada. A tabela registra o tempo total | Sem medição separada |
| Facilidade de uso simulada | 44 pontos ÷ 12 notas do roteiro | 3,7 de 5 |

**Dúvidas sem solução.** C11 ficou sem orientação para o histórico de doses. Em C12, a palavra `aposentadoria` favoreceu a orientação para solicitar o benefício, embora a dúvida fosse sobre o extrato de pagamento. C05 e C08 foram resolvidos após uma reformulação no mesmo atendimento.

## Melhoria aplicada e reteste do C11

Na versão inicial, “Como vejo o histórico das minhas doses?” dava 0 ponto ao ID 4. A lista reconhecia expressões como `historico de vacinas`. Acrescentamos `historico das minhas doses` ao campo `palavras_chave` do ID 4 em `data/base_conhecimento.json`. A normalização remove o acento de “histórico”, a expressão completa passa a corresponder à consulta e soma **3 pontos**.

No reteste pelo terminal, repetimos a mesma pergunta depois de incluir a expressão e selecionar **3. Recarregar base**.

| Versão | Pontos do ID 4 | Resultado no terminal |
| --- | ---: | --- |
| Antes | 0 | “Não encontrei uma orientação.” |
| Depois | 3 | **Consultar vacinas no Meu SUS Digital (ID 4)** em primeiro lugar, com **confiança média** |

## Como reproduzir

1. Na pasta do projeto, execute `python main.py --terminal`. Escolha **1. Fazer uma pergunta** e digite **“Como vejo o histórico das minhas doses?”**.
2. Confira a orientação de vacinação, a confiança média, a fonte e o aviso sobre o canal oficial. Em seguida, pressione `0` para pular a avaliação de ajuda e `0` na consulta para voltar ao menu.
3. Para demonstrar a falha anterior, use outra cópia do projeto e retire apenas a linha `"historico das minhas doses",` do ID 4. Repita a consulta, volte ao menu, reinsira a linha e selecione **3. Recarregar base**. Repita a consulta com a expressão já restaurada.
4. Use **4. Ver indicadores** e **5. Exportar CSV** para conferir os atendimentos gerados na execução atual. As tabelas acima preservam os números da reprodução anterior à correção. O reteste técnico verifica se o assistente encontra o ID 4.
