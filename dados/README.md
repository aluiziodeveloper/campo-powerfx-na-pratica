# Dados do CAMPO

*Gerados por `ferramentas/gerar_material.py`, com semente fixa. Pessoas, unidades e ordens de serviço são inventadas; não há informação pessoal real.*

| Arquivo | O que é | Capítulos |
|---|---|---|
| `planilha_ocorrencias_351.csv` | As 351 linhas da aba Ocorrencias da planilha v0.0, só as oito colunas de dado, com a sujeira que a planilha tem (seis grafias de `Status`, 47 sem responsável, 12 sem data, sete locais digitados de outro jeito) | 4, 7 |
| `unidades_40.csv` | As 40 unidades e os seus supervisores | 4 |
| `ocorrencias_12000.csv` | A massa do Teste de Realidade #1: 12.000 ordens de serviço em dezoito meses, com as duas sentinelas | 8, 10, 11, 12, 19, 24 |
| `lotes/lote_001.txt` a `lote_120.txt` | Os corpos das requisições em lote da API REST do SharePoint, 100 itens cada, na ordem do arquivo. É o que o fluxo do Power Automate envia | 8 |
| `estatisticas.md` | Os números da massa, para conferência humana | 8, 11 |
| `esperado.json` | Os mesmos números, para a conferência dos roteiros de carga | 8 |

## Convenções

- Separador `;`, codificação UTF-8 com BOM. A codificação é a tabela que transforma bytes em letras; UTF-8 é a que cobre todos os acentos, e o BOM é uma marca invisível no início do arquivo que avisa o Excel disso. Sem ela, o Excel em português abre "Manutenção" como "ManutenÃ§Ã£o".
- A primeira coluna, `ID_esperado`, **não** é carregada: é o `ID` que o SharePoint vai dar a cada item se a lista receber os 351 registros da planilha e nada mais antes da massa.
- Os horários são de Brasília (UTC−3). Os lotes e os roteiros de carga gravam em UTC, para que o instante salvo não dependa do fuso do computador de quem carrega nem do fuso regional do site (Capítulo 9).

## O que a massa garante, e o que não garante

- As palavras **"vibração"** e **"B-07"** aparecem só nas duas sentinelas, em toda a massa e na planilha. A busca do Capítulo 8 depende disso.
- As duas sentinelas estão com `Status` **"Aberta"**, e a segunda está entre as mais novas, como o roteiro de teste do Capítulo 24 supõe.
- A massa usa só as três grafias canônicas de `Status`. A sujeira de grafia é da planilha, e o Capítulo 7 já a limpou.
- As datas da massa se sobrepõem às da planilha. Nenhum teste do livro depende disso: o que decide os Capítulos 8 e 11 é a **posição** do item na lista, e não a data.
- Os números exatos de abertas, por status e por unidade, estão em `estatisticas.md`. O Capítulo 11 usa os mesmos números arredondados (cerca de 2.400 abertas, sessenta por unidade, cento e oitenta na maior).
