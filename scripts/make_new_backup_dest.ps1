<#
.SHORT
Create new timestamped backup destination
#>
$now = Get-Date -Format 'yyyyMMdd-HHmmss'
$dest = 'C:\backups\ssc_marketing_managing_backup_20261118-' + $now
New-Item -ItemType Directory -Path $dest -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $dest 'validation') -Force | Out-Null
Write-Host "Backup destination: $dest"
Write-Host "Created backup destination"
