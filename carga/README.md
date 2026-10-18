# Carga do CAMPO no seu SharePoint

*Capítulos 4, 8 e 11 de* Power Fx na Prática. *Três caminhos para levar a massa do Teste de Realidade #1 (e, se você precisar, as listas e a planilha do Capítulo 4) para um site seu.*

## Qual caminho usar

| | Navegador | PowerShell | Power Automate |
|---|---|---|---|
| Arquivo | `carregar-campo-navegador.js` | `Carregar-CAMPO.ps1` | `Fluxo_de_carga_em_lotes.md` |
| Instala alguma coisa? | Não | PowerShell 7.4 e o módulo PnP.PowerShell | Não |
| Registra aplicativo no Entra ID? | Não | Sim (veja abaixo) | Não |
| Cria as listas, colunas e índices? | Sim | Sim | Não: as listas precisam existir |
| Confere o resultado sozinho? | Sim | Sim | Não: a conferência é manual |
| Retoma se parar no meio? | Sim | Sim | Não |
| Limitação | Algumas organizações bloqueiam as ferramentas do desenvolvedor do navegador | Registrar aplicativo costuma exigir consentimento de administrador | Montar o fluxo à mão, e conferir à mão |

Os três gravam a mesma massa, na mesma ordem, em lotes de 100 itens enviados um depois do outro, e gravam as datas em UTC. Os dois roteiros fazem as mesmas quatro etapas e se recusam a começar a massa quando a primeira sentinela ficaria com `ID` acima de 500.

## As quatro etapas

| Etapa | O que faz | Quando usar |
|---|---|---|
| Listas | Cria `Ocorrencias` (com `Titulo` na coluna `Title`, `NumeroOS`, `Descricao`, `Status`, `Prioridade`, `Local`, `DataAbertura` e `Responsavel`) e `Unidades` (`Nome`, `Supervisor`), com os seis índices do Capítulo 4. Se a lista já existe, só acrescenta o que falta | Se você não fez o Capítulo 4 no seu site |
| Planilha | Grava os 351 registros da planilha v0.0, do jeito que a importação do Capítulo 4 os deixa (com as seis grafias de `Status`), e as 40 unidades. Pula a etapa se a lista já tiver itens | Junto com Listas |
| Massa | Grava as 12.000 ordens de serviço. Se for interrompida, a próxima execução grava só o que falta | Capítulo 8 |
| Conferir | Conta os itens por status e localiza as duas sentinelas, e compara com `dados/esperado.json` | Sempre, depois da massa |

**Quem fez os Capítulos 4 a 7 no próprio site** usa só Massa e Conferir: a lista já está lá, com os 351 registros e as grafias que o Capítulo 7 corrigiu. **Quem chega ao Capítulo 8 sem ter montado a lista** usa as quatro etapas num site novo.

## Por que a posição importa, e por que não se conserta apagando

O teste depende do `ID` que o SharePoint dá a cada item: a primeira sentinela precisa ficar com `ID` até 500 e a segunda acima de 10.000, o teto do limite de linhas que o Capítulo 8 manda subir (até setembro de 2026 o teto era 2.000). O `ID` segue a ordem de gravação e **nunca é reaproveitado**: um item apagado leva o número dele junto. Por isso, numa lista que já teve muitos itens criados e apagados, a primeira sentinela pode passar de 500 mesmo com a lista quase vazia, e apagar mais itens só piora. Os dois roteiros estimam a posição antes de gravar e param com a explicação. A saída é um site novo, ou a opção de ignorar a posição, sabendo que o teste perde o que mostra.

## Os conceitos por trás dos roteiros

Você não precisa deles para carregar a massa. Eles explicam por que os roteiros são escritos assim, e quase todos voltam no livro.

