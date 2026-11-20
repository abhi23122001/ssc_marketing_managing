#!/usr/bin/env pwsh
<#
.SYNOPSIS
  SHAH AI OS - Phase 5A isolated restore-test launcher.

.DESCRIPTION
  Runs an isolated restore test:
    1. Discover Python interpreter.
    2. Create a fresh temporary restore directory.
    3. Run restore_and_check.py --archive <archive> --dest <temp>.
    4. Report final status.

.PARAMETER Archive
  Path to the backup archive (.tar.gz) to restore.

.EXAMPLE
  .\Start-SHAI-Restore-Test.ps1 -Archive .\validation\ssc_marketing_managing.tar.gz
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Archive,

    [string]$Timestamp = (Get-Date -Format "yyyyMMdd-HHmmss")
)

$RepoRoot = "C:\Users\HP\Desktop\ssc_marketing_managing"
$ScriptsDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Discover Python interpreter.
$Python = $null
$cmd = Get-Command python3 -ErrorAction SilentlyContinue
if ($cmd) { $Python = $cmd.Source }

if (-not $Python) {
    $tools = "C:\Users\HP\AppData\Local\hermes\tools"
    if (Test-Path $tools) {
        $dirs = Get-ChildItem -Path $tools -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -like 'python-3.14*' -and $_.Name -like '*win32*' }
        foreach ($d in $dirs) {
            $ex = Get-ChildItem -Path $d.FullName -Filter python3.exe -ErrorAction SilentlyContinue
            if ($ex) { $Python = $ex.FullName; break }
        }
    }
}

if (-not $Python -or -not (Test-Path $Python)) {
    Write-Error "CRITICAL: Python 3 interpreter could not be discovered."
    exit 3
}

Write-Host "[INFO] Python interpreter: $Python"
$ver = & $Python --version 2>&1
Write-Host "[INFO] Python version: $ver"

if (-not (Test-Path $Archive)) {
    Write-Error "CRITICAL: archive not found: $Archive"
    exit 3
}

# Create fresh temp restore directory.
$TempRestore = Join-Path "C:\temp" "restore_test_$Timestamp"
if (Test-Path $TempRestore) { Remove-Item -Recurse -Force $TempRestore }
New-Item -ItemType Directory -Path $TempRestore -Force | Out-Null

Write-Host "[INFO] Running isolated restore test into: $TempRestore"
& $Python "$ScriptsDir\restore_and_check.py" --archive $Archive --dest $TempRestore
$LAST = $LASTEXITCODE

Write-Host "RESTORE TEST: exit=$LAST"
if ($LAST -ne 0) {
    Write-Error "RESTORE TEST FAILED."
    exit 7
}

Write-Host "=== RESTORE TEST PASSED ==="
exit 0
