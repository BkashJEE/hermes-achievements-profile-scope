[CmdletBinding()]
param(
    [string]$HermesDir,
    [switch]$Check,
    [switch]$Uninstall,
    [switch]$Yes
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$installer = Join-Path $scriptDir 'install.py'

if (-not $HermesDir) {
    if ($env:HERMES_AGENT_ROOT) {
        $HermesDir = $env:HERMES_AGENT_ROOT
    } else {
        $HermesDir = Join-Path $env:LOCALAPPDATA 'hermes\hermes-agent'
    }
}

$arguments = @($installer, '--hermes-dir', $HermesDir)
if ($Check) { $arguments += '--check' }
if ($Uninstall) { $arguments += '--uninstall' }
if ($Yes) { $arguments += '--yes' }

$venvPython = Join-Path $HermesDir 'venv\Scripts\python.exe'
if (Test-Path -LiteralPath $venvPython) {
    & $venvPython @arguments
    exit $LASTEXITCODE
}

$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) {
    & $py.Source -3 @arguments
    exit $LASTEXITCODE
}

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    & $python.Source @arguments
    exit $LASTEXITCODE
}

Write-Error 'Python was not found. Install Hermes Agent first, then try again.'
