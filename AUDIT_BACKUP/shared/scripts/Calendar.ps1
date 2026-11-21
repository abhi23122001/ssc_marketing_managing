# SHAH AI — Module 02 Content Calendar
# ----------------------------------------------------------
# Console views over data/content-calendar.csv.
#
# Usage:
#   .\shared\scripts\Calendar.ps1 [-Days 7] [-View daily|weekly|monthly|next]
#
# Examples:
#   .\shared\scripts\Calendar.ps1 -View daily -Days 7
#   .\shared\scripts\Calendar.ps1 -View weekly
#   .\shared\scripts\Calendar.ps1 -View monthly

param(
    [int]$Days = 7,
    [string]$View = "daily"
)

$csvPath = Join-Path $PSScriptRoot "..\..\data\content-calendar.csv"

if (-not (Test-Path $csvPath)) {
    Write-Host "Content calendar not found at $csvPath"
    exit
}

$rows = Import-Csv -Path $csvPath

# Skip sample/ADMIN header rows
$rows = $rows | Where-Object { $_.date_proposal -notlike "#*" }

function Get-WeekNumber {
    param([DateTime]$d)
    $cal = [System.Globalization.CultureInfo]::InvariantCulture.Calendar
    $week = $cal.GetWeekOfYear($d, [System.Globalization.CalendarWeekRule]::FirstFourDayWeek, [DayOfWeek]::Monday)
    return "$($d.Year)-W$($week.ToString('00'))"
}

function Get-View {
    param([string]$View, [int]$Days)
    $now = Get-Date
    switch ($View) {
        "daily" {
            $dates = @()
            for ($i = 0; $i -le $Days; $i++) {
                $dates += Get-WeekNumber -d ($now.AddDays($i))
            }
            $rows | Where-Object { $dates -contains $_.date_proposal } |
                Sort-Object date_proposal
        }
        "weekly" {
            $start = $now.AddDays(-($now.DayOfWeek.value__ - 1))
            $rows | Where-Object { $_.date_proposal -ge (Get-WeekNumber -d $start) } |
                Sort-Object date_proposal
        }
        "monthly" {
            $rows | Group-Object date_proposal |
                Sort-Object name | Select-Object -First $Days
        }
        "next" {
            $rows | Where-Object { $_.status -in "DRAFT","PENDING" } |
                Sort-Object date_proposal
        }
        default { $rows | Sort-Object date_proposal }
    }
}

$table = Get-View -View $View -Days $Days

if ($table.Count -eq 0) {
    Write-Host "No planned items for this view."
} else {
    if ($View -eq "monthly") {
        $table | Format-Table -AutoSize
    } else {
        Write-Host "Planned items (view=$View days=$Days):"
        $table | Format-Table date_proposal, platform, content_pillar, topic, format, language, status -AutoSize
    }
}
Write-Host ""
Write-Host "Open pending items: $($rows.date_proposal.Count)"
