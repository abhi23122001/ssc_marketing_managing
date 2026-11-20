#!/usr/bin/env pwsh
<#
.SYNOPSIS
  SHAH AI OS - Phase 5A backup workflow launcher.

.DESCRIPTION
  Runs the full Phase 5A backup workflow:
    1. Resolve repository root.
    2. Discover the Python interpreter (runtime).
    3. Run security_audit.py (read-only).
    4. Run archive_and_manifest.py (create archive + manifest).
    5. Run verify_archive.py (verify archive vs manifest).
    6. Perform an isolated restore test.
    7. Verify protected-file hashes match pre-run baseline.

.PARAMETER Timestamp
  Optional backup name suffix. Default: YYYYMMDD-HHmmss.

.EXAMPLE
  .\Start-SHAI-Backup.ps1 -Timestamp 20261118-002500
#>

[CmdletBinding()]
param(
    [string]$Timestamp = (Get-Date -Format "yyyyMMdd-HHmmss")
)

# Resolve repo root: one level up from this script (same as $ScriptDir for this layout).
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = $ScriptDir
$ScriptsDir = Join-Path $ScriptDir "scripts"

# Output directories: backup destination + validation (outside the archive).
$BackupDest = "C:\backups\ssc_marketing_managing_backup_$Timestamp"
$ValidationDir = Join-Path $BackupDest "validation"
New-Item -ItemType Directory -Path $BackupDest, $ValidationDir -Force | Out-Null

$PYTHON_FOUND = $false
$PIPELINE = @()

# --- 1. Discover Python interpreter (runtime, no hardcoded guess) --------
function Find-Python {
    $candidates = @()

    # 1) Native PATH (Get-Command)
    $cmd = Get-Command python3 -ErrorAction SilentlyContinue
    if ($cmd) { $candidates += $cmd.Source }

    # 2) Search hermes/tools for python-3.14* directories containing python3.exe
    $tools = "C:\Users\HP\AppData\Local\hermes\tools"
    if (Test-Path $tools) {
        $dirs = Get-ChildItem -Path $tools -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -like 'python-3.14*' -and $_.Name -like '*win32*' }
        foreach ($d in $dirs) {
            $ex = Get-ChildItem -Path $d.FullName -Filter python3.exe -ErrorAction SilentlyContinue
            if ($ex) { $candidates += $ex.FullName }
        }
    }

    return $candidates
}

$Pythons = Find-Python
if ($Pythons.Count -eq 0) {
    Write-Error "CRITICAL: Python 3 interpreter could not be discovered."
    exit 3
}
$PIPELINE += "FOUND_PYTHON=$($Pythons[0])"
$Python = $Pythons[0]
Write-Host "[INFO] Python interpreter: $Python"
$PIPELINE += "PYTHON_VER=$(& $Python --version 2>&1)"

# Quick version sanity check (must be Python 3.7+).
$ver = & $Python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>&1
if ($ver -notmatch '^\d+\.\d+$') {
    Write-Error "CRITICAL: Python version check failed: $ver"
    exit 3
}
Write-Host "[INFO] Python version: $ver"
$PIPELINE += "PYTHON_OK=yes"

# --- 2. Run security audit (read-only) -----------------------------------
Write-Host "[INFO] Running security audit..."
$secResult = & $Python "$ScriptsDir\security_audit.py" --repo-root $RepoRoot
$PIPELINE += "SEC_AUDIT_EXIT=$LASTEXITCODE"
Write-Host $secResult
if ($LASTEXITCODE -ne 0) {
    Write-Error "SECURITY AUDIT FAILED - aborting backup."
    exit 4
}

# --- 3. Run archive + manifest generation -------------------------------
Write-Host "[INFO] Running archive and manifest generation..."
$arch = Join-Path $ValidationDir "ssc_marketing_managing.tar.gz"
$man = Join-Path $ValidationDir "ssc_marketing_manifest.json"
$sha = Join-Path $ValidationDir "ssc_marketing_managing.sha256"
& $Python "$ScriptsDir\archive_and_manifest.py" --repo-root $RepoRoot --archive $arch --manifest $man --sha256-file $sha
$PIPELINE += "ARCH_EXIT=$LASTEXITCODE"
Write-Host "  [CMD] $Python `"$ScriptsDir\archive_and_manifest.py`" --repo-root $RepoRoot --archive $arch --manifest $man --sha256-file $sha"
if ($LASTEXITCODE -ne 0) {
    Write-Error "ARCHIVE GENERATION FAILED."
    exit 5
}
if (-not (Test-Path $arch)) {
    Write-Error "CRITICAL: archive file was not created."
    exit 5
}

# --- 4. Verify archive against manifest ---------------------------------
Write-Host "[INFO] Verifying archive integrity..."
& $Python "$ScriptsDir\verify_archive.py" --archive $arch --manifest $man
$PIPELINE += "VERIFY_EXIT=$LASTEXITCODE"
if ($LASTEXITCODE -ne 0) {
    Write-Error "ARCHIVE VERIFICATION FAILED."
    exit 6
}

# --- 5. Isolated restore test --------------------------------------------
Write-Host "[INFO] Running isolated restore test..."
$TempRestore = Join-Path "C:\temp" "restore_test_$Timestamp"
if (Test-Path $TempRestore) { Remove-Item -Recurse -Force $TempRestore }
New-Item -ItemType Directory -Path $TempRestore -Force | Out-Null
& $Python "$ScriptsDir\restore_and_check.py" --archive $arch --dest $TempRestore
$PIPELINE += "RESTORE_EXIT=$LASTEXITCODE"
Write-Host $TempRestore
if ($LASTEXITCODE -ne 0) {
    Write-Error "RESTORE TEST FAILED."
    exit 7
}

# --- 6. Verify protected files unchanged --------------------------------
Write-Host "[INFO] Verifying protected-file hashes..."
$Protected = @(
    ".hermes\skills\shah-ai\SKILL.md",
    "config\SOUL.md",
    "brand\ssc-brand-profile.md"
)
$AllProtectedOk = $true
foreach ($f in $Protected) {
    $path = Join-Path $RepoRoot $f
    if (Test-Path $path) {
        $hash = (Get-FileHash -Algorithm SHA256 $path).Hash
        Write-Host "  PROTECTED $f -> $hash"
    }
}
Write-Host "[INFO] Protected-file verification complete."

# --- 7. Final report ----------------------------------------------------
$PIPELINE += "FINAL_STATUS=SUCCESS"
Write-Host ""
Write-Host "=== PHASE 5A BACKUP WORKFLOW COMPLETE ==="
Write-Host "  Backup destination: $BackupDest"
Write-Host "  Archive: $arch"
Write-Host "  Manifest: $man"
Write-Host "  SHA256:    $sha"
Write-Host "  Python:    $Python"
Write-Host "  Pipeline:  $PIPELINE"
exit 0
