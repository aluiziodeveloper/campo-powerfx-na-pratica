# CAMPO — material de apoio de *Power Fx na Prática*

Este repositório acompanha o livro *Power Fx na Prática — A Linguagem por Trás do Power Apps*, de Jorge Aluizio Alves de Souza. O CAMPO (Controle de Atividades, Manutenção e Ocorrências) é a aplicação que o livro constrói do Capítulo 1 ao 28. Aqui estão a planilha de onde ele nasce, os dados do Teste de Realidade #1, os roteiros que carregam esses dados no seu SharePoint e os modelos que os capítulos mandam preencher.

Os dados são fictícios: pessoas, unidades e ordens de serviço inventadas.

## Como baixar, sem saber git

Um repositório é uma pasta de arquivos que guarda também o histórico de cada alteração. Você não precisa de nenhuma ferramenta para usá-lo: nesta página, clique em **Code** e depois em **Download ZIP**, e descompacte o arquivo onde quiser. Para baixar um arquivo só, abra-o aqui e use o botão de download no canto da visualização.

Quem já usa git pode clonar (`git clone https://github.com/aluiziodeveloper/campo-powerfx-na-pratica.git`) e receber as correções com `git pull`.

O histórico deste repositório (o link *commits*, no topo da lista de arquivos) mostra cada alteração feita no material, com data e descrição. É o controle de origem de que o Capítulo 24 fala, aplicado a um projeto pequeno.

## O que há aqui, por capítulo

| Capítulo | O que usar | Onde |
|---|---|---|
| 1, 3, 5, 8 | A planilha v0.0, com as sete abas, as doze fórmulas e a sujeira que o livro manda inventariar | `material/CAMPO_v0.0.xlsx` |
| 1, 3, 5 | Ficha da planilha, para o inventário | `material/Ficha_da_planilha_v0.0.md` |
| 5 | As listas `Ocorrencias` e `Unidades`, se você preferir criá-las por roteiro em vez de importar a planilha | `carga/` (etapas Listas e Planilha) |
| 6 em diante | Cartão de leitura de fórmulas, para imprimir | `material/Cartao_de_leitura_de_formulas.md` |
| 9, 12 | A massa de 12.000 ordens de serviço com as duas sentinelas, e três jeitos de carregá-la | `dados/` e `carga/` |
| 5 em diante | Pendências do CAMPO | `material/modelos/Pendencias_CAMPO.md` |
| 9, 23, 24, 26, 28 | Registro de Decisões do CAMPO | `material/modelos/Registro_de_Decisoes_do_CAMPO.md` |
| 23 | Registro de Recomendação Técnica | `material/modelos/Registro_de_Recomendacao_Tecnica.md` |
| 25, 27 | Checklist de revisão de fórmulas | `material/modelos/Checklist_de_revisao_de_formulas.md` |
| 25, 26 | Checklist de Produção | `material/modelos/Checklist_de_Producao.md` |
| 27 | Protocolo de medição de fórmulas geradas por IA: vinte pedidos e ficha de registro | `material/Protocolo_IA_20_pedidos.md` |

## Os formatos dos arquivos

- **`.md` (Markdown):** texto comum com marcas simples de formatação (`|` desenha tabelas, `**` faz negrito, `#` faz títulos). O GitHub mostra o arquivo formatado; qualquer editor de texto o abre e grava. Os modelos que os capítulos mandam preencher estão nesse formato para que você os mantenha num editor qualquer, sem depender de um programa específico.
- **`.xlsx`:** a planilha do Capítulo 1, para o Excel.
- **`.csv`:** tabela em texto puro, uma linha por registro, colunas separadas por `;`. Abre no Excel; veja `dados/README.md`.
- **`.json`:** dados estruturados em texto, com nomes e valores entre chaves. Só os roteiros de carga o leem.
- **`.ps1` e `.js`:** os roteiros de carga, em PowerShell e em JavaScript. Veja `carga/README.md`.

## Carregar a massa no seu ambiente

Leia `carga/README.md`. Em resumo: o caminho pelo **navegador** não instala nada nem registra aplicativo; o caminho por **PowerShell** é o mais confortável para quem já usa o PnP; o **fluxo do Power Automate** é o que o Capítulo 9 descreve, e o único que não confere o resultado sozinho.

## Gerar os dados de novo

A massa termina em 30/09/2026. Se você for carregá-la muito depois, gere de novo com a data do dia, para que "aberta há mais de N dias" e as vencidas do Capítulo 12 façam sentido no seu calendário:

```
pip install openpyxl
python ferramentas/gerar_material.py --fim 2027-03-15
```

A semente é fixa: com a mesma data final, os arquivos saem idênticos. A posição das sentinelas não muda com a data.

## Testes dos roteiros de carga

Os dois roteiros são testados contra um SharePoint simulado, sem conectar a nada:

```
node testes/testar-navegador.js
pwsh testes/Testar-Carga.ps1
```

Os cenários: ambiente novo, item recusado no meio da massa, retomada sem duplicar, e lista que já consumiu `ID` demais.

O SharePoint simulado é o que a literatura de testes chama de **dublê** (*test double*): uma peça falsa que responde como a real, para que o teste rode sem rede, sem conta e sem custo, sempre com o mesmo resultado. O dublê prova a lógica dos roteiros; não prova o comportamento do serviço real, e por isso uma execução num locatário de verdade continua necessária. O Capítulo 25 volta ao assunto.

## Errata

Achou um erro no livro ou neste repositório? Abra uma *issue* com o modelo **Errata do livro**: ele pede o capítulo e a seção, o pacto descumprido e onde você conferiu. As correções confirmadas recebem o rótulo `errata` e ficam listadas em [issues com o rótulo errata](https://github.com/aluiziodeveloper/campo-powerfx-na-pratica/issues?q=label%3Aerrata), com o capítulo e a data.

## Licenças

- **Código** (`carga/`, `ferramentas/`, `testes/`): MIT, no arquivo `LICENSE`.
- **Dados e material** (`dados/`, `material/`): Creative Commons Atribuição 4.0 Internacional, em `LICENSE-DADOS.md`.

Os dados são fictícios. O texto do livro não faz parte deste repositório.
