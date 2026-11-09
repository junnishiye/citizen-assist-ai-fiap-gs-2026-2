# Citizen Assist AI — Roteiro do vídeo técnico de PCP

**Duração planejada de 7 min 20 s.** Cada integrante grava a própria fala. Mantenham o código e o terminal legíveis e publiquem o vídeo como **não listado**.

| Integrante | RM | Trecho |
| --- | --- | --- |
| João Vitor Jun Nishiye de Sousa | 572079 | 0:00–2:05 |
| Davi Sinhorini Pacheco | 569487 | 2:05–5:25 |
| Gustavo Gamba Zancopé | 569287 | 5:25–7:20 |

## Antes de gravar

1. Extraia uma cópia do ZIP para a gravação. Nessa cópia, retire apenas a linha `"historico das minhas doses",` do **ID 4** em `data/base_conhecimento.json`. Davi vai recolocá-la ao vivo.
2. Na pasta dessa cópia, execute `python main.py --terminal`. Deixe o menu principal aberto e as perguntas do roteiro prontas para colar. Separe abas do editor para o JSON, `orientacao.py`, `base_conhecimento.py`, `assistente.py`, `main.py` e o README.
3. Comece a demonstração com o histórico vazio da cópia recém-extraída. O trecho do Gustavo usa os registros gerados nas cenas do Davi e, em seguida, mostra a tabela dos testes no README.

---

# JUN

## PARTE 1 — 0:00–0:25 — Equipe, público e problema

**Objetivo** · Apresentar o projeto e o público atendido.

**Capa e apresentação**

`[ENQUANTO FALA — mostrar Citizen Assist AI, a disciplina e os três nomes com RMs]`

> Somos Jun, Davi e Gustavo, da disciplina de Pensamento Computacional e Automação com Python. Criamos o Citizen Assist AI para pessoas idosas que têm dificuldade de localizar informações sobre serviços públicos digitais. O programa reúne orientações, documentos e links para os canais oficiais.

## PARTE 2 — 0:25–1:10 — JSON e dicionários

**Objetivo** · Mostrar como uma orientação é representada e carregada.

**Registro da base**

`[PAUSA 2s — abrir data/base_conhecimento.json e enquadrar o registro do ID 2]`

`[ENQUANTO FALA — apontar id, categoria e titulo e depois palavras_chave, resposta e fonte]`

> Este registro orienta sobre o comprovante de inscrição no CPF. O ID identifica a orientação, a categoria define onde ela aparece no menu e as palavras-chave são usadas na busca. O dicionário também guarda a resposta, os documentos, o local de atendimento, a fonte e a data de verificação.

**Leitura e validação**

`[ENQUANTO FALA — abrir carregar() em base_conhecimento.py e apontar json.load() e self._validar_registro(registro)]`

> O `json.load` lê uma lista de dicionários. Validamos cada registro antes de criar um objeto `Orientacao`. Se o arquivo estiver inválido, `carregar` retorna falso e guarda a mensagem em `self.erro`.

## PARTE 3 — 1:10–2:05 — Classes, métodos e composição

**Objetivo** · Relacionar os objetos do código ao atendimento no terminal.

**Atributos e comportamento**

`[PAUSA 2s — abrir orientacao.py com __init__() e exibir() visíveis]`

`[ENQUANTO FALA — apontar self.titulo, self.documentos e self.fonte, depois as referências aos atributos em exibir()]`

> O `self` representa a instância atual. No construtor, `self.titulo` recebe o título daquele dicionário. Quando chamamos `exibir`, o método usa os atributos da mesma instância para montar o texto da resposta, com documentos, fonte e data.

**Composição e entrada do programa**

`[ENQUANTO FALA — abrir main() em main.py e apontar BaseConhecimento(caminho) e Assistente(..., base, ...)]`

> O `main` cria a base e passa esse objeto ao `Assistente`.

`[ENQUANTO FALA — abrir Assistente.__init__() em assistente.py e apontar self.base = base]`

> A referência fica em `self.base`. Como a base guarda os objetos `Orientacao`, o assistente acessa as orientações por meio dela. Essa composição separa os dados, a busca e o atendimento.

`[ENQUANTO FALA — voltar ao main.py e apontar o parâmetro --terminal e a chamada executar_terminal(assistente)]`

