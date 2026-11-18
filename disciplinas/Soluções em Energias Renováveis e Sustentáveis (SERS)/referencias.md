# Referências — Módulo Minha Energia (Soluções em Energias Renováveis)

Todas as fontes usadas em `parametros.json`, por parâmetro. Datas entre parênteses são de consulta/captura, não de publicação da norma.

## Tarifa e tributos

- **Tarifa Residencial (B1, R$ 0,78938/kWh) e Fio B (R$ 0,212077/kWh):** ANEEL, Resolução Homologatória 3.596/2026 (30/06/2026), Tabela 2 (B1 Residencial Convencional) e Tabela 4; vigência 04/07/2026 a 03/07/2027. Fio B confirmado também nos Dados Abertos da ANEEL, conjunto "Componentes Tarifárias" (TUSD_FioB, agente Eletropaulo/Enel SP, CNPJ 61695227000193, resource_id `e8717aa8-2521-453f-bf16-fbb9a16eea39`) — diferença de 0,02% em relação ao valor derivado da REH.
- **Tarifa Baixa Renda (R$ 0,61191/kWh) e franquia de 80 kWh da Tarifa Social:** mesma REH 3.596/2026, Tabela 2 (subclasse Baixa Renda) e Tabela 3; Lei 15.235/2025. Confirmado de forma independente nos Dados Abertos da ANEEL, "Tarifas de Aplicação", subclasses "Tarifa Social – faixa 01/02".
- **Tarifa Desconto Social (R$ 0,63366/kWh) e franquia de 120 kWh:** REH 3.596/2026, Tabela 2, nota (2); página da Enel SP, *Tarifa Social e Baixa Renda* (capturas do grupo, 11/11/2026) — cita REN ANEEL 1.147/2025 e Lei 15.235/2025.
- **Regras para manter o benefício** (CadÚnico atualizado há até 2 anos, titularidade, mesmo município): página da Enel SP acima e página da ANEEL, *Tarifa Social* (https://www.gov.br/aneel/pt-br/assuntos/tarifas/tarifa-social).
- **PIS/Cofins (5,45%, provisório):** fatura real da Enel SP (B1 Residencial, São Paulo capital, referência out/2026, cedida anonimizada pelo grupo em 13/11/2026): PIS 0,97% + Cofins 4,48%. Referência histórica: tabela mensal da Enel SP (média fev/2025–jan/2026 = 5,30%, faixa 4,40%–6,08%).
- **Isenção de ICMS até 90 kWh:** Lei estadual (SP) 12.185/2006, art. 1º; confirmado na mesma fatura real (Decreto 45.490/00, art. 29, inciso II, letra "a").
- **ICMS de 18% acima de 90 kWh (simplificação):** página "Impostos e Outros Encargos" da Enel SP (captura do grupo, 12/11/2026), que lista 12% de 91 a 200 kWh e 18% acima de 200 kWh. O módulo não modela a faixa de 12% por falta de fatura ou fonte que confirme a regra — ver `NOTAS_INTEGRACAO_ENERGIA.md` e a nota do próprio parâmetro no `parametros.json` para a justificativa dessa escolha conservadora.
- **Custo de disponibilidade:** ANEEL, Resolução Normativa 1.000/2021, art. 291.

## Bandeiras tarifárias

- **Bandeira vigente (verde, nov/2026):** Dados Abertos da ANEEL, conjunto "Bandeira tarifária – acionamento" (gerado 10/11/2026); confirmado por notícia da própria ANEEL (anúncio de 30/10/2026, amplamente divulgado, ex. SBT News).
- **Valores por bandeira (amarela R$ 0,01885/kWh; vermelha P1 R$ 0,04463/kWh; vermelha P2 R$ 0,07877/kWh):** Dados Abertos da ANEEL, conjunto "Bandeira tarifária – adicional" (gerado 15/07/2026), REH 3.306/2024, vigente desde 01/04/2024.

## Energia solar

- **Fio B não compensado (60% em 2026):** Lei 14.300/2022, art. 27 (cronograma GD II: 15% em 2023, 30% em 2024, 45% em 2025, 60% em 2026); conferido em fonte secundária (canalsolar.com.br) por o texto legal não ter sido consultado diretamente.
- **HSP (irradiação, 4.657,25 kWh/m²/dia médio anual):** arquivo `tilted_latitude_means_SP.csv` fornecido pelo grupo, média dos 4 pontos de grade mais próximos do centro de São Paulo. Citação oficial do Atlas Solarimétrico a confirmar.
- **Taxa de desempenho (70%–80%):** trecho de manual de engenharia fotovoltaica fornecido pelo grupo, provavelmente CRESESB/CEPEL, *Manual de Engenharia para Sistemas Fotovoltaicos* (Pinho e Galdino, 2014), cap. 6 — título, autores, ano e página a confirmar antes de citar formalmente.
- **Custo por kWp instalado (R$ 2,45/Wp):** Radar Solfácil via Cenário Energia (09/06/2026, 1º trimestre de 2026).
- **Regime GD II (2026):** Lei 14.300/2022; REN ANEEL 1.000/2021, arts. 655-O a 655-Q (define o enquadramento de sistemas solicitados após 07/01/2023).

## Impacto ambiental

- **Fator de emissão médio do SIN (0,0461 kgCO2/kWh):** planilha `Inventario_2026_janset.xlsx` fornecida pelo grupo (aba inventário-todos, Fator Médio Anual 2025); meses de 2025 coincidem com dados publicados por cenarioenergia.com.br. Confirmar link/citação oficial do MCTI antes de uso formal.
- **Fator de emissão de margem de operação (0,4368 kgCO2/kWh):** planilha "Despacho 2026 jan-set" fornecida pelo grupo (aba MDL, Margem de Operação), média simples jan–set/2026. Confirmar link/citação oficial do MCTI.

## API e integração

- OpenAI, function calling: https://developers.openai.com/api/docs/guides/function-calling
- OpenAI, Chat Completions: https://developers.openai.com/api/reference/python/resources/chat/subresources/completions/methods/create

---
**Nota geral:** vários itens acima dependem de fontes secundárias ou de arquivos fornecidos pelo grupo sem o link direto da norma/fonte primária (marcados "a confirmar" ou "fonte secundária"). Isso está sinalizado em `parametros.json` (campo `estimativa`) e repetido nos avisos que as ferramentas devolvem — não é uma omissão desta lista, é o estado real da verificação até 16/11/2026.
