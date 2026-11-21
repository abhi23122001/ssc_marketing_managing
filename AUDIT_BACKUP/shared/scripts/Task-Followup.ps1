#Requires -Version 5.1
<#
.SYNOPSIS
  SHAH AI - Shared Task & Follow-up view (consolidation).

.DESCRIPTION
  Single Windows console view over:
    (a) open tasks/approvals from data/status-tasks.csv
    (b) contractor lead follow-up due / overdue from data/leads.csv (via CRM logic)

  Consolidates the previous "Task & Follow-up" areas into one script. No external
  APIs, no publishing, no contacting, no spending. Draft-only.

.PARAMETER Filter
  Optional module-id filter for the task board.
.PARAMETER Status
  Optional status filter (e.g. DRAFT).
.PARAMETER LeadFilter
  Optional substring filter to show only leads whose company matches.
#>

[CmdletBinding()]
param(
    [string]$Filter,
    [string]$Status,
    [string]$LeadFilter
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

$TasksCsv = [System.IO.Path]::Combine($RepoRoot, "data", "status-tasks.csv")
$LeadsCsv = [System.IO.Path]::Combine($RepoRoot, "data", "leads.csv")

function Show-Tasks {
    param([string]$Filter, [string]$Status)
    if (-not (Test-Path $TasksCsv)) {
        Write-Host "Task board not found at $TasksCsv" -ForegroundColor Yellow
        return
    }
    $rows = Import-Csv -Path $TasksCsv
    if ($Filter) { $rows = $rows | Where-Object { $_.module -like "*$Filter*" } }
    if ($Status) { $rows = $rows | Where-Object { $_.status -eq $Status } }
    $open = @($rows | Where-Object { $_.status -in "DRAFT", "PENDING" })
    Write-Host "=== SHAH AI - Open tasks and approvals ==="
    Write-Host "Open tasks: $($open.Count)"
    if ($open.Count -eq 0) { Write-Host "(no open tasks)" } else {
        $open | ForEach-Object {
            Write-Host "  [$($_.task_id)] $($_.module) - $($_.description)"
            Write-Host "     status=$($_.status)  approval_record=$($_.approval_record)"
        }
    }
}

function Show-LeadsFollowup {
    param([string]$LeadFilter)
    if (-not (Test-Path $LeadsCsv)) {
        Write-Host "Lead data not found at $LeadsCsv" -ForegroundColor Yellow
        return
    }
    $rows = Import-Csv -Path $LeadsCsv
    $rows = $rows | Where-Object {
        if ($LeadFilter) { $_.company -like "*$LeadFilter*" } else { $true }
    }
    $today = Get-Date
    $due = @($rows | Where-Object {
        $fu = $_.follow_up_date
        if (-not $fu) { return $false }
        try {
            $fuDate = [datetime]::ParseExact($fu, "yyyy-MM-dd", $null)
        } catch {
            return $false
        }
        $stage = $_.stage
        return $fuDate -le $today -and $stage -notin @("Customer", "Disqualified")
    })
    Write-Host ""
    Write-Host "=== SHAH AI - Lead follow-up (due / overdue) ==="
    if ($due.Count -eq 0) { Write-Host "(no follow-up due)" } else {
        $due | ForEach-Object {
            $fu = $_.follow_up_date
            try { $fuDate = [datetime]::ParseExact($fu, "yyyy-MM-dd", $null) }
            catch { $fuDate = Get-Date }
            $relative = switch ($fuDate.CompareTo($today)) {
                -1 { "OVERDUE ($( [datetime]::Now.Subtract($fuDate).Days ) days ago)" }
                0 { "DUE TODAY" }
                1 { "in $(( $fuDate - $today).Days) days" }
            }
            Write-Host "  [$($_.company)] follow-up $fu  $relative"
        }
    }
}

Write-Host "SHAH AI - Task & Follow-up (consolidation view)" -ForegroundColor Cyan
if ($Filter -or $Status) { Show-Tasks -Filter $Filter -Status $Status }
if ($LeadFilter -or (-not $Filter -and -not $Status)) { Show-LeadsFollowup -LeadFilter $LeadFilter }
if (-not $Filter -and -not $Status -and -not $LeadFilter) {
    Show-Tasks
    Show-LeadsFollowup
}
