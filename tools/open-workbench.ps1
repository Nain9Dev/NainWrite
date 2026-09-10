#Requires -Version 7.4
<#Open or start this repository's local review application.#>
[CmdletBinding()]
param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$nainRoot = Split-Path -Parent $PSScriptRoot
$nainUrl = 'http://127.0.0.1:8765'
$nainListeners = @(Get-NetTCPConnection -State Listen | Where-Object LocalPort -eq 8765)
if ($nainListeners.Count) {
    if ($nainListeners.Count -ne 1 -or $nainListeners[0].LocalAddress -ne '127.0.0.1') {
        throw 'Application port is occupied by an unexpected listener.'
    }
    $nainProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $($nainListeners[0].OwningProcess)"
    if ($nainProcess.CommandLine -notmatch 'tools[/\\]start_workbench\.py') {
        throw 'Application port belongs to another process; it will not be opened or stopped.'
    }
} else {
    & (Join-Path $PSScriptRoot 'start-workbench.ps1')
}
$nainPage = Invoke-WebRequest -Uri $nainUrl -TimeoutSec 10 -NoProxy
if ($nainPage.Content -notmatch 'name="nainwrite-token"' -or $nainPage.Content -notmatch 'NainWrite') {
    throw 'Local application identity check failed.'
}
if (-not $NoBrowser) { Start-Process $nainUrl }
Write-Output $nainUrl
