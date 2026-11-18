# Justificativas — Módulo Minha Energia

Custo, viabilidade e impacto ambiental das três ferramentas do módulo, e por que o projeto foi modelado assim.

## Por que este problema

Famílias de baixa e média-baixa renda em São Paulo têm direito a descontos (Tarifa Social, Desconto Social) que dependem de um cadastro (CadÚnico) que precisa ser mantido atualizado — e a perda do desconto costuma ser percebida só quando a conta já chegou mais cara. O módulo não substitui a distribuidora nem o CRAS: ele existe para que a pessoa saiba, em reais por mês, o que está em jogo antes de agir.

## 1. Guardião do benefício (`verificar_beneficio_energia`)

**Custo:** nenhum — usa só os dados que a pessoa já tem na fatura e as respostas que dá sobre o CadÚnico.

**Viabilidade:** alta. As regras de manutenção do benefício (CadÚnico atualizado, mesmo município, titularidade) vêm diretamente da página da Enel SP e da ANEEL; o cálculo do valor em risco usa a diferença entre a tarifa com benefício e a tarifa Residencial cheia, então é direto de auditar.

**Limite:** o cruzamento automático com o CadÚnico é roadmap — hoje a ferramenta confia nas respostas que a pessoa dá (sim/não), não consulta nenhum cadastro de verdade. Por isso a ferramenta fala em **risco**, nunca em perda confirmada do benefício.

## 2. Simulador de alternativas (`comparar_alternativas_energia`)

### Eficiência energética (troca de equipamento)

**Custo:** o da própria troca, informado pela pessoa (ex.: R$ 2.000 por um equipamento mais eficiente).

**Viabilidade:** depende de onde a família está na curva da tarifa. Dentro da franquia gratuita da Tarifa Social (até 80 kWh), reduzir consumo não reduz a conta — a ferramenta mostra isso explicitamente (economia R$ 0,00) em vez de incentivar uma troca que não compensa. Acima da franquia, a economia é proporcional aos kWh que deixam de ser cobrados, já com os tributos aplicados.

**Retorno:** calculado em meses (investimento ÷ economia mensal); quando a economia é zero ou negativa, o campo de retorno vem vazio (`null`) em vez de um número sem sentido.

### Energia solar fotovoltaica

**Custo:** dimensionado pelos kWh efetivamente pagos (não pelo consumo bruto) — uma família com Tarifa Social que consome 80 kWh/mês não precisa, e o módulo não recomenda, nenhum sistema. Preço por kWp (R$ 2,45/Wp) de fonte de mercado (Solfácil/Cenário Energia).

**Viabilidade:** mais lenta para retornar que a eficiência, mas o potencial de economia é maior para quem já ultrapassa a franquia. Exige telhado adequado, sem sombra, e imóvel próprio ou geração compartilhada — a ferramenta não verifica nenhuma dessas condições físicas, só o retorno financeiro.

**Por que o cálculo é conservador:** toda a energia solar gerada é tratada como se passasse pela rede e pagasse o Fio B (60% não compensado em 2026, regra GD II), mesmo a parcela que teoricamente ficaria dentro da franquia gratuita — isso subestima a economia em vez de supor o cenário mais favorável sem confirmação.

## 3. Alerta de bandeira (`impacto_bandeira_energia`)

**Custo:** nenhum.

**Viabilidade:** o impacto por bandeira (verde/amarela/vermelha P1/P2) é calculado como a diferença de custo entre o cenário atual e cada bandeira, nos kWh efetivamente pagos — assim o impacto é proporcional ao consumo real da família, não um valor fixo igual para todos.

**Limite:** o módulo usa uma bandeira única por mês; faturas reais cobram o adicional proporcional aos dias de cada bandeira dentro do ciclo de faturamento (confirmado numa fatura real), então o valor de um mês com troca de bandeira no meio do ciclo pode diferir um pouco do que a ferramenta mostra.

## Impacto ambiental

O CO2 evitado é calculado por dois métodos, lado a lado, porque a escolha muda o resultado em ordem de grandeza:
- **Fator médio do SIN** (0,0461 kgCO2/kWh) — o que de fato deixou de ser emitido, em média, pela matriz brasileira (bastante limpa, por ser majoritariamente hídrica).
- **Margem de operação** (0,4368 kgCO2/kWh) — o que a usina marginal (termelétrica, acionada por último) deixaria de emitir; é o método recomendado para medir o impacto real de uma ação pontual de redução de consumo, e por isso é bem maior.

O módulo mostra os dois e deixa explícito qual é qual, em vez de escolher um só e esconder a diferença.

## Por que as decisões conservadoras

Em pelo menos dois pontos o grupo teve que escolher entre uma hipótese não verificada e uma simplificação:
- **ICMS entre 91 e 200 kWh:** a Enel SP lista 12% nessa faixa, mas não há fatura real nem fonte aberta que confirme se a alíquota de 18% listada para faturas maiores incide sobre o consumo inteiro ou só sobre o excedente. O módulo optou por aplicar 18% para todo o consumo acima de 90 kWh — superestimando o imposto, e portanto subestimando a economia das alternativas, em vez de supor a hipótese mais favorável sem prova.
- **Fio B na energia solar:** tratado como incidente sobre toda a geração compensada, mesmo a parcela que teoricamente estaria dentro da franquia gratuita da Tarifa Social — de novo, a simplificação reduz a economia estimada em vez de infla-la.

Essa escolha metodológica (na dúvida, superestimar custo e subestimar benefício) está documentada nos comentários de `calculos.py`, nas notas do `parametros.json` e é repetida nos avisos que cada ferramenta devolve ao chatbot — para que o usuário final também veja a ressalva, não só quem lê o código.
