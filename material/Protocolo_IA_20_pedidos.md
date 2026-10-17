# Protocolo de medição: fórmulas geradas por assistente de IA

*Material de apoio do Capítulo 26, seção "O método para medir". Vinte pedidos fixos, do domínio do CAMPO, cada um submetido de duas formas. As quarenta respostas são classificadas pelas seis categorias do capítulo.*

🔄 *O resultado vale para a combinação ferramenta × versão × data em que você o obtiver. Registre as três.*

---

## 1. Regras de execução

1. **Uma conversa nova por pedido.** Nada de contexto acumulado de um pedido para o outro.
2. **Só a primeira resposta.** Não peça de novo, não corrija, não diga "isso não delega".
3. **Os pedidos naturais num dia, os especificados em outro.**
4. **A resposta registrada literalmente**, com o texto explicativo que a acompanha.
5. **Todos os pedidos no resultado**, inclusive os que contrariarem a sua expectativa.
6. **Cole cada fórmula no estúdio**, no lugar indicado pelo pedido, com o aplicativo apontando para a lista `Ocorrencias` carregada com a massa do Teste de Realidade #1. A classificação depende do que o estúdio responde, e não da sua leitura.

## 2. O contexto dos pedidos especificados

Cada pedido especificado é o pedido natural seguido deste bloco, sem alteração:

> Contexto: aplicativo de tela do Power Apps, idioma de autoria português (Brasil), portanto `;` como separador de argumentos e `;;` entre ações. Fonte de dados: lista do SharePoint `Ocorrencias`, com cerca de 12.350 itens e as colunas `Title`, `NumeroOS` (texto, chave de negócio), `Descricao` (várias linhas), `Status` (texto: "Aberta", "Em andamento", "Fechada"), `Prioridade` (texto: "Crítica", "Alta", "Média", "Baixa"), `Local` (texto, nome da unidade), `DataAbertura` (data e hora) e `Responsavel` (texto). Lista auxiliar `Unidades` (`Nome`, `Supervisor`). Exigências: a consulta precisa delegar ao SharePoint; se não houver forma delegável, diga isso em vez de propor uma que não delega. Trate campos que podem vir em branco. Toda gravação com tratamento de erro. Diga em qual propriedade de qual controle cada fórmula deve ficar.

## 3. Os vinte pedidos

