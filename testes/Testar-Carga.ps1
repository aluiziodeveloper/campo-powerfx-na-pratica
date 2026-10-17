<#
  Testa a lógica de carga/Carregar-CAMPO.ps1 contra um SharePoint simulado em memória.
  Não conecta a nada: os cmdlets do PnP são substituídos por funções com o mesmo nome.

  O que se confere:
    1. ambiente novo: listas, planilha e massa; sentinelas com os ID esperados
    2. falha no meio da massa: a carga para e informa o lote
    3. nova execução: grava só o que falta, inclusive o item recusado no meio, sem duplicar
    4. lista com itens apagados demais: a massa se recusa a começar

  Uso: pwsh ./testes/Testar-Carga.ps1
#>
$ErrorActionPreference = "Stop"
$roteiro = Join-Path (Split-Path $PSScriptRoot -Parent) "carga/Carregar-CAMPO.ps1"

function Reiniciar([int] $proximoId = 1) {
    $global:SP = @{ Listas = @{}; Proximo = @{}; FalharNoItem = 0; Gravados = 0 }
    $global:ProximoInicial = $proximoId
}

function global:Connect-PnPOnline { param([string]$Url, [string]$ClientId, [switch]$Interactive, [switch]$DeviceLogin, [string]$Tenant) }
function global:Get-PnPList {
    param([string]$Identity, $ErrorAction)
    if ($SP.Listas.ContainsKey($Identity)) { return [pscustomobject]@{ Title = $Identity; ItemCount = $SP.Listas[$Identity].Itens.Count } }
    return $null
}
function global:New-PnPList {
    param([string]$Title, [string]$Template, [switch]$OnQuickLaunch)
    $SP.Listas[$Title] = @{ Itens = [System.Collections.Generic.List[hashtable]]::new(); Campos = @{ Title = $true } }
    $SP.Proximo[$Title] = $ProximoInicial
}
function global:Get-PnPField {
    param([string]$List, [string]$Identity, $ErrorAction)
    if ($SP.Listas[$List].Campos.ContainsKey($Identity)) { return $Identity }
    return $null
}
function global:Add-PnPField {
    param([string]$List, [string]$DisplayName, [string]$InternalName, [string]$Type, [switch]$AddToDefaultView)
    $SP.Listas[$List].Campos[$InternalName] = $true
}
function global:Set-PnPField { param([string]$List, [string]$Identity, [hashtable]$Values) }
function global:New-PnPBatch { return [pscustomobject]@{ Pedidos = [System.Collections.Generic.List[object]]::new() } }
function global:Add-PnPListItem {
    param([string]$List, [hashtable]$Values, $Batch)
    $Batch.Pedidos.Add(@{ Lista = $List; Valores = $Values })
}
function global:Invoke-PnPBatch {
    param($Batch, [switch]$Details)
    $falhas = @()
    foreach ($p in $Batch.Pedidos) {
        $SP.Gravados++
        if ($SP.FalharNoItem -gt 0 -and $SP.Gravados -eq $SP.FalharNoItem) {
            $falhas += [pscustomobject]@{ ResponseCode = 429; ErrorMessage = "simulado: limite de requisições" }
            continue
        }
        $item = @{ Id = $SP.Proximo[$p.Lista] }
        foreach ($k in $p.Valores.Keys) { $item[$k] = $p.Valores[$k] }
        $SP.Proximo[$p.Lista]++
        $SP.Listas[$p.Lista].Itens.Add($item)
    }
    return $falhas
}
function global:Get-PnPListItem {
    param([string]$List, [string]$Query, [string[]]$Fields, [int]$PageSize)
    $itens = $SP.Listas[$List].Itens
    if ($Query -match "Ascending='FALSE'") {
        if ($itens.Count -eq 0) { return @() }
        return , ($itens | Sort-Object { $_.Id } -Descending | Select-Object -First 1)
    }
    if ($Query -match "<Value Type='Text'>([^<]+)</Value>") {
        $alvo = $Matches[1]
        return @($itens | Where-Object { $_.NumeroOS -eq $alvo })
    }
    return $itens
}

