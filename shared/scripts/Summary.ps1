# SHAH AI — Module 01 Task & Approval Summary
# ----------------------------------------------------------
# Creates a readable summary of open tasks and approvals from the task board.
# Used by the Module 01 command center dashboard.
#
# Usage:
#   .\shared\scripts\Summary.ps1 [-Filter <module-id>] [-Status <status>] [-NoHeader]
#
# Example:
#   .\shared\scripts\Summary.ps1 -Filter "01-marketing-command-center"
#   .\shared\scripts\Summary.ps1 -Status "DRAFT" -NoHeader

param(
    [string]$Filter,
    [string]$Status,
    [switch]$NoHeader
)

$csvPath = Join-Path $PSScriptRoot "..\..\data\status-tasks.csv"

if (-not (Test-Path $csvPath)) {
    Write-Host "Task board not found at $csvPath"
    exit
}

$rows = Import-Csv -Path $csvPath

if ($Filter) { $rows = $rows | Where-Object { $_.module -like "*$Filter*" } }
if ($Status) { $rows = $rows | Where-Object { $_.status -eq $Status } }

$open = @($rows | Where-Object { $_.status -in "DRAFT","PENDING" })

if (-not $NoHeader) {
    Write-Host "=== SHAH AI - Open tasks and approvals ==="
    Write-Host "Open tasks: $($open.Count)"
    Write-Host "Status legend: DRAFT = needs owner review ; APPROVED = ready for scheduled action"
    Write-Host "--------------------------------------------------------------"
}
if ($open.Count -eq 0) {
    Write-Host "(no open tasks)"
} else {
    $open | ForEach-Object {
        Write-Host "[$($_.task_id)] $($_.module) - $($_.description)"
        Write-Host "   status=$($_.status)  approval_record=$($_.approval_record)"
    }
}
