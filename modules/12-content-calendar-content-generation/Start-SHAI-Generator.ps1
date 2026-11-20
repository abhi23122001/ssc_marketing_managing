#Requires -Version 5.1
<#
.SYNOPSIS
  SHAH AI - Module 12 Content Calendar & Content Generation launcher.

.DESCRIPTION
  Starts the Module 12 content calendar and content generator from a Windows
  terminal. Local, read-write operations only (data/m12-content-calendar.csv
  and outputs/12). No external APIs, no paid services, no publishing.

.PARAMETER Cmd
  Optional commands forwarded to ContentCalendar.py / ContentGenerator.py:
    list, view, add, export, validate, integrity-check, generate-all, generate-one
#>

[CmdletBinding()]
param(
    [string[]]$Cmd = @()
)

$ErrorActionPreference = "Stop"

# Resolve the repository root (walk up to the folder containing 'modules').
function Find-RepoRoot {
    $current = $PSScriptRoot
    while ($current) {
        if (Test-Path (Join-Path $current "modules")) {
            return $current
        }
        $parent = Split-Path -Parent $current
        if ($parent -eq $current) { break }
        $current = $parent
    }
    return $null
}

$RepoRoot = Find-RepoRoot
if (-not $RepoRoot) {
    Write-Host "Could not locate the SHAH AI repository root." -ForegroundColor Red
    exit 1
}

$ScriptPath = Join-Path $RepoRoot "modules/12-content-calendar-content-generation/scripts/ContentCalendar.py"
$Generator  = Join-Path $RepoRoot "modules/12-content-calendar-content-generation/scripts/ContentGenerator.py"

$Python = $null
try { $Python = Get-Command python3 -ErrorAction Stop } catch {}
if (-not $Python) { try { $Python = Get-Command python -ErrorAction Stop } catch {} }
if (-not $Python) {
    Write-Host "Python 3 was not found on PATH." -ForegroundColor Red
    exit 1
}

if ($Cmd.Count -eq 0) {
    Write-Host "SHAH AI - Module 12 Content Calendar & Content Generation" -ForegroundColor Cyan
    Write-Host "Project root : $RepoRoot"
    Write-Host "Commands: list, view, add, export, validate, integrity-check, generate-all, generate-one"
    exit 0
}

& $Python $ScriptPath @Cmd