function Executar([string[]] $etapas, [switch] $esperaFalha) {
    try {
        & $roteiro -Site "https://exemplo.sharepoint.com/sites/campo" -ClientId "00000000-0000-0000-0000-000000000000" -Etapas $etapas *> $null
        if ($esperaFalha) { throw "esperava falha e não houve" }
    } catch {
        if (-not $esperaFalha) { throw }
        return $_.Exception.Message
    }
}

function Confere($condicao, [string] $descricao) {
    if (-not $condicao) { throw "FALHOU: $descricao" }
    Write-Host "ok  $descricao"
}

function IdDe([string] $numero) {
    return ($SP.Listas["Ocorrencias"].Itens | Where-Object { $_.NumeroOS -eq $numero }).Id
}

# 1. ambiente novo
Reiniciar
Executar @("Listas", "Planilha", "Massa", "Conferir")
$oc = $SP.Listas["Ocorrencias"].Itens
Confere ($oc.Count -eq 12351) "ambiente novo: 12.351 itens"
Confere ($SP.Listas["Unidades"].Itens.Count -eq 40) "ambiente novo: 40 unidades"
Confere ((IdDe "OS-000472") -eq 472) "primeira sentinela com ID 472"
Confere ((IdDe "OS-012152") -eq 12152) "segunda sentinela com ID 12152"
Confere ($oc[0].DataAbertura.Kind -eq [DateTimeKind]::Utc -and $oc[0].DataAbertura.Hour -eq 19) "datas em UTC (16:40 de Brasília vira 19:40)"
Confere (-not ($oc | Where-Object { $_.NumeroOS -eq "OS-000352" }).ContainsKey("Responsavel")) "responsável em branco não é gravado como texto vazio"
$semData = @($oc | Select-Object -First 351 | Where-Object { -not $_.ContainsKey("DataAbertura") }).Count
Confere ($semData -eq 12) "as 12 ocorrências sem data continuam sem data"

# 2 e 3. falha no meio da massa (item 5.050) e retomada
Reiniciar
$SP.FalharNoItem = 351 + 40 + 5050
$msg = Executar @("Listas", "Planilha", "Massa") -esperaFalha
Confere ($msg -match "retoma") "falha no meio: a carga para e diz que retoma"
$parcial = $SP.Listas["Ocorrencias"].Itens.Count
Confere ($parcial -eq 351 + 5099) "falha no meio: o lote não é transacional, e os outros 99 itens do lote entraram ($parcial)"
$SP.FalharNoItem = 0
Executar @("Massa", "Conferir")
$oc = $SP.Listas["Ocorrencias"].Itens
Confere ($oc.Count -eq 12351) "retomada: 12.351 itens, sem duplicar"
Confere (@($oc.NumeroOS | Group-Object | Where-Object Count -gt 1).Count -eq 0) "retomada: nenhum NumeroOS repetido"
Confere ((IdDe "OS-005401") -eq 5451) "retomada: o item recusado entra primeiro, logo depois do último gravado"
Confere ((IdDe "OS-005452") -eq 5452) "retomada: o restante do arquivo vem em seguida, na ordem"
Confere ((IdDe "OS-012152") -eq 12152) "retomada: a segunda sentinela mantém o ID 12152"

# 4. lista que já consumiu ID demais
Reiniciar -proximoId 600
$msg = Executar @("Listas", "Planilha", "Massa") -esperaFalha
Confere ($msg -match "acima de 500") "ID consumidos: a massa se recusa a começar"
Confere ($SP.Listas["Ocorrencias"].Itens.Count -eq 351) "ID consumidos: nada da massa foi gravado"

Write-Host "`nTodos os testes passaram."