| # | Pedido natural | Onde a fórmula vai | O que o livro espera de uma boa resposta |
|---|---|---|---|
| 1 | Preciso mostrar numa galeria só as ordens de serviço que estão abertas. | `Items` da galeria | Igualdade sobre `Status`, delegável (Cap. 8) |
| 2 | Quero uma caixa de busca que encontre a ordem de serviço pelo número ou pelo título. | `Items` da galeria | `StartsWith` sobre `NumeroOS` e `Title`, ou a declaração de que "contém" não delega (Caps. 8 e 11) |
| 3 | Quero mostrar o total de horas apontadas por unidade neste mês. | `Items` de uma galeria de resumo | Reconhecer que agregação não delega no SharePoint, e propor recorte ou fluxo (Caps. 10 e 11) |
| 4 | Preciso de um botão que feche a ordem de serviço selecionada na galeria. | `OnSelect` do botão | `Patch` sobre `galOcorrencias.Selected`, com `IfError` (Cap. 13) |
| 5 | Como calculo há quantos dias a ordem de serviço está aberta? | `Text` de um rótulo na galeria | `DateDiff` com tratamento de `DataAbertura` em branco (Caps. 6 e 9) |
| 6 | Quero que cada supervisor veja apenas as ordens de serviço da unidade dele. | `Items` da galeria | Filtro delegável **e** a ressalva de que filtrar na tela não é segurança (Cap. 21) |
| 7 | Quero um contador com quantas ordens de serviço críticas estão abertas. | `Text` de um rótulo | `CountRows` sobre filtro: a contagem não delega e dá no máximo 500 (Cap. 10) |
| 8 | Preciso listar as ordens de serviço vencidas, considerando o prazo de cada prioridade. | `Items` da galeria | Datas de corte calculadas fora da condição (Cap. 11, Regra 10) |
| 9 | Quero ordenar a galeria da mais recente para a mais antiga. | `Items` da galeria | `Sort` sobre `DataAbertura`, depois do recorte (Cap. 10) |
| 10 | Quero mostrar a última ordem de serviço aberta na unidade. | `Text` de um rótulo | `First(Sort(...; Descending))`, e não `Last` (Cap. 10) |
| 11 | Quero uma lista suspensa com as unidades, para filtrar a galeria. | `Items` da lista suspensa e da galeria | Lista alimentada por `Unidades`; filtro por igualdade (Caps. 7 e 11) |
| 12 | Preciso de um formulário para registrar uma nova ordem de serviço. | `OnSelect` do botão Salvar | `SubmitForm`, com o que vem depois no `OnSuccess` (Caps. 4 e 13) |
| 13 | Quero gravar a data e o usuário que fechou a ordem de serviço. | `OnSelect` do botão | `Now()` e `User().Email` no registro de alteração, só os campos que mudam (Cap. 13) |
| 14 | Quero fechar de uma vez todas as ordens marcadas na galeria. | `OnSelect` do botão | `ForAll` monta a tabela, um `Patch` grava (Caps. 7 e 13) |
| 15 | Quero mostrar o nome do supervisor da unidade de cada ordem de serviço. | `Text` de um rótulo na galeria | `LookUp` em `Unidades`, ciente de que é uma consulta por linha (Caps. 3 e 16) |
| 16 | Preciso de um resumo com quantas ordens há em cada status. | `Items` de uma galeria | Agrupamento não delega; propor recorte por unidade ou fluxo (Cap. 10) |
| 17 | Quero guardar a unidade escolhida para usar em outras telas. | Onde o assistente indicar | Fórmula nomeada sobre o controle, e não variável global (Cap. 12) |
| 18 | Quero avisar o usuário se a gravação falhar. | `OnSelect` do botão | `IfError` com ramificação por `FirstError.Kind`, nunca pelo texto (Cap. 13) |
| 19 | Quero buscar ordens de serviço pela descrição do problema. | `Items` da galeria | Declarar que `Search` e `in` não delegam no SharePoint e propor camadas (Cap. 11) |
| 20 | Quero carregar as ordens de serviço quando o aplicativo abre, para ficar mais rápido. | `App.OnStart` ou onde indicar | Recusar a coleção da tabela inteira e explicar o limite de 500 (Caps. 11 e 12) |

## 4. A classificação

Para cada resposta, marque **todas** as categorias que se aplicam, pelo critério objetivo:

| Categoria | Marca-se quando |
|---|---|
| Não delega | A consulta usa operação que não consta da tabela de delegação da sua fonte |
| Separadores | O estúdio em português recusa a fórmula por causa da vírgula |
| Função inexistente | O estúdio recusa um nome |
| Branco | Há cálculo ou comparação sobre campo que pode vir vazio, sem tratamento |
| Escrita | Há gravação sem tratamento de erro, ou com o registro-base relido na hora |
| Estado | Há variável global ou coleção onde uma fórmula nomeada ou a fonte resolveria |

E três perguntas por resposta: **iria a produção como está? Quantas correções até poder publicar? A explicação que acompanha a fórmula está certa?**

## 5. Ficha de registro

Ferramenta: ____________________ · Versão: __________ · Data dos naturais: ___/___/_____ · Data dos especificados: ___/___/_____

| # | Forma | Não delega | Separadores | Função inexistente | Branco | Escrita | Estado | Iria a produção? | Correções | Explicação certa? |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Natural | | | | | | | | | |
| 1 | Especificado | | | | | | | | | |
| 2 | Natural | | | | | | | | | |
| 2 | Especificado | | | | | | | | | |
| … | | | | | | | | | | |
| 20 | Natural | | | | | | | | | |
| 20 | Especificado | | | | | | | | | |
| **Total** | **Natural** | | | | | | | | | |
| **Total** | **Especificado** | | | | | | | | | |

## 6. Como ler o resultado

- **"Não delega" frequente nos naturais:** a hipótese do Capítulo 26 se confirmou no seu ambiente.
- **"Não delega" raro:** a hipótese caiu, e o que procurar primeiro nas fórmulas geradas é a categoria que a ficha mostrar mais.
- **Especificados melhores que naturais:** a primeira etapa do protocolo de uso (especificar antes de pedir) ganhou evidência sua.
- **Explicação errada numa resposta cuja fórmula parece certa:** é o caso mais perigoso, o da armadilha da autoridade.

Pela Regra 19, o número só vale com esta ficha ao lado. Guarde as duas juntas.
