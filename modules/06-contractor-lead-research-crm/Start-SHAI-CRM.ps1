#Requires -Version 5.1
<#
.SYNOPSIS
    SHAH AI - Module 06 Contractor Lead Research & CRM console launcher.

.DESCRIPTION
    Opens a small console menu for the lead CRM, or dispatches a command to
    scripts/CRM-Leads.py. Runs locally against data/leads.csv. No external
    accounts, APIs or paid services; nothing is published or sent.

.PARAMETER Command
    A CRM subcommand (list / dashboard / validate / backup / search / etc.) to
    run directly. Pass any full CRM argument list.

.EXAMPLE
    .\Start-SHAI-CRM.ps1 dashboard
    .\Start-SHAI-CRM.ps1 add --company "Auranga" --website "https://auranga.in" --city "Meera"
#>

[CmdletBinding()]
$UserArgs = @() + $args

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

$ScriptPath = Join-Path $RepoRoot "modules/06-contractor-lead-research-crm/scripts/CRM-Leads.py"

$Python = $null
try { $Python = Get-Command python3 -ErrorAction Stop } catch {}
if (-not $Python) { try { $Python = Get-Command python -ErrorAction Stop } catch {} }
if (-not $Python) {
    Write-Host "Python 3 was not found on PATH." -ForegroundColor Red
    exit 1
}

if ($UserArgs.Count -eq 0) {
    Write-Host "SHAH AI - Contractor Lead CRM" -ForegroundColor Cyan
    Write-Host 'Run python scripts\CRM-Leads.py -h for all commands.'
    exit 0
}

& $Python $ScriptPath @UserArgs
