#Requires -Version 7.4
<#
Start a dedicated loopback-only Ollama without changing shared services.
Run with PowerShell 7.4 or later. No models are loaded or downloaded.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$nainPort = 11436
$nainRoot = Split-Path -Parent $PSScriptRoot
$nainExecutable = (Get-Command ollama -CommandType Application -ErrorAction Stop).Source
$nainOccupied = @(Get-NetTCPConnection -State Listen -ErrorAction Stop |
    Where-Object LocalPort -eq $nainPort)
if ($nainOccupied.Count -ne 0) {
    throw "Port $nainPort is occupied. Inspect its owner; no process was changed."
}

$nainLogDirectory = Join-Path $nainRoot '.tools/nainwrite-ollama'
$null = New-Item -ItemType Directory -Path $nainLogDirectory -Force
$nainRunId = [Guid]::NewGuid().ToString('N')
$nainStdout = Join-Path $nainLogDirectory "$nainRunId.stdout.log"
$nainStderr = Join-Path $nainLogDirectory "$nainRunId.stderr.log"
$nainProcess = $null
try {
    $nainProcess = Start-Process -FilePath $nainExecutable -ArgumentList 'serve' `
        -WorkingDirectory $nainRoot -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $nainStdout -RedirectStandardError $nainStderr `
        -Environment @{
            OLLAMA_HOST = "127.0.0.1:$nainPort"
            OLLAMA_NO_CLOUD = '1'
            OLLAMA_ORIGINS = 'http://127.0.0.1,http://localhost'
        }

    $nainReady = $false
    $nainDeadline = [DateTime]::UtcNow.AddSeconds(30)
    while ([DateTime]::UtcNow -lt $nainDeadline) {
        $nainProcess.Refresh()
        if ($nainProcess.HasExited) {
            throw 'Dedicated Ollama exited before verification. Inspect its local startup log.'
        }
        $nainListeners = @(Get-NetTCPConnection -State Listen -ErrorAction Stop |
            Where-Object LocalPort -eq $nainPort)
        if ($nainListeners.Count -gt 0) {
            if ($nainListeners.Count -ne 1 -or
                $nainListeners[0].LocalAddress -ne '127.0.0.1' -or
                $nainListeners[0].OwningProcess -ne $nainProcess.Id) {
                throw 'Unexpected listener address or process ownership; refusing readiness.'
            }
            $nainCloudDisabled = Select-String -LiteralPath $nainStderr `
                -Pattern 'Ollama cloud disabled:\s*true' -Quiet
            if ($nainCloudDisabled) {
                try {
                    $nainVersion = Invoke-RestMethod -Uri "http://127.0.0.1:$nainPort/api/version" `
                        -NoProxy -MaximumRedirection 0 -TimeoutSec 5
                } catch {
                    # Binding can precede HTTP readiness during a cold start.
                    Start-Sleep -Milliseconds 250
                    continue
                }
                if (-not $nainVersion.version) {
                    throw 'Ollama returned no version identity.'
                }
                $nainReady = $true
                break
            }
        }
        Start-Sleep -Milliseconds 250
    }
    if (-not $nainReady) {
        throw 'Dedicated Ollama readiness timed out; cloud-disabled startup was not established.'
    }
    [pscustomobject]@{
        Endpoint = "http://127.0.0.1:$nainPort"
        ProcessId = $nainProcess.Id
        StartedAt = $nainProcess.StartTime.ToUniversalTime().ToString('o')
        Executable = $nainExecutable
        Version = $nainVersion.version
        CloudDisabled = $true
        StartupLog = $nainStderr
    } | ConvertTo-Json
} catch {
    # Stop only the process created by this invocation, never an occupied-port owner.
    if ($null -ne $nainProcess) {
        $nainProcess.Refresh()
        if (-not $nainProcess.HasExited) {
            Stop-Process -InputObject $nainProcess -ErrorAction SilentlyContinue
        }
    }
    throw
}
