# Ficha da planilha v0.0

*Material de apoio do Capítulo 0. Usada de novo no Capítulo 2 (o mapa de quem depende de quem) e no Capítulo 4 (as fontes de dados). Imprima, ou copie para um arquivo seu, e preencha à mão.*

Arquivo: `CAMPO_v0.0.xlsx` · Data do inventário: ____/____/______ · Quem preencheu: ______________________

---

## 1. As abas

| Aba | O que tem dentro | Quantas linhas de dado | Dado, fórmula ou ação? |
|---|---|---|---|
| LEIA-ME | | | |
| Ocorrencias | | | |
| Painel | | | |
| Unidades | | | |
| Equipe | | | |
| Listas | | | |
| Arquivo_2025 | | | |

## 2. As colunas da tabela Ocorrencias

| Col. | Cabeçalho | Alguém digita, ou é calculada? | Se calculada: de quais colunas depende | Vai para a lista do SharePoint? (Cap. 4) | Tipo na lista (Cap. 4) |
|---|---|---|---|---|---|
| A | | | | | |
| B | | | | | |
| C | | | | | |
| D | | | | | |
| E | | | | | |
| F | | | | | |
| G | | | | | |
| H | | | | | |
| I | | | | | |
| J | | | | | |
| K | | | | | |
| L | | | | | |

## 3. As doze fórmulas (Capítulo 0, Tarefa 1)

| # | Aba e célula ou coluna | O que calcula | Tradução para Power Fx (Tarefa 2, só para cinco) |
|---|---|---|---|
| F1 | | | |
| F2 | | | |
| F3 | | | |
| F4 | | | |
| F5 | | | |
| F6 | | | |
| F7 | | | |
| F8 | | | |
| F9 | | | |
| F10 | | | |
| F11 | | | |
| F12 | | | |

## 4. A sujeira (Capítulo 0, Tarefas 3 e 4)

| Pergunta | Resposta | Como contei |
|---|---|---|
| Quantas grafias diferentes de Status existem? Quais? | | |
| Quantas ocorrências estão sem responsável? | | |
| Quantas estão sem data de abertura? | | |
| Quantos registros há em Ocorrencias? | | |
| Quantos registros há em Arquivo_2025? | | |
| Algum Local que a aba Unidades não reconhece? Quais? | | |

*Guarde estes números: o Capítulo 7 volta a eles.*

## 5. Quem depende de quem (Capítulo 2, Tarefa 1)

Desenhe as setas: de cada coluna de dado para cada fórmula que a lê, e de cada fórmula para o contador do Painel que a usa. Marque a cadeia mais longa e a fórmula que não recebe seta nenhuma.

```
  Ocorrencias[Status]        ─►
  Ocorrencias[Prioridade]    ─►
  Ocorrencias[Local]         ─►
  Ocorrencias[DataAbertura]  ─►



                                                    Painel
```

## 6. Ações humanas disfarçadas de recurso (Capítulo 2, Tarefa 2)

Liste o que alguém faz com as mãos para a planilha continuar funcionando, e o que cada coisa vira no aplicativo.

| Ação | Quem faz, e quando | No aplicativo, vira |
|---|---|---|
| | | |
| | | |
| | | |
