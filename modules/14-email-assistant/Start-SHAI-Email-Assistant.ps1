#Requires -Version 5.1
<#
.SYNOPSIS
  SHAH AI - Module 14 Email Assistant launcher.

.DESCRIPTION
  Starts the Email Assistant from a Windows terminal. Draft-only and read-only:
  it analyses email files (or pasted text) and produces classification,
  summary, priority, follow-up and bilingual drafts. It never sends email.
  Gmail OAuth sync is disabled by default and requires a token.json that lives
  OUTSIDE this repository, plus explicit owner approval.

.PARAMETER Cmd
  Optional commands forwarded to EmailAssistant.py:
    analyze, classify, summary, priority, follow-up, bilingual, dry-run
#>

[CmdletBinding()]
param(
    [string[]]$Cmd = @()
)

$ErrorActionPreference = "Stop"

function Find-RepoRoot {
    $current = $PSScriptRoot
    while ($current) {
        if (Test-Path (Join-Path $current "modules")) { return $current }
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

$ScriptPath = Join-Path $RepoRoot "modules/14-email-assistant/scripts/EmailAssistant.py"

$Python = $null
try { $Python = Get-Command python3 -ErrorAction Stop } catch {}
if (-not $Python) { try { $Python = Get-Command python -ErrorAction Stop } catch {} }
if (-not $Python) {
    Write-Host "Python 3 was not found on PATH." -ForegroundColor Red
    exit 1
}

if ($Cmd.Count -eq 0) {
    Write-Host "SHAH AI - Module 14 Email Assistant (draft-only)" -ForegroundColor Cyan
    Write-Host "Project root : $RepoRoot"
    Write-Host "Commands: analyze, classify, summary, priority, follow-up, bilingual, dry-run"
    Write-Host "Read-only. No email is sent."
    exit 0
}

& $Python $ScriptPath @Cmd
