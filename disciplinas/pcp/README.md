# Citizen Assist AI | Global Solution 2026.2 de PCP

Protótipo acadêmico para orientar **pessoas idosas com dificuldade de usar serviços públicos digitais no Brasil**. O problema é encontrar, em páginas diferentes, os documentos, os passos e o canal oficial de atendimento. O assistente reúne dez orientações sobre documentos, saúde, transporte, aposentadoria e benefícios sociais.

A proposta se relaciona ao [ODS 10 — Redução das Desigualdades](https://brasil.un.org/pt-br/sdgs/10), ao facilitar o acesso de pessoas com menor familiaridade digital, e ao [ODS 16 — Paz, Justiça e Instituições Eficazes](https://brasil.un.org/pt-br/sdgs/16), pelo acesso a informações públicas e a indicação das fontes.

## Integrantes

| Integrante | Nome completo | RM |
| --- | --- | --- |
| 1 | João Vitor Jun Nishiye de Sousa | 572079 |
| 2 | Davi Sinhorini Pacheco | 569487 |
| 3 | Gustavo Gamba Zancopé | 569287 |

## Como executar

Abra a pasta `disciplinas/pcp` do repositório e rode com Python 3.10 ou mais recente:

```bash
python main.py
```

Em Linux, use `python3` se esse for o comando do seu sistema. A janela abre quando Tkinter e a sessão gráfica estiverem disponíveis. Em outros ambientes o mesmo comando abre o menu no terminal. Para escolher o terminal diretamente, use `python main.py --terminal`. No Debian ou Ubuntu, a janela pode ser habilitada instalando `python3-tk` pelo gerenciador de pacotes do sistema.

Comece com **“Como consultar minhas vacinas?”** ou abra uma orientação pela categoria **Saúde**. A resposta mostra os passos, documentos, onde buscar atendimento, fonte oficial, data de verificação e o aviso sobre o caráter acadêmico do assistente. Na janela, clique em **Meu SUS Digital** no texto ou em **Abrir fonte oficial**. No terminal, os endereços aparecem junto da orientação.

Depois de ler, responda **Sim**, **Não** ou **Pular**. Na ausência de resultado, reformule ou encerre sem resposta. O menu oferece **Indicadores** (opção 4) e **Exportar CSV** (opção 5). Ao sair, dê uma nota de facilidade de 1 a 5 ou pule a avaliação.

## Organização do código

| Arquivo | Responsabilidade |
| --- | --- |
| `main.py` | Carrega a base, cria o assistente e inicia a janela ou o terminal |
| `orientacao.py` | `Orientacao` guarda os dados de um serviço e prepara o texto exibido |
| `base_conhecimento.py` | `BaseConhecimento` lê o JSON, valida registros, lista categorias e ordena resultados |
| `assistente.py` | `Assistente` valida consultas, registra atendimentos, calcula indicadores e exporta CSV |
| `interface.py` | Janela Tkinter e links clicáveis, usando a mesma busca do terminal |
| `data/` | Base com fontes oficiais, histórico e CSV. A nota de saída gera `avaliacoes.json` |

Por composição, o objeto `Assistente` possui uma `BaseConhecimento`, que guarda uma lista de objetos `Orientacao`. Cada orientação vem de um dicionário do JSON. `buscar()` retorna uma lista de tuplas `(pontos, orientacao)`.

## Pontuação da busca

A comparação usa minúsculas, sem acentos e sem pontuação. Cada palavra-chave distinta encontrada vale **3 pontos**. Cada palavra distinta da pergunta com pelo menos quatro caracteres presente no título vale **1 ponto**. A confiança é **alta** a partir de 6 pontos e **média** de 3 a 5. A busca abaixo de 3 sugere reformular ou navegar por categorias. Mostramos até três resultados elegíveis, com desempate pelo menor ID.

Exemplo com a base incluída. A pergunta **“Como imprimir o comprovante de CPF?”** soma 3 por `cpf`, 3 por `comprovante de cpf` e 1 por `comprovante` no título. A orientação de ID 2 recebe **7 pontos**.

## Histórico, indicadores e CSV

`data/historico.json` guarda data, origem, última pergunta, ID da orientação, resultado, avaliação, número de tentativas e tempo. O histórico recebe o registro quando o atendimento é concluído. Ao navegar por categoria, o campo de pergunta fica vazio. A validação barra perguntas com arroba ou oito ou mais dígitos antes do registro. Oriente os participantes a usar dúvidas genéricas, sem nomes ou dados pessoais.

| Indicador | Cálculo |
| --- | --- |
| Resposta encontrada | Percentual dos atendimentos concluídos que exibiram uma orientação |
| Taxa de acerto (ajudou) | Percentual de respostas que ajudaram entre os atendimentos com resultado de ajuda. Encerrar sem resposta conta como “Não”. Avaliações puladas ficam fora do cálculo |
| Tempo médio para encontrar | Média do tempo entre a primeira tentativa e a primeira orientação encontrada. O tempo total, até encerrar, também é salvo |
| Tentativas por atendimento | Média de buscas válidas e trocas de orientação dentro dos atendimentos concluídos |
| Facilidade de uso | Média das notas registradas na saída, de 1 a 5 |
| Dúvidas sem solução | Consultas encerradas sem orientação ou com avaliação “Não”, sem duplicar a lista exibida |

O botão de exportação atualiza `data/atendimentos.csv` usando `csv.DictWriter`. O histórico incluído tem três atendimentos registrados. O CSV contém o cabeçalho até a próxima exportação. Os números surgem a partir das sessões realizadas.

## Validação com usuários

Antes de começar o teste, informamos que as perguntas podiam tratar de **aposentadoria, benefícios sociais, documentos, saúde e transporte**. Também avisamos que corrigiríamos erros gramaticais quando necessário, preservando o sentido da pergunta.

O [relatório de teste](docs/TESTE_COM_USUARIOS.md) registra **12 casos reproduzidos no terminal**. Os resultados abaixo descrevem essa reprodução com a base anterior à melhoria.

| Indicador | Resultado da reprodução |
| --- | --- |
| Resposta encontrada | 91,7% (11 de 12, incluindo a resposta incorreta do C12) |
| Taxa de acerto (ajudou) | 83,3% (10 de 12 avaliações do roteiro) |
| Tentativas por atendimento | 1,2 (14 tentativas em 12 atendimentos) |
| Tempo total médio | 40,4 s, incluindo a leitura e a conclusão do atendimento |
| Tempo até a primeira orientação | Sem medição separada no relatório |
| Facilidade de uso | 3,7 de 5 (12 notas simuladas no roteiro) |

**Dúvidas sem solução na base anterior.** Em C11, “Como vejo o histórico das minhas doses?” ficou sem orientação. Em C12, “Como vejo o pagamento da minha aposentadoria?” trouxe a orientação para solicitar aposentadoria (ID 7), embora a consulta fosse sobre o extrato de pagamento (ID 8).

**Melhoria aplicada e verificada.** Acrescentamos `historico das minhas doses` a `palavras_chave` do ID 4 em `data/base_conhecimento.json`. No reteste pelo terminal, C11 passou de 0 pontos e nenhuma orientação para **ID 4 em primeiro lugar, com 3 pontos e confiança média**. Os indicadores da tabela referem-se à rodada anterior à correção.

**Comprovação do teste com pessoas.** O enunciado pede ao menos 3 pessoas externas à equipe e 10 atendimentos. Para documentar as sessões relatadas pela equipe, é preciso informar o total de pessoas externas e identificar os indicadores medidos com elas.

**Conferência técnica.** Execute `python -m unittest discover -s tests -v` para verificar busca, entrada inválida, bloqueio de dados, links, histórico, indicadores e CSV. No computador com interface gráfica, teste também a seleção de categorias, o clique em um link, a avaliação e os botões de indicadores e exportação.

## Limitações e integração

A pontuação mede correspondência de texto. Sinônimos ausentes podem produzir zero resultados e uma pontuação alta ainda pede leitura da fonte. O atendimento real, as regras atualizadas e eventuais solicitações ficam nos canais oficiais. O protótipo usa a base local e opera sem login. A base pode ser reutilizada em DSA, cujo trabalho implementa suas próprias estruturas e algoritmos.

## Fontes consultadas

O campo `fonte` do JSON guarda o endereço de cada serviço. A data registrada na base é **06/11/2026**.

| ID | Orientação e fonte |
| --- | --- |
| 1 | [Carteira de Identidade Nacional](https://www.gov.br/governodigital/pt-br/identidade/cin/duvidas-frequentes-sobre-a-cin-campanha) |
| 2 | [Comprovante de inscrição no CPF](https://www.gov.br/pt-br/servicos/obter-cartao-de-cpf) |
| 3 | [Meu SUS Digital](https://www.gov.br/saude/pt-br/composicao/seidigi/meususdigital) |
| 4 | [Consulta de vacinas no Meu SUS Digital](https://www.gov.br/saude/pt-br/assuntos/noticias/2026/outubro/quer-consultar-suas-vacinas-saiba-como-acessar-a-carteira-de-vacinacao-pelo-meu-sus-digital/) |
| 5 | [Carteira da Pessoa Idosa](https://www.gov.br/pt-br/servicos/adquirir-carteira-do-idoso) |
| 6 | [Credencial digital de estacionamento](https://www.gov.br/pt-br/servicos/emitir-credencial-de-estacionamento-digital) |
| 7 | [Aposentadoria por idade urbana](https://www.gov.br/pt-br/servicos/solicitar-aposentadoria-por-idade-trabalhador-urbano) |
| 8 | [Extrato de pagamento de benefício do INSS](https://www.gov.br/pt-br/servicos/emitir-extrato-de-pagamento-de-beneficio) |
| 9 | [Cadastro Único](https://www.gov.br/mds/pt-br/acoes-e-programas/cadastro-unico/Cadastro-unico/) |
| 10 | [BPC para pessoa idosa](https://www.gov.br/pt-br/servicos/solicitar-beneficio-assistencial-ao-idoso) |

## Vídeo técnico e envio

O [roteiro de 7 min 20 s](docs/ROTEIRO_VIDEO.md) divide as partes técnicas entre os três integrantes e mostra como demonstrar o antes e o depois da correção em uma cópia do projeto.

**Vídeo técnico no YouTube** · [inserir o link após publicar como não listado]

Publique o código em um repositório público e confira o acesso aos dois links em janela anônima. Preencha os links em [entrega_fiap.MODELO.txt](entrega_fiap.MODELO.txt). O enunciado pede somente o TXT no Portal FIAP, em **Entregas de Trabalho**, até **19/11 às 23h59**.
