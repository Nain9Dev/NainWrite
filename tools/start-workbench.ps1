#Requires -Version 7.4
<#Start the local application and only its stopped, scoped dependencies.#>
[CmdletBinding()]
param([string]$Python, [string]$Java)
$ErrorActionPreference = 'Stop'
$nainRoot = Split-Path -Parent $PSScriptRoot
$nainConfigPath = Join-Path $nainRoot '.tools/workbench-runtime.json'
if (Test-Path -LiteralPath $nainConfigPath) {
    $nainConfig = Get-Content -LiteralPath $nainConfigPath -Raw | ConvertFrom-Json
    if (-not $Python) { $Python = $nainConfig.python }
    if (-not $Java) { $Java = $nainConfig.java }
}
if (-not $Python) { $Python = (Get-Command python -CommandType Application).Source }
if (-not $Java) { $Java = (Get-Command java -CommandType Application).Source }
if (-not (Test-Path -LiteralPath $Python) -or -not (Test-Path -LiteralPath $Java)) {
    throw 'Set -Python and -Java to installed local runtimes.'
}
& $Python -c 'import pdfplumber, pypdfium2, pypdf, reportlab, PIL'
if ($LASTEXITCODE -ne 0) { throw 'Document dependencies are missing; install requirements-documents.txt into a local environment first.' }
$nainOllama = @(Get-NetTCPConnection -State Listen | Where-Object LocalPort -eq 11436)
if ($nainOllama.Count -eq 0) {
    & (Join-Path $PSScriptRoot 'start-local-ollama.ps1')
} elseif ($nainOllama.Count -ne 1 -or $nainOllama[0].LocalAddress -ne '127.0.0.1') {
    throw 'Dedicated Ollama listener is not loopback-only.'
}
$nainLT = @(Get-NetTCPConnection -State Listen | Where-Object LocalPort -eq 8082)
if ($nainLT.Count -eq 0) {
    $nainLTDirectory = Join-Path $nainRoot '.tools/languagetool/LanguageTool-6.9-SNAPSHOT'
    if (-not (Test-Path (Join-Path $nainLTDirectory 'languagetool-server.jar'))) {
        throw 'The existing local LanguageTool installation is missing.'
    }
    $nainJavaProcess = Start-Process -FilePath $Java -WindowStyle Hidden -PassThru `
        -WorkingDirectory $nainLTDirectory `
        -ArgumentList @('-cp', 'languagetool-server.jar', 'org.languagetool.server.HTTPServer', '--port', '8082') `
        -RedirectStandardOutput (Join-Path $nainRoot '.tools/languagetool.stdout.log') `
        -RedirectStandardError (Join-Path $nainRoot '.tools/languagetool.stderr.log')
    $nainDeadline = [DateTime]::UtcNow.AddSeconds(30)
    do {
        $nainJavaProcess.Refresh()
        if ($nainJavaProcess.HasExited) { throw 'LanguageTool stopped during startup; inspect its local log.' }
        $nainLT = @(Get-NetTCPConnection -State Listen | Where-Object LocalPort -eq 8082)
        if ($nainLT.Count) { break }
        Start-Sleep -Milliseconds 250
    } while ([DateTime]::UtcNow -lt $nainDeadline)
    if (-not $nainLT.Count -or @($nainLT | Where-Object { $_.LocalAddress -notin @('127.0.0.1','::1') -or $_.OwningProcess -ne $nainJavaProcess.Id }).Count) {
        Stop-Process -InputObject $nainJavaProcess
        throw 'LanguageTool startup could not establish an owned loopback-only listener.'
    }
} elseif (@($nainLT | Where-Object LocalAddress -notin @('127.0.0.1','::1')).Count) {
    throw 'Existing proofreading listener is not loopback-only.'
}
& $Python -c "import sys; sys.path.insert(0, r'$nainRoot/src'); from spanish_rewriter.language_tool import LanguageToolClient; [LanguageToolClient(language=l).check('Prueba.' if l=='es-ES' else 'Check.') for l in ('es-ES','en-US','en-GB')]; print('Local proofreaders verified.')"
if ($LASTEXITCODE -ne 0) { throw 'Local proofreading identity check failed.' }
if (@(Get-NetTCPConnection -State Listen | Where-Object LocalPort -eq 8765).Count) {
    throw 'Application port 8765 is occupied; inspect or reuse the existing application.'
}
$nainRun = [Guid]::NewGuid().ToString('N')
$nainApp = Start-Process -FilePath $Python -WindowStyle Hidden -PassThru -WorkingDirectory $nainRoot `
    -ArgumentList @('-u', 'tools/start_workbench.py') `
    -RedirectStandardOutput (Join-Path $nainRoot ".tools/workbench-$nainRun.stdout.log") `
    -RedirectStandardError (Join-Path $nainRoot ".tools/workbench-$nainRun.stderr.log")
$nainDeadline = [DateTime]::UtcNow.AddSeconds(15)
do {
    $nainApp.Refresh()
    if ($nainApp.HasExited) { throw "Workbench stopped; inspect .tools/workbench-$nainRun.stderr.log" }
    $nainListener = @(Get-NetTCPConnection -State Listen | Where-Object LocalPort -eq 8765)
    if ($nainListener.Count) { break }
    Start-Sleep -Milliseconds 250
} while ([DateTime]::UtcNow -lt $nainDeadline)
if ($nainListener.Count -ne 1 -or $nainListener[0].LocalAddress -ne '127.0.0.1' -or $nainListener[0].OwningProcess -ne $nainApp.Id) {
    Stop-Process -InputObject $nainApp
    throw 'Workbench listener could not be verified.'
}
[pscustomobject]@{url='http://127.0.0.1:8765'; processId=$nainApp.Id; startedAt=$nainApp.StartTime; log=".tools/workbench-$nainRun.stderr.log"} | ConvertTo-Json
