#Requires -Version 5.1
<#
.SYNOPSIS
    Open a markdown file in the default viewer.

.DESCRIPTION
    Opens an existing .md file using the Windows default application.
    Used by the command center menu and module launchers.

.PARAMETER Path
    Path to the markdown file to open.

.EXAMPLE
    .\Open-Readme.ps1 -Path ".\modules\03-instagram-facebook-content-studio\README.md"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Path
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $Path)) {
    Write-Host ("File not found: {0}" -f $Path) -ForegroundColor Red
    exit 1
}

try {
    Start-Process (Resolve-Path $Path).Path
} catch {
    Write-Host ("Unable to open: {0}" -f $Path) -ForegroundColor Yellow
    exit 1
}
