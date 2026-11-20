<#
.SYNOPSIS
  SHAH AI - Module 11 Unified Marketing Command Center launcher.

.DESCRIPTION
  Starts the Command-Center.py dashboard from a Windows terminal.
  No external APIs, no paid services, no network/analytics calls.
  Only local Python execution against project files.

.PARAMETER Cmd
  Optional commands forwarded to Command-Center.py:
    dashboard, status, modules, workflows, reports, exit

.EXAMPLE
  .\modules\11-marketing-command-center\Start-SHAI-Command-Center.ps1
  .\modules\11-marketing-command-center\Start-SHAI-Command-Center.ps1 status
  .\modules\11-marketing-command-center\Start-SHAI-Command-Center.ps1 workflows
#>

[CmdletBinding()]
param(
    [string[]]$Cmd = @()
)

$ErrorActionPreference = "Stop"

# Locate Python (prefer python3, then python, then py)
$Python = $null
foreach ($c in @("python3", "python", "py")) {
    $tmp = Get-Command $c -ErrorAction SilentlyContinue
    if ($tmp) {
        $Python = $tmp.Definition
        break
    }
}

if (-not $Python) {
    Write-Error "Python was not found. Install Python and ensure it is in PATH."
    exit 1
}

$ScriptDir = [System.IO.Path]::GetFullPath($PSScriptRoot)
$ProjectRoot = $ScriptDir
while (-not (Test-Path (Join-Path $ProjectRoot "modules\"))) {
    $Parent = Split-Path $ProjectRoot
    if ([string]::IsNullOrEmpty($Parent) -or $Parent -eq $ProjectRoot) { break }
    $ProjectRoot = $Parent
}
if (-not (Test-Path (Join-Path $ProjectRoot "modules\"))) {
    Write-Error "Could not resolve project root from script directory: $ScriptDir"
    exit 1
}
$Center = Join-Path $ProjectRoot "modules\11-marketing-command-center\scripts\Command-Center.py"

if (-not (Test-Path $Center)) {
    Write-Error "Command-Center.py was not found at $Center"
    exit 1
}

Write-Host "SHAH AI - Module 11 Unified Marketing Command Center" -ForegroundColor Cyan
Write-Host "Project root : $ProjectRoot"
Write-Host "Running     : $Python $Center"
if ($Cmd.Count -gt 0) {
    Write-Host "Command     : $($Cmd -join ' ')"
}
Write-Host ""

# Forward to Command-Center.py.  Empty $Cmd => dashboard.
& $Python $Center @Cmd
