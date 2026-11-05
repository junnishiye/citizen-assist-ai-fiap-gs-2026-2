# Plano sugerido para três integrantes

Distribuição provisória por frentes, sem atribuir nomes ainda não informados. Todos participam do desenvolvimento e entendem a entrega final. Ajustar após o grupo informar disponibilidade e afinidade.

| Pessoa | Responsabilidade principal | Responsabilidade secundária | Revisor |
|---|---|---|---|
| I1 | Assistente PCP e módulo DSA | Integração, execução limpa e documentação técnica | I2 |
| I2 | Agente de Prompt e IA, juiz e validação | Análise estatística de Modelagem Linear | I3 |
| I3 | SERS e protótipo COA | Modelagem Matemática e organização das evidências | I1 |

I2 e I3 acumulam análises substanciais: após o núcleo PCP/DSA funcionar, I1 apoia uma dessas frentes. Não deixar estatística ou MMC para o fim. Computer Science fica sem responsável até chegar o enunciado e redistribuir a carga.

## Etapa 0 — Fechar organização

- [ ] Preencher os três nomes completos, RMs e GitHubs.
- [ ] Conferir todos os prazos e formatos no Portal.
- [ ] Confirmar se há continuação/instruções de entrega de MMC.
- [ ] Confirmar público de PCP/SERS e caso de uso COA.
- [ ] Nomear responsável e revisor das tarefas.

**Saída:** decisões registradas, sem hipóteses apresentadas como consenso.

## Etapa 1 — Contratos e bases, em paralelo

- I1: definir modelo, contrato JSON e fluxo PCP/DSA; pesquisar ≥10 orientações oficiais em ≥3 categorias.
- I2: conferir preservação das fichas; transcrever fielmente os 26 casos e respostas esperadas; propor framework/modelo.
- I3: propor necessidade energética e duas alternativas; planejar componentes Wokwi; iniciar formulação dos ônibus.
- I2 + I3: escolher base real de estatística com variáveis que permitam hipóteses, regressões e classificação binária.

**Dependências:** nenhuma pesquisa fictícia de Aurora poderá alimentar as orientações oficiais. Seleção da base estatística acontece antes das regressões.

## Etapa 2 — Protótipos mínimos avaliáveis

- I1: classes, busca por pontos, navegação e bloqueio de dados; lista encadeada/CRUD/busca/ordenação/Big-O.
- I2: agente com framework, fontes/data/avisos; primeiro ciclo de juiz nas 26 mensagens.
- I3: cálculos SERS e simulação Pico com leitura/processamento/saída; solução Python da Etapa 1 de MMC.
- Trio: revisão cruzada e demonstração dos fluxos sem erros.

**Saída:** código testável em cada frente, ainda sem alegar validação com usuários.

## Etapa 3 — Análises e integração

- I1: histórico, métricas e CSV; incorporar resultados de energia verificados.
- I2: análise dos erros do agente, melhoria e segunda execução nos mesmos 26 casos; iniciar análise estatística completa.
- I3: justificar custos/impactos e limites; propor matriz de redistribuição; verificar conservação, não negatividade e inteiros.
- I1 apoia a frente com maior carga após estabilizar o assistente.

## Etapa 4 — Validação e correção

- Trio executa o protocolo em `validacao/README.md`.
- Guardar registros anônimos, resultados reais e mudanças observadas.
- Registrar melhoria PCP, melhoria do agente e ajustes de energia separadamente.
- I2 + revisor concluem regressões/relatório; I3 + revisor fecham demonstrações matemáticas e IoT.

## Etapa 5 — Vídeos e submissão

- Gravar PCP com os três explicando código, sem narração sintética e com alteração ao vivo.
- Gravar SERS e COA com seus próprios requisitos.
- Revisar arquivos, abrir links sem login e testar instalação/execução em ambiente limpo.
- Preencher `entregas/`, escolher representante e registrar o comprovante de cada envio.

## Fluxo no GitHub

Uma issue por resultado verificável, com responsável, revisor, disciplina(s), dependências e aceite. Branches como `feat/pcp-busca` e `docs/sers-comparacao`; pull request com evidências. Evitar duas pessoas editando a mesma base no mesmo momento. Antes de integrar, o revisor executa ou confere o artefato.

Estados sugeridos para um quadro: A fazer → Em andamento → Em revisão → Concluído. Isso é uma convenção sugerida; nenhum quadro remoto foi criado por este documento.
