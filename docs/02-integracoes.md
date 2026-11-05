# Integrações e reaproveitamento

## Relações reais entre as matérias

| Relação | Trabalho compartilhável | Exigência que continua própria |
|---|---|---|
| PCP + DSA | Modelo de orientação, menu, validações, busca por atributo, dados oficiais e documentação | PCP: busca por pontuação, classes/composição e lista de objetos, JSON/histórico/CSV e usuários. DSA: nós e lista encadeada explícita, CRUD, busca e ordenação implementadas e Big-O |
| Prompt e IA + PCP | Rotinas de interface, acessibilidade, barreira de dados pessoais e protocolo de teste | IA usa exclusivamente Aurora e framework/LLM; PCP exige base de fontes oficiais e busca por regras. Uma resposta de LLM não substitui a busca de PCP |
| Prompt e IA + Modelagem Linear | Pergunta de pesquisa, definição de indicadores, infraestrutura de medição e dados observacionais reais se adequados | Juiz LLM não substitui probabilidade, hipóteses e regressões. Os 26 casos fixos de avaliação não viram automaticamente uma base estatística suficiente |
| SERS + PCP/DSA | Categoria de energia com fontes verificadas, registros e consulta | Exige cálculos, comparação ≥2 alternativas, renovável, custos/impactos e testes específicos |
| SERS + COA | Possível medição/controle de consumo ou condição ambiental em Wokwi | Apenas proposta: definir componentes e problema. Simulação não equivale a coleta real; demonstrar lógica MicroPython e respostas do circuito |
| COA + assistente | Contexto do problema e eventual entrada de dados | Integração técnica não exigida; Pico não precisa rodar LLM nem conversar com gov.br |
| MMC + empresa | Contextualização como outro estudo de solução cidadã | Problema de ônibus é fixo e deve ser resolvido como pedido; não substituir por métricas do chatbot |

## Arquitetura sugerida para reduzir retrabalho

1. **Modelo comum de orientação**, com campos exigidos em PCP. DSA pode manipular os mesmos registros.
2. **Camada PCP em terminal**, mantendo `Orientacao`, `BaseConhecimento`, `Assistente`, composição e busca por pontos.
3. **Módulo DSA**, com `No` e `ListaEncadeada` próprios e operação explícita sobre essa lista. Não basta guardar dados numa lista nativa e chamá-la de encadeada.
4. **Modo IA Aurora separado**, com entrada e corpus próprios. Mostrar aviso de material didático fictício antes da consulta. Nunca pesquisar fichas fictícias na base oficial.
5. **Módulo de energia**, cujos resultados verificados alimentam orientações oficiais do assistente. Não inserir energia no agente de documentos de Aurora, cujo escopo é fixo.
6. **Análises estatística e matemática em pastas próprias**. Reaproveitar contexto e ferramentas somente quando os dados e critérios permitirem.

A estrutura interna ainda deve ser decidida. Uma opção segura é PCP manter a lista de objetos exigida e DSA usar a lista encadeada, trocando registros por um formato JSON comum. Se houver edição, definir fonte de persistência e recarga para evitar cópias divergentes. Se adotarem estrutura unificada, demonstrar como ela satisfaz ambos os enunciados.

## Três bases que não podem ser confundidas

| Base | Natureza | Uso permitido neste planejamento |
|---|---|---|
| `fontes/aurora/` | Fictícia e fixa | Agente e golden dataset de Prompt e IA |
| `app/data/base_conhecimento.json` (a criar) | Orientações verificadas em fontes oficiais | PCP; compartilhamento com DSA; energia validada |
| `estatistica/dados/` (a criar) | Base empírica real e documentada | Modelagem Linear; eventualmente apoiar decisões do PX |

Os números hipotéticos dos ônibus são válidos para MMC, mas não atendem à proibição de dados fictícios de Modelagem Linear. Dados estimados e justificados podem atender a SERS, mas isso também não os torna aceitos em Modelagem Linear.

## Uma rodada de usuários, evidências separadas

Proposta: recrutar pelo menos 5 pessoas externas, com 3 tarefas cada **no agente de IA**, questionário de 5 itens e tempos. Acrescentar ≥10 atendimentos **no programa PCP**, envolvendo ≥3 dessas pessoas. Incluir tarefas de energia e registrar compreensão, comentários e ajustes. As mesmas pessoas podem participar, mas executar os fluxos de fato e distinguir produto/modo/tarefa. Não contar automaticamente as mesmas 15 execuções para todas as matérias.

## Vídeos

Reaproveitar captura de tela e preparação. Exportar cortes específicos: PCP 5–8 min com roteiro completo; SERS ≤3 min; COA com circuito em ação. Pitch é outra finalidade e ainda não tem enunciado próprio recebido. Não presumir que um vídeo único atenderá a tudo.
