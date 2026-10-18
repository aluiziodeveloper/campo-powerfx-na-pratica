<#
.SYNOPSIS
  Prepara as listas do CAMPO e carrega a massa do Teste de Realidade #1 num site do
  SharePoint, conferindo no fim os números que o livro usa.

.DESCRIPTION
  Material de apoio do livro "Power Fx na Prática" (Capítulos 5, 9 e 12).

  O roteiro faz, na ordem, só as etapas pedidas:

    Listas    cria Ocorrencias e Unidades com as colunas e os seis índices do Capítulo 5,
              ou confere as que já existem
    Planilha  grava os 351 registros da planilha v0.0 e as 40 unidades, como a importação
              do Capítulo 5 faria (pula a etapa se a lista já tiver itens)
    Massa     grava as 12.000 ordens de serviço em lotes de 100, em sequência, para que o
              ID de cada item siga a ordem do arquivo; se for interrompido, a nova
              execução grava só o que falta
    Conferir  conta os itens por status, localiza as duas sentinelas e compara com
              dados/esperado.json

  Antes da massa, o roteiro estima o ID que cada sentinela vai receber e se recusa a
  carregar quando a primeira passaria de 500: apagar itens não devolve posições, porque
  o SharePoint não reaproveita ID.

  Requisitos: PowerShell 7.4 ou superior e o módulo PnP.PowerShell (código aberto,
  gratuito, mantido pela comunidade, sem suporte da Microsoft). Desde setembro de 2024 o
  PnP exige um aplicativo registrado no Microsoft Entra ID para entrar no locatário; o
  README desta pasta explica o registro e a alternativa sem registro, pelo navegador.

.EXAMPLE
  ./Carregar-CAMPO.ps1 -Site https://contoso.sharepoint.com/sites/campo -ClientId <id> -Etapas Listas,Planilha,Massa,Conferir

.EXAMPLE
  ./Carregar-CAMPO.ps1 -Site https://contoso.sharepoint.com/sites/campo -ClientId <id> -Etapas Massa,Conferir
  Para quem fez os Capítulos 5 a 8 e já tem a lista com os 351 registros.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $Site,
    [Parameter(Mandatory)] [string] $ClientId,
    [ValidateSet("Listas", "Planilha", "Massa", "Conferir")]
    [string[]] $Etapas = @("Massa", "Conferir"),
    [switch] $EntrarPorCodigo,
    [string] $Tenant,
    [string] $Dados = (Join-Path (Split-Path $PSScriptRoot -Parent) "dados"),
    [int]    $TamanhoLote = 100,
    [switch] $IgnorarPosicao
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Lista = "Ocorrencias"
$ListaUnidades = "Unidades"
$Inicio = Get-Date
$Log = Join-Path $PSScriptRoot ("carga-{0:yyyyMMdd-HHmmss}.log" -f $Inicio)

function Registrar([string] $texto) {
    $linha = "{0:HH:mm:ss}  {1}" -f (Get-Date), $texto
    Write-Host $linha
    Add-Content -Path $Log -Value $linha -Encoding utf8
}

# Os horários do CSV são de Brasília (UTC-3). Grava-se em UTC, para que o instante salvo
# não dependa do fuso deste computador nem do fuso regional do site (Capítulo 10).
function ParaUtc([string] $texto) {
    if ([string]::IsNullOrWhiteSpace($texto)) { return $null }
    return [datetimeoffset]::Parse("$texto-03:00", [Globalization.CultureInfo]::InvariantCulture).UtcDateTime
}

function Valores($linha) {
    $v = @{
        "Title"      = $linha.Titulo
        "NumeroOS"   = $linha.NumeroOS
        "Descricao"  = $linha.Descricao
        "Status"     = $linha.Status
        "Prioridade" = $linha.Prioridade
        "Local"      = $linha.Local
    }
    $data = ParaUtc $linha.DataAbertura
    if ($null -ne $data) { $v["DataAbertura"] = $data }
    if (-not [string]::IsNullOrWhiteSpace($linha.Responsavel)) { $v["Responsavel"] = $linha.Responsavel }
    return $v
}