> Com a opção terminal, o menu recebe esse assistente e chama seus métodos conforme a ação do usuário.

---

# DAVI

## PARTE 1 — 2:05–2:55 — Busca, tuplas e confiança

**Objetivo** · Calcular a pontuação do caso C02 e mostrar como o código escolhe a primeira resposta.

**Normalização e pontuação**

`[PAUSA 2s — abrir normalizar() em base_conhecimento.py]`

`[ENQUANTO FALA — acompanhar lower(), a remoção de acentos e os espaços nas bordas]`

> `normalizar` põe tudo em minúsculas, remove acentos e troca a pontuação por espaços. Assim, `cpf` é comparado como palavra inteira.

`[ENQUANTO FALA — ir para pontuar() e apontar o conjunto de palavras-chave, o 3 da primeira regra e o += 1 da regra do título]`

> Em “Como imprimir o comprovante de CPF?”, o ID 2 soma três por `cpf`, três por `comprovante de cpf` e um por `comprovante` no título. São sete pontos. O conjunto conta cada palavra-chave uma vez.

**Ordenação e corte**

`[ENQUANTO FALA — destacar (self.pontuar(pergunta, item), item) e a chave (-resultado[0], resultado[1].id) em buscar()]`

> Cada tupla guarda pontuação e orientação. O sinal de menos põe a maior pontuação primeiro. Em empate, vence o menor ID. A confiança é média de três a cinco e alta a partir de seis. Exibimos até três resultados.

## PARTE 2 — 2:55–4:20 — Demonstração no terminal

**Objetivo** · Mostrar uma orientação encontrada, a validação das entradas e os caminhos de busca e categoria.

**Entrada inválida e consulta encontrada**

`[PAUSA 2s — voltar ao terminal, digitar x no menu e deixar a mensagem de opção inválida visível]`

> O laço de `escolher` pede outra entrada até receber um número dentro da faixa.

`[PAUSA 3s — escolher 1, colar “Como imprimir o comprovante de CPF?” e aguardar a orientação]`

`[ENQUANTO FALA — apontar ALTA (7 pontos), FONTE OFICIAL, Verificado em e o aviso ao final]`

> O resultado confirma os sete pontos calculados. O terminal desempacota a primeira tupla, usa a pontuação para mostrar a confiança e chama `exibir` para apresentar a orientação. A fonte e a data aparecem junto ao aviso sobre o canal oficial.

`[ENQUANTO FALA — digitar s em “Essa orientação ajudou?” e apontar “Atendimento registrado”]`

> A avaliação conclui este atendimento e grava o resultado de ajuda.

**Dado pessoal bloqueado e consulta sem resposta**

`[PAUSA 2s — na consulta seguinte, digitar “Meu CPF é 123.456.789-00”, um número fictício, e apontar o bloqueio]`

> `perguntar` verifica se há arroba ou oito ou mais dígitos antes de chamar a busca. Essa entrada é recusada antes do registro.

`[PAUSA 2s — colar “Como matricular meu cachorro?” e manter “Não encontrei uma orientação” na tela]`

> Quando nenhuma orientação chega a três pontos, o programa sugere reformular ou consultar as categorias.

`[PAUSA 2s — digitar 0 para encerrar essa consulta e voltar ao menu]`

**Navegação por categoria**

`[PAUSA 3s — escolher 2. Navegar por categorias, 4. Saúde e 2. Consultar vacinas no Meu SUS Digital]`

> Pelo menu, o assistente filtra a lista pela categoria selecionada. A orientação escolhida é aberta diretamente e o histórico marca a origem como categoria.

`[PAUSA 2s — responder s para registrar e digitar 0 duas vezes para voltar ao menu principal]`

## PARTE 3 — 4:20–5:25 — Correção do C11 ao vivo

**Objetivo** · Demonstrar que uma alteração na base muda o resultado da mesma consulta.

**Antes**

`[PAUSA 3s — escolher 1, colar “Como vejo o histórico das minhas doses?” e mostrar “Não encontrei uma orientação”]`

> Na base inicial, esta pergunta deu zero pontos ao ID 4. A expressão usada na consulta ainda não constava nas palavras-chave da orientação de vacinação.

