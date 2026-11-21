#Requires -Version 5.1
<#
.SYNOPSIS
    SHAH AI Marketing Management System — Command Center launcher.

.DESCRIPTION
    Opens the central project dashboard (COMMAND-CENTER.md) and provides a
    simple console menu to jump straight to any of the 10 modules. This
    launcher only opens local markdown files. It does not publish, schedule,
    message, contact leads, connect accounts, or spend money.

.PARAMETER Module
    A number from 1 to 10 to open a specific module directly.
.PARAMETER OpenDashboard
    Open the central dashboard (COMMAND-CENTER.md) even when a module is
    already visible.

.EXAMPLE
    .\Start-SHAI-Center.ps1
    Opens the dashboard with the module menu.

.EXAMPLE
    .\Start-SHAI-Center.ps1 -Module 3
    Opens the Instagram / Facebook Content Studio README.
#>

[CmdletBinding()]
param(
    [Parameter()]
    [ValidateRange(0, 10)]
    [int]$Module = 0,

    [Parameter()]
    [switch]$OpenDashboard
)

$ErrorActionPreference = "Stop"

# Resolve the repository root from this script's location.
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ScriptRoot) { $ScriptRoot = $PSScriptRoot }
if (-not $ScriptRoot) { $ScriptRoot = (Get-Location).Path }

$CenterFile  = Join-Path $ScriptRoot "COMMAND-CENTER.md"
$ModulesDir  = Join-Path $ScriptRoot "modules"

# ---- Helpers ---------------------------------------------------------------

function Write-Banner([string]$Title) {
    $Line = "═" * 52
    Write-Host $Line
    Write-Host ("  $Title".PadRight(52))
    Write-Host $Line
}

function Write-Section([string]$Text) {
    Write-Host ""
    Write-Host "  ─────────────────────────────────────────"
    Write-Host "  $Text"
    Write-Host "  ─────────────────────────────────────────"
}

function Get-ModuleList {
    if (-not (Test-Path $ModulesDir)) { return @() }
    return @(Get-ChildItem -Path $ModulesDir -Directory | Sort-Object Name)
}

function Show-Menu {
    Write-Banner " SHAH AI MARKETING MANAGEMENT SYSTEM "
    Write-Section " Open the central dashboard: COMMAND-CENTER.md "

    $Modules = Get-ModuleList
    Write-Section " MODULE NAVIGATION "
    Write-Host "  [0]  Open project dashboard"
    for ($i = 0; $i -lt $Modules.Count; $i++) {
        $Name = Split-Path -Leaf $Modules[$i].FullName
        $DisplayName = $Name
        if ($Name -match "^\d+_(.*)") { $DisplayName = $Matches[1] }
        Write-Host "  [$($i + 1)]  $DisplayName"
    }
    Write-Section " Other"
    Write-Host "  [M]  Refresh menu"
    Write-Host "  [Q]  Quit"
    Write-Host ""

    $Choice = Read-Host " Select a module (0, 1-10), M, or Q"
    if (-not $Choice) { $Choice = "0" }
    return $Choice
}

function Open-File([string]$Path) {
    if (Test-Path $Path) {
        try {
            Start-Process (Resolve-Path $Path).Path
            return $true
        } catch {
            Write-Host ("  Unable to open: {0}" -f $Path) -ForegroundColor Yellow
            return $false
        }
    } else {
        Write-Host ("  File not found: {0}" -f $Path) -ForegroundColor Red
        return $false
    }
}

# ---- Dispatch ----------------------------------------------------------------

$CenterAlreadyOpen = $false

if ($Module -ge 1 -and $Module -le 10) {
    $ModuleDir = Join-Path $ModulesDir ("{0:00}" -f $Module)
    $ModFile   = Join-Path $ModuleDir "README.md"
    Open-File $ModFile
    exit 0
}

if ($OpenDashboard -or -not (Test-Path $CenterFile)) {
    Open-File $CenterFile
    $CenterAlreadyOpen = $true
}

do {
    $Choice = Show-Menu
    switch ($Choice.Trim().ToUpperInvariant()) {
        "0" {
            if (-not $CenterAlreadyOpen) {
                Open-File $CenterFile
                $CenterAlreadyOpen = $true
            } else {
                Write-Host "  Dashboard already open." -ForegroundColor Yellow
            }
        }
        { $_ -match "^[1-9]$" -and $Modules.Count -ge [int]$_ } {
            $Idx   = [int]$_ - 1
            $ModFile = Join-Path $Modules[$Idx].FullName "README.md"
            Open-File $ModFile
        }
        "M" {
            # Loop re-runs Show-Menu, effectively refreshing the menu.
        }
        "Q" {
            Write-Host "  Goodbye." -ForegroundColor Green
            exit 0
        }
        default {
            Write-Host ("  Unknown choice: {0}" -f $Choice) -ForegroundColor Yellow
        }
    }
} while ($Choice.Trim().ToUpperInvariant() -ne "Q")
