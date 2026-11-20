#Requires -Version 5.1
<#
.SYNOPSIS
    SHAH AI — Module 07 SEO & Keyword Research console launcher.

.DESCRIPTION
    Opens a small console menu for the SEO keyword research workbench, or
    dispatches a command to scripts/SEO-Keywords.py. Runs locally against
    data/keywords.csv. No external accounts, APIs or paid services; nothing is
    published or sent.

.PARAMETER Command
    A SEO-Keywords subcommand (list / search / cluster / local / report / etc.).
    Pass any full CLI argument list.

.EXAMPLE
    .\Start-SHAI-SEO.ps1 local
    .\Start-SHAI-SEO.ps1 report --out 07-seo-plan.md
#>

[CmdletBinding()]
$UserArgs = @() + $args

$ErrorActionPreference = "Stop"

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

$ScriptPath = Join-Path $RepoRoot "modules/07-seo-keyword-research/scripts/SEO-Keywords.py"

$Python = $null
try { $Python = Get-Command python3 -ErrorAction Stop } catch {}
if (-not $Python) { try { $Python = Get-Command python -ErrorAction Stop } catch {} }
if (-not $Python) {
    Write-Host "Python 3 was not found on PATH." -ForegroundColor Red
    exit 1
}

if ($UserArgs.Count -eq 0) {
    Write-Host "SHAH AI - SEO & Keyword Research" -ForegroundColor Cyan
    Write-Host "Run 'python scripts\SEO-Keywords.py -h' for all commands."
    exit 0
}

& $Python $ScriptPath @UserArgs
