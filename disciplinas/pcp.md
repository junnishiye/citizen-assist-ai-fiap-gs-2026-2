# Pensamento Computacional e Automação com Python

Fonte: [enunciado original](../fontes/enunciados/pcp.pdf), seções 2–15. Status: **planejado, não implementado**. Responsável sugerido I1; revisor I2.

## Critérios de aceite

- [ ] Escolher público/tema e ODS; definir problema.
- [ ] `data/base_conhecimento.json` com ≥10 orientações, ≥3 categorias, ≥3 palavras-chave por orientação.
- [ ] Campos em todos os registros: `id`, `categoria`, `titulo`, `palavras_chave`, `resposta`, `documentos`, `onde`, `fonte`, `verificado_em`.
- [ ] Fontes oficiais conferidas pela equipe, data real de verificação e linguagem simples.
- [ ] `Orientacao`: campos do registro e `exibir()`.
- [ ] `BaseConhecimento`: caminho, lista de objetos; carregar, listar categorias, filtrar, pontuar e buscar.
- [ ] `Assistente`: nome, base por composição e histórico; perguntar, navegar, registrar, indicadores e CSV.
- [ ] Quatro arquivos principais: `main.py`, `orientacao.py`, `base_conhecimento.py`, `assistente.py`; executar `python main.py` na pasta de entrega.
- [ ] Normalizar pergunta, título e palavras-chave: sem acento/pontuação e em minúsculas.
- [ ] +3 por palavra-chave encontrada; +1 por palavra da pergunta com ≥4 letras encontrada no título. Alta ≥6; média 3–5; abaixo de 3 não encontrou. Ajustes permitidos se justificados no README/vídeo.
- [ ] `buscar()` retorna lista de tuplas `(pontos, orientacao)` em ordem decrescente; exibir melhor e até duas alternativas.
- [ ] Menu por categorias e orientações numeradas, `0` para voltar; validar opção, texto vazio e s/n sem encerrar por erro.
- [ ] Recusar pergunta com ≥8 dígitos ou `@`, **antes de registrar**; não pedir nome, CPF, telefone ou e-mail.
- [ ] Toda resposta mostra fonte, data e aviso de que o assistente não é canal oficial.
- [ ] JSON ausente/corrompido recebe tratamento sem travamento.
- [ ] Histórico JSON: data, origem pergunta/categoria, pergunta, id da orientação, encontrou, ajudou, tentativas e tempo em segundos. Não armazenar entrada bloqueada.
- [ ] Cronometrar início/fim; solicitar facilidade 1–5 ao sair.
- [ ] Indicadores: encontrou %, ajudou %, tempo médio, tentativas, facilidade, dúvidas sem solução.
- [ ] Exportar `data/atendimentos.csv` com `csv.DictWriter`.
- [ ] ≥3 pessoas externas e ≥10 atendimentos; resultados reais, dúvidas sem solução e uma melhoria no README.
- [ ] README: nomes/RMs, público/problema, ODS, execução, pontuação, integrações, fontes, teste, limitações e vídeo.

## Vídeo e envio

- [ ] YouTube não listado, 5–8 minutos; todos falam; tela/código legíveis; sem voz sintética.
- [ ] Equipe/público/problema até 30 s; registro JSON e dicionários/tuplas; classes, `self` e composição; cálculo real de pontuação.
- [ ] Demonstrar encontrado, não encontrado, inválido, dado bloqueado e categoria.
- [ ] Alterar palavra-chave no JSON ao vivo e resolver pergunta antes não encontrada.
- [ ] Mostrar histórico, CSV, indicadores, decisão técnica e limitação.
- [ ] Repositório público acessível; extrair pacote com os arquivos no layout solicitado caso o repositório geral use subpasta.
- [ ] Enviar somente TXT no Portal até 19/11 às 23h59: nome do assistente, público, integrantes/RMs, GitHub e YouTube.

A busca por pontuação não é substituída por LLM. Reaproveitamento com DSA descrito em [integrações](../docs/02-integracoes.md).
