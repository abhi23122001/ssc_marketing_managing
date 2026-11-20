<#
.SYNOPSIS
  SHAH AI - Module 13 Contractor Lead Intelligence launcher.

.DESCRIPTION
  Starts Lead-Intelligence.py from a Windows terminal.
  Read-only with respect to data/leads.csv. No external APIs, no paid
  services, no publishing, no lead contact.

.PARAMETER Cmd
  Optional commands forwarded to Lead-Intelligence.py:
    dashboard, score, prioritize, qualify, recommend, summary

.EXAMPLE
  .\modules\13-contractor-lead-intelligence\Start-SHAI-Lead-Intelligence.ps1
  .\modules\13-contractor-lead-intelligence\Start-SHAI-Lead-Intelligence.ps1 score
  .\modules\13-contractor-lead-intelligence\Start-SHAI-Lead-Intelligence.ps1 summary
#>

[CmdletBinding()]
param(
    [string[]]$Cmd = @()
)

$ErrorActionPreference = "Stop"

# Locate Python
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

# Launcher -> scripts; project root = three levels above the scripts dir
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

$Center = Join-Path $ProjectRoot "modules\13-contractor-lead-intelligence\scripts\Lead-Intelligence.py"
if (-not (Test-Path $Center)) {
    Write-Error "Lead-Intelligence.py was not found at $Center"
    exit 1
}

Write-Host "SHAH AI - Module 13 Contractor Lead Intelligence" -ForegroundColor Cyan
Write-Host "Project root : $ProjectRoot"
Write-Host "Running     : $Python $Center"
if ($Cmd.Count -gt 0) {
    Write-Host "Command     : $($Cmd -join ' ')"
}
Write-Host ""

# Default = dashboard when no arg is given
& $Python $Center @Cmd