function UltimoItem([string] $nomeLista) {
    $caml = "<View><Query><OrderBy><FieldRef Name='ID' Ascending='FALSE'/></OrderBy></Query>" +
            "<ViewFields><FieldRef Name='ID'/><FieldRef Name='NumeroOS'/></ViewFields><RowLimit>1</RowLimit></View>"
    $itens = @(Get-PnPListItem -List $nomeLista -Query $caml)
    if ($itens.Count -eq 0) { return $null }
    return $itens[0]
}

function GravarEmLotes([string] $nomeLista, $linhas, [scriptblock] $montar, [string] $rotulo) {
    $total = $linhas.Count
    for ($i = 0; $i -lt $total; $i += $TamanhoLote) {
        $fim = [Math]::Min($i + $TamanhoLote, $total) - 1
        $lote = New-PnPBatch
        foreach ($l in $linhas[$i..$fim]) {
            Add-PnPListItem -List $nomeLista -Values (& $montar $l) -Batch $lote | Out-Null
        }
        # Com -Details e sem -StopOnException, o lote inteiro é enviado e o cmdlet devolve
        # as requisições que falharam, com o código e a mensagem de cada uma.
        $resultado = @(Invoke-PnPBatch -Batch $lote -Details)
        $falhas = @($resultado | Where-Object { $null -ne $_ -and [int]$_.ResponseCode -ge 400 })
        if ($falhas.Count -gt 0) {
            Registrar ("{0}: {1} item(ns) recusado(s) no lote que começa na linha {2}. Primeiro erro: {3}" -f
                $rotulo, $falhas.Count, ($i + 1), $falhas[0].ErrorMessage)
            throw "Carga interrompida. Corrija a causa e execute de novo: a etapa retoma de onde parou."
        }
        Registrar ("{0}: {1} de {2}" -f $rotulo, ($fim + 1), $total)
    }
}

# ------------------------------------------------------------------ conexão

$parametros = @{ Url = $Site; ClientId = $ClientId }
if ($EntrarPorCodigo) {
    $parametros["DeviceLogin"] = $true
    if ($Tenant) { $parametros["Tenant"] = $Tenant }
} else {
    $parametros["Interactive"] = $true
}
Connect-PnPOnline @parametros
Registrar "Conectado a $Site. Etapas: $($Etapas -join ', '). Registro em $Log"

$csvPlanilha = Join-Path $Dados "planilha_ocorrencias_351.csv"
$csvUnidades = Join-Path $Dados "unidades_40.csv"
$csvMassa    = Join-Path $Dados "ocorrencias_12000.csv"
$esperado    = Get-Content (Join-Path $Dados "esperado.json") -Raw -Encoding utf8 | ConvertFrom-Json

# ------------------------------------------------------------------ listas

$colunas = @(
    @{ Nome = "NumeroOS";     Tipo = "Text";     Indice = $true  },
    @{ Nome = "Descricao";    Tipo = "Note";     Indice = $false },
    @{ Nome = "Status";       Tipo = "Text";     Indice = $true  },
    @{ Nome = "Prioridade";   Tipo = "Text";     Indice = $true  },
    @{ Nome = "Local";        Tipo = "Text";     Indice = $true  },
    @{ Nome = "DataAbertura"; Tipo = "DateTime"; Indice = $true  },
    @{ Nome = "Responsavel";  Tipo = "Text";     Indice = $false }
)

if ($Etapas -contains "Listas") {
    if (-not (Get-PnPList -Identity $Lista -ErrorAction SilentlyContinue)) {
        New-PnPList -Title $Lista -Template GenericList -OnQuickLaunch | Out-Null
        Set-PnPField -List $Lista -Identity "Title" -Values @{ Title = "Titulo" } | Out-Null
        Registrar "Lista $Lista criada."
    } else {
        Registrar "Lista $Lista já existe; conferindo as colunas."
    }
    foreach ($c in $colunas) {
        if (-not (Get-PnPField -List $Lista -Identity $c.Nome -ErrorAction SilentlyContinue)) {
            Add-PnPField -List $Lista -DisplayName $c.Nome -InternalName $c.Nome -Type $c.Tipo -AddToDefaultView | Out-Null
            Registrar "  coluna $($c.Nome) ($($c.Tipo)) criada"
        }
    }
    # Índices com a lista ainda pequena: depois de crescer, a operação pode ser recusada (Capítulo 5).
    foreach ($nome in @("Title") + ($colunas | Where-Object { $_.Indice } | ForEach-Object { $_.Nome })) {
        Set-PnPField -List $Lista -Identity $nome -Values @{ Indexed = $true } | Out-Null
    }
    Registrar "  seis índices conferidos: Titulo, NumeroOS, Status, Prioridade, Local, DataAbertura"

    if (-not (Get-PnPList -Identity $ListaUnidades -ErrorAction SilentlyContinue)) {
        New-PnPList -Title $ListaUnidades -Template GenericList -OnQuickLaunch | Out-Null
        Set-PnPField -List $ListaUnidades -Identity "Title" -Values @{ Title = "Nome" } | Out-Null
        Add-PnPField -List $ListaUnidades -DisplayName "Supervisor" -InternalName "Supervisor" -Type Text -AddToDefaultView | Out-Null
        Registrar "Lista $ListaUnidades criada."
    }
}

