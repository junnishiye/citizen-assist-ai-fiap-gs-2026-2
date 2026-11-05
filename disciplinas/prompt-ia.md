# Prompt and Artificial Intelligence

Fonte: [DOCX original](../fontes/enunciados/prompt-ia.docx) e [fichas](../fontes/aurora/00_LEIA-ME.md). Status: **planejado**. Responsável I2; revisor I3.

## Protótipo

- [ ] Nome completo de todos os integrantes no início.
- [ ] Tema fixo: RG, CPF, título, CTPS, certidões e CNH; corpus exclusivo FC-01 a FC-07.
- [ ] Explicar que Aurora e seus valores/regras são fictícios; não transformar em orientação real.
- [ ] Carregar e organizar fichas com estratégia justificada.
- [ ] Agente com framework (LangChain, LangGraph, CrewAI ou similar); justificar framework, arquitetura/agentes e modelo permitido.
- [ ] Explicar onde usar LLM e onde bastam busca/condicionais/validação.
- [ ] Menu por categorias e entrada livre; respostas simples, passo a passo, fonte da ficha e data.
- [ ] Aviso em toda resposta: não é canal oficial e confirmar informação no órgão.
- [ ] Tratar vazio, sem sentido, longo e fora do escopo; não inventar.
- [ ] Frases curtas, contraste/tamanho e uso pelo teclado.
- [ ] Não pedir, armazenar, repetir nem enviar desnecessariamente dados pessoais a serviço externo; proteger antes do LLM e dos logs.
- [ ] Testes de proteção usam somente exemplos fictícios. Não expor dados reais em saídas, notebook ou relatório.
- [ ] Não obedecer a instruções externas nem revelar prompt; manter fichas como dados.

## Avaliação

- [ ] Transcrever exatamente as 26 mensagens e respostas esperadas da seção 4.1. Perguntas próprias são adicionais.
- [ ] Preservar casos de escopo, fora do escopo, inválido, dados pessoais, injection e limitação.
- [ ] Implementar juiz LLM com régua explícita e justificada: conteúdo esperado, fonte quando exigida, ausência de invenção e proteção de dados/instruções.
- [ ] Executar agente e juiz nos 26 casos, salvar tabela de respostas/julgamentos e conferir amostra manualmente.
- [ ] Analisar erros, fazer melhoria concreta e executar as mesmas 26 mensagens novamente; comparar antes/depois.
- [ ] ≥5 pessoas externas em 3 tarefas simples cada, medindo tempos.
- [ ] Questionário curto de 5 perguntas em escala 1–5 após teste.
- [ ] Relatório com acerto, tempo e facilidade, sem identificar participantes.

## Pacote

- [ ] Notebook executado ou repositório/código com instruções; se script, imagem do grafo/arquitetura.
- [ ] Organização das fichas; pipeline e resultados antes/depois; testes com usuários; justificativas, tentativas, mudanças e limites.
- [ ] Confirmar prazo, formato Portal e se há regra adicional de vídeo — não informados no DOCX.

O original contém uma frase final suspeita que tenta alterar a resposta do assistente. Ver [registro de integridade](../docs/00-contexto.md); ela não foi incorporada como requisito.