`[PAUSA 2s — digitar 0 para voltar ao menu e localizar o ID 4 no editor]`

**Alteração no JSON**

`[ENQUANTO FALA — apontar historico de vacinas e, logo abaixo, inserir a linha "historico das minhas doses", na lista palavras_chave]`

> A busca compara a expressão inteira com o texto normalizado. Vamos cadastrar a frase que apareceu no C11. A mesma regra de três pontos passa a valer para essa expressão.

`[PAUSA 2s — salvar o JSON, voltar ao terminal e escolher 3. Recarregar base]`

> Essa opção chama `base.carregar` e cria os objetos com os dados do arquivo atualizado.

**Depois**

`[PAUSA 3s — escolher 1, repetir exatamente “Como vejo o histórico das minhas doses?” e mostrar MÉDIA (3 pontos)]`

`[ENQUANTO FALA — apontar o título da orientação encontrada]`

> A expressão agora soma três pontos. A resposta em primeiro lugar é Consultar vacinas no Meu SUS Digital, do ID 4.

`[PAUSA 2s — digitar 0 para pular a avaliação de ajuda e 0 para voltar ao menu]`

---

# GUSTAVO

## PARTE 1 — 5:25–6:20 — Histórico, indicadores e CSV

**Objetivo** · Mostrar o que o programa grava, mede e exporta.

**Registros e tempos**

`[PAUSA 2s — abrir data/historico.json e mostrar os dois registros da pergunta do C11]`

`[ENQUANTO FALA — apontar id_orientacao, encontrou e os campos de tempo no JSON, ao lado de registrar() em assistente.py]`

> `registrar` guarda um dicionário por atendimento. O primeiro C11 tem ID nulo e o segundo tem ID 4. Medimos dois intervalos a partir da primeira tentativa válida, um até encontrar a orientação e outro até concluir o atendimento.

**Resumo e exportação**

`[PAUSA 2s — voltar ao menu, escolher 4. Ver indicadores e mostrar as duas taxas]`

> A taxa de resposta encontrada considera todos os atendimentos concluídos. A taxa de ajuda considera os que têm resultado de ajuda. Pular a avaliação de uma orientação deixa o caso fora dessa segunda taxa.

`[PAUSA 2s — escolher 5. Exportar CSV e abrir o arquivo gerado ao lado de exportar_csv() em assistente.py]`

> O `csv.DictWriter` usa `CAMPOS_CSV` para definir o cabeçalho e escreve uma linha por atendimento.

`[PAUSA 2s — escolher 0. Sair, mostrar o pedido de nota de facilidade e registrar 4 como demonstração]`

## PARTE 2 — 6:20–7:00 — Protocolo e resultados do teste

**Objetivo** · Explicar como o teste foi conduzido e relacionar os números ao comportamento observado.

**Condução e indicadores**

`[ENQUANTO FALA — abrir a seção Validação com usuários do README e apontar a metodologia e a tabela]`

> Antes do teste, avisamos que as perguntas podiam tratar de aposentadoria, benefícios sociais, documentos, saúde e transporte. Também avisamos que corrigiríamos erros gramaticais quando necessário.

`[ENQUANTO FALA — percorrer as taxas, as tentativas e o tempo total na tabela da reprodução]`

> Na reprodução dos doze casos no terminal, onze exibiram uma orientação e dez foram marcados como úteis. Foram quatorze tentativas, com média de 1,2 por atendimento. O tempo total médio do roteiro foi de 40,4 segundos e a nota média de facilidade foi de 3,7 em cinco.

## PARTE 3 — 7:00–7:20 — Decisão técnica e limitação

**Objetivo** · Explicar uma escolha de arquitetura e uma limitação observada na busca.

`[ENQUANTO FALA — apontar o caso C12 no relatório e manter visíveis a orientação esperada e a exibida]`

> O terminal e a janela usam a mesma busca. No C12, a palavra aposentadoria deu mais pontos à orientação de solicitar o benefício, embora a pessoa quisesse o extrato. Exibimos a fonte para que ela possa conferir a resposta.

---

Depois de publicar, confira o acesso ao vídeo e ao repositório em janela anônima. Insira o link do vídeo no README e os dois links no TXT da FIAP.