# Mesmo sem a etapa Listas, nada é gravado numa lista sem as colunas do livro.
if ($Etapas -contains "Planilha" -or $Etapas -contains "Massa") {
    $faltando = @($colunas | Where-Object { -not (Get-PnPField -List $Lista -Identity $_.Nome -ErrorAction SilentlyContinue) } |
                  ForEach-Object { $_.Nome })
    if ($faltando.Count -gt 0) {
        throw (("A lista $Lista não tem as colunas: {0}. Rode com -Etapas Listas, ou confira o nome interno " +
               "de cada coluna (Configurações da lista, coluna, parâmetro Field= no endereço).") -f ($faltando -join ", "))
    }
}

# ------------------------------------------------------------------ planilha

if ($Etapas -contains "Planilha") {
    $existentes = (Get-PnPList -Identity $Lista).ItemCount
    if ($existentes -gt 0) {
        Registrar "Planilha: a lista já tem $existentes itens; etapa pulada (nada é gravado em duplicidade)."
    } else {
        $linhas = @(Import-Csv -Path $csvPlanilha -Delimiter ";" -Encoding utf8)
        GravarEmLotes $Lista $linhas { param($l) Valores $l } "Planilha"
    }
    if ((Get-PnPList -Identity $ListaUnidades -ErrorAction SilentlyContinue) -and
        (Get-PnPList -Identity $ListaUnidades).ItemCount -eq 0) {
        $unidades = @(Import-Csv -Path $csvUnidades -Delimiter ";" -Encoding utf8)
        GravarEmLotes $ListaUnidades $unidades { param($u) @{ Title = $u.Nome; Supervisor = $u.Supervisor } } "Unidades"
    }
}

# ------------------------------------------------------------------ massa

if ($Etapas -contains "Massa") {
    $massa = @(Import-Csv -Path $csvMassa -Delimiter ";" -Encoding utf8)
    $indice = @{}
    for ($k = 0; $k -lt $massa.Count; $k++) { $indice[$massa[$k].NumeroOS] = $k }

    $ultimo = UltimoItem $Lista
    $pendentes = $massa
    if ($null -ne $ultimo -and $indice.ContainsKey([string]$ultimo["NumeroOS"])) {
        # Retomada. O lote do SharePoint não é transacional: um item recusado no meio não
        # impede os seguintes. Por isso se procura tudo o que falta, e não só o que vem
        # depois do último item gravado.
        $presentes = [System.Collections.Generic.HashSet[string]]::new()
        Get-PnPListItem -List $Lista -Fields "NumeroOS" -PageSize 2000 | ForEach-Object {
            [void]$presentes.Add([string]$_["NumeroOS"])
        }
        $pendentes = @($massa | Where-Object { -not $presentes.Contains($_.NumeroOS) })
        $buracos = @($pendentes | Where-Object { $indice[$_.NumeroOS] -lt $indice[[string]$ultimo["NumeroOS"]] })
        Registrar "Massa: retomando. Último item gravado: $($ultimo['NumeroOS']) (ID $($ultimo.Id)); faltam $($pendentes.Count)."
        if ($buracos.Count -gt 0) {
            Registrar (("  {0} item(ns) recusado(s) no meio da carga entram agora, depois do último gravado, com ID fora " +
                       "da ordem do arquivo. A conferência mostra se as sentinelas continuam dentro das regras.") -f $buracos.Count)
        }
    } else {
        $proximo = if ($null -eq $ultimo) { 1 } else { $ultimo.Id + 1 }
        $s1 = $esperado.sentinelas[0]
        $s2 = $esperado.sentinelas[1]
        $id1 = $proximo + $s1.indice_na_massa
        $id2 = $proximo + $s2.indice_na_massa
        Registrar ("Massa: o próximo ID é pelo menos {0}. Estimativa: {1} com ID {2}, {3} com ID {4}." -f
            $proximo, $s1.NumeroOS, $id1, $s2.NumeroOS, $id2)
        Registrar "  (itens apagados também consomem ID; se houve exclusões, os números reais serão maiores)"
        if ($id1 -gt 500 -and -not $IgnorarPosicao) {
            throw (("A primeira sentinela ficaria com ID {0}, acima de 500, e o Teste de Realidade #1 deixaria de " +
                   "mostrar o que mostra. Use um site novo, com -Etapas Listas,Planilha,Massa,Conferir, ou execute " +
                   "com -IgnorarPosicao, sabendo o que o teste perde.") -f $id1)
        }
    }
    if ($pendentes.Count -gt 0) {
        $relogio = [Diagnostics.Stopwatch]::StartNew()
        GravarEmLotes $Lista $pendentes { param($l) Valores $l } "Massa"
        $relogio.Stop()
        Registrar (("Massa gravada em {0:hh\:mm\:ss}. Anote a duração: ela é do seu locatário, " +
                   "não da plataforma.") -f $relogio.Elapsed)
    } else {
        Registrar "Massa: já estava completa."
    }
}