- **API REST e HTTP.** O SharePoint aceita pedidos pela web: cada recurso (uma lista, um item, uma coluna) tem um endereço, e o pedido diz o que fazer com ele (`GET` para ler, `POST` para criar). HTTP é o protocolo da web, o mesmo que o navegador usa para abrir páginas. REST é o estilo de organizar uma API dessa forma, por endereços e verbos.
- **Lote (`$batch`).** Um pedido HTTP que carrega muitos outros dentro dele. Cem gravações viajam numa ida ao servidor só. O lote do SharePoint **não é transacional**: se um item falha, os outros do mesmo lote são gravados assim mesmo. Por isso os roteiros conferem a resposta item a item, e por isso a retomada procura o que falta em vez de recomeçar.
- **Sequência e `ID`.** O SharePoint numera os itens na ordem em que chegam e nunca reaproveita um número. Lotes em paralelo embaralhariam a ordem; os roteiros enviam um lote depois do outro.
- **Sessão e chave de formulário.** No navegador, o roteiro usa a sessão em que você já entrou (o mesmo cookie que mantém você conectado ao site). Para gravar, o SharePoint exige ainda uma chave de formulário (*form digest*), que prova que o pedido saiu de uma página do próprio site; o roteiro a pede e a renova antes de vencer.
- **Limitação de ritmo (*throttling*).** Quando muitos pedidos chegam depressa, o serviço responde `429` ou `503` e diz quanto esperar (`Retry-After`). Os roteiros esperam e tentam de novo, com intervalos crescentes quando o serviço não diz o tempo (*backoff*). Insistir sem esperar só aumenta a punição.
- **Retomada sem duplicar.** Executar a etapa Massa duas vezes produz o mesmo resultado que executar uma: ela grava só os `NumeroOS` que ainda não estão na lista. Em programação, isso se chama **idempotência**, e o Capítulo 20 faz dela uma regra de integração.
- **UTC.** O horário universal, sem fuso. Os horários do CSV são de Brasília; os roteiros os convertem para UTC antes de gravar, para que o instante salvo seja o mesmo qualquer que seja o fuso do seu computador ou do site (Capítulo 9).
- **PowerShell e módulo.** PowerShell é a linguagem de comandos da Microsoft para automação, e roda em Windows, macOS e Linux. Um módulo é um pacote de comandos prontos; o PnP.PowerShell traz os comandos para o SharePoint.
- **Registro de aplicativo no Entra ID.** O Microsoft Entra ID controla as contas e os acessos da organização. Um programa que age em nome de uma pessoa (como o PnP) precisa estar registrado lá, com as permissões que pode pedir. O navegador dispensa isso porque o roteiro roda dentro da página do site, com a sua sessão.
- **Console do navegador.** O painel técnico que o navegador abre com F12. A aba *Console* executa código JavaScript na página aberta, com os mesmos acessos que a página tem.

## Navegador, sem instalar nada

1. Baixe a pasta `dados/` deste repositório.
2. Entre, com a sua conta, no site do SharePoint onde a lista vai morar. Você precisa de permissão para criar listas (para a etapa Listas) ou para editar itens (para as demais).
3. **Abra `carregar-campo-navegador.js` e leia.** Ele só conversa com o site em que você está, com a sua sessão, pela API REST do SharePoint. Colar no console um código que você não leu é como dar a senha a um desconhecido; a regra vale para este arquivo também.
4. Tecle F12, abra a aba *Console*, cole o conteúdo do arquivo e tecle Enter. Alguns navegadores pedem que você digite uma confirmação antes de aceitar a colagem; é a proteção contra exatamente o que o passo 3 descreve.
5. No painel que aparece, confira o endereço do site, escolha os quatro arquivos de `dados/` (`planilha_ocorrencias_351.csv`, `unidades_40.csv`, `ocorrencias_12000.csv`, `esperado.json`), marque as etapas e clique em *Executar*.
6. Não feche a aba até aparecer *Fim*. Se fechar, ou se algo falhar, execute de novo com as mesmas etapas: a massa continua de onde parou.

## PowerShell

Requisitos: PowerShell 7.4 ou superior e o módulo PnP.PowerShell, que é código aberto, gratuito e mantido pela comunidade, sem suporte da Microsoft.

```powershell
Install-Module PnP.PowerShell -Scope CurrentUser
```

Desde setembro de 2024, o PnP exige um aplicativo registrado no Microsoft Entra ID do seu locatário. O próprio módulo o registra, se a sua conta puder consentir:

```powershell
Register-PnPEntraIDAppForInteractiveLogin -ApplicationName "Carga CAMPO" -Tenant contoso.onmicrosoft.com
```

Anote o identificador do aplicativo (*Client ID*) que o comando devolve. Se a sua conta não puder consentir, o pedido vai para um administrador; enquanto ele não responde, use o caminho do navegador.

```powershell
# quem fez os Capítulos 4 a 7
./carga/Carregar-CAMPO.ps1 -Site https://contoso.sharepoint.com/sites/campo -ClientId <client-id>

# site novo, do zero
./carga/Carregar-CAMPO.ps1 -Site https://contoso.sharepoint.com/sites/campo -ClientId <client-id> -Etapas Listas,Planilha,Massa,Conferir
```

Sem navegador na máquina, acrescente `-EntrarPorCodigo -Tenant contoso.onmicrosoft.com`. Cada execução grava um registro `carga-AAAAMMDD-HHMMSS.log` nesta pasta.

## Depois da carga

- A conferência mostra os números esperados ao lado dos encontrados. Os totais por status juntam as grafias da planilha, como o Capítulo 7 faz.
- **Anote a duração.** O Capítulo 8 não publica quanto a carga demora, porque depende do seu locatário, da hora e da fila do serviço. O número é seu, e o método é este.
- Se você carregar muito depois de setembro de 2026, gere a massa de novo com a data do dia (veja o README principal), para que "aberta há mais de N dias" faça sentido no seu calendário.

🔄 *Escrito em outubro de 2026. Os dois roteiros foram testados contra um SharePoint simulado (`testes/`), com os cenários de ambiente novo, falha no meio, retomada e lista com `ID` consumidos. Nomes de cmdlets, a exigência de registro do PnP e o comportamento do console dos navegadores mudam; se algo divergir, abra uma *issue* neste repositório.*
