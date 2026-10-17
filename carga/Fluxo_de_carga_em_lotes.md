# Fluxo de carga em lotes (Power Automate)

*Material de apoio do Capítulo 8, seção "O método de carga". O fluxo grava as 12.000 ordens de serviço em 120 requisições, uma por arquivo de lote de 100 itens, usando o recurso de lote da API REST do SharePoint pela ação "Enviar uma solicitação HTTP para o SharePoint", do* connector *padrão.*

🔄 *Nomes de ações e menus do Power Automate mudam. Procure pela ação descrita, não pelo desenho. Roteiro escrito em outubro de 2026. Diferente dos dois roteiros desta pasta, o fluxo não cria as listas, não retoma e não confere: para isso, prefira o navegador ou o PowerShell (veja o `README.md`).*

## Por que assim

- **Uma requisição por item** seriam cerca de 12.000 chamadas, acima do teto diário de requisições de uma licença comum do Microsoft 365 (Capítulo 8, nota 17).
- **Em lotes de 100**, são 120 chamadas de gravação, mais as de leitura dos arquivos: duas ordens de grandeza a menos. A documentação do `$batch` não publica um teto de operações por requisição; 100 é o tamanho que o PnP usa internamente.
- **Os lotes rodam em sequência, sem paralelismo**, para que o `ID` de cada item siga a ordem do arquivo. O teste depende da posição das sentinelas.

## Preparação

1. Envie a pasta `dados/lotes/` para uma biblioteca de documentos do mesmo site da lista (ou para o seu OneDrive). Os nomes `lote_001.txt` a `lote_120.txt` já saem na ordem certa.
2. Anote a URL do site, por exemplo `https://contoso.sharepoint.com/sites/campo`, sem barra no fim.

## O fluxo, passo a passo

1. **Gatilho:** *Disparar um fluxo manualmente*.
2. **Inicializar variável** `SiteUrl`, do tipo cadeia de caracteres, com a URL do site.
3. **Listar arquivos na pasta** da biblioteca onde estão os lotes.
4. **Filtrar matriz** sobre o resultado, mantendo só os nomes que começam com `lote_`, e **ordenar** por nome: `sort(body('Filtrar_matriz'), 'Name')`. A ordem alfabética é a ordem dos lotes.
5. **Aplicar a cada** sobre a matriz ordenada. Nas configurações da ação, ligue o **controle de simultaneidade** e ponha o **grau de paralelismo em 1**. Sem isso, os lotes rodam ao mesmo tempo e os `ID` deixam de seguir a ordem do arquivo.
6. Dentro do laço:
   1. **Obter conteúdo do arquivo** pelo identificador do item corrente.
   2. **Enviar uma solicitação HTTP para o SharePoint**:
      - Endereço do site: `SiteUrl`
      - Método: `POST`
      - URI: `_api/$batch`
      - Cabeçalhos:
        - `Content-Type`: `multipart/mixed; boundary=batch_campo`
        - `Accept`: `application/json;odata=nometadata`
      - Corpo (expressão):
        ```
        replace(base64ToString(body('Obter_conteúdo_do_arquivo')?['$content']), '{{SITE}}', variables('SiteUrl'))
        ```
        Se a ação devolver o conteúdo como texto, e não como objeto com `$content`, use `replace(string(body('Obter_conteúdo_do_arquivo')), '{{SITE}}', variables('SiteUrl'))`.
7. Salve e execute.

## Como saber se deu certo

- A resposta de cada requisição em lote volta com **código 200 mesmo quando itens falham**: o status de cada item está dentro do corpo da resposta, um `HTTP/1.1 201 Created` por item gravado. Abra a saída de uma das execuções e confira.
- No fim, a lista deve ter os 351 da planilha mais 12.000. Confira as duas sentinelas pelo `NumeroOS` e veja se os `ID` batem com `dados/estatisticas.md`. Se quiser a conferência automática, rode só a etapa Conferir de um dos dois roteiros.
- A duração está no histórico de execuções do fluxo, e o consumo de requisições nos relatórios do centro de administração. Anote os dois: o Capítulo 8 não publica esses números, porque dependem do seu locatário.

## Se o serviço recusar um lote, ou o fluxo parar no meio

O lote do SharePoint não é transacional: um item recusado não impede os outros do mesmo lote. **Não apague o que foi gravado para recomeçar**: o SharePoint não reaproveita `ID`, e a primeira sentinela pode deixar de ficar abaixo de 500. Complete a carga com um dos dois roteiros desta pasta, só com as etapas Massa e Conferir: eles procuram o que falta e gravam só isso.

## Se uma coluna tiver outro nome interno

Os lotes usam os nomes `Title`, `NumeroOS`, `Descricao`, `Status`, `Prioridade`, `Local`, `DataAbertura` e `Responsavel`, e as datas vão em UTC (os horários do CSV são de Brasília). Se a sua lista nasceu com outro nome interno (o SharePoint às vezes acrescenta sufixos), descubra o nome em *Configurações da lista → coluna → endereço da página*, parâmetro `Field=`, e troque nos arquivos com um localizar e substituir.