# ------------------------------------------------------------------ conferência

if ($Etapas -contains "Conferir") {
    $normal = @{ "aberta" = "Aberta"; "aberto" = "Aberta"; "em andamento" = "Em andamento"; "fechada" = "Fechada" }
    $porStatus = @{}
    # Hashtable do PowerShell não diferencia maiúsculas; as grafias precisam diferenciar.
    $grafias = [System.Collections.Generic.Dictionary[string, int]]::new([StringComparer]::Ordinal)
    $total = 0
    Get-PnPListItem -List $Lista -Fields "Status" -PageSize 2000 | ForEach-Object {
        $total++
        $st = [string]$_["Status"]
        $grafias[$st] = 1 + $(if ($grafias.ContainsKey($st)) { $grafias[$st] } else { 0 })
        $chave = $normal[$st.Trim().ToLowerInvariant()] ?? $st
        $porStatus[$chave] = 1 + ($porStatus[$chave] ?? 0)
    }

    $linhasConf = @()
    $linhasConf += [pscustomobject]@{ Item = "Registros"; Esperado = $esperado.total; Na_lista = $total }
    foreach ($st in "Aberta", "Em andamento", "Fechada") {
        $linhasConf += [pscustomobject]@{ Item = $st; Esperado = $esperado.por_status.$st; Na_lista = ($porStatus[$st] ?? 0) }
    }
    foreach ($s in $esperado.sentinelas) {
        $caml = "<View><Query><Where><Eq><FieldRef Name='NumeroOS'/><Value Type='Text'>$($s.NumeroOS)</Value></Eq></Where></Query></View>"
        $achado = @(Get-PnPListItem -List $Lista -Query $caml)
        $id = if ($achado.Count -gt 0) { $achado[0].Id } else { "não encontrada" }
        $linhasConf += [pscustomobject]@{ Item = "$($s.NumeroOS) ($($s.regra))"; Esperado = $s.ID_esperado; Na_lista = $id }
    }
    $linhasConf | Format-Table -AutoSize | Out-String | ForEach-Object { Registrar $_ }
    Registrar ("Grafias de Status na lista: {0}" -f (($grafias.GetEnumerator() | Sort-Object Key |
        ForEach-Object { "$($_.Key) = $($_.Value)" }) -join "; "))
    Registrar ("As contagens por status normalizam as grafias da planilha, como o Capítulo 8 faz. " +
               "O que o Teste de Realidade #1 exige são as duas regras de ID; os totais são os números contra os " +
               "quais o Capítulo 9 compara o aplicativo.")
}

Registrar ("Fim. Duração total: {0:hh\:mm\:ss}." -f ((Get-Date) - $Inicio))
