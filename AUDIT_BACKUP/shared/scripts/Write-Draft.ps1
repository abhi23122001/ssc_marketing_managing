#Requires -Version 5.1
<#
.SYNOPSIS
    Create a draft content file with a standard SHAH AI header.

.DESCRIPTION
    Creates a markdown draft under <repo>/outputs/ with a standard header
    (status: DRAFT, approval required) and the owner-supplied content.

.PARAMETER ModuleName
    Short module name used in the file name. Required.
.PARAMETER Title
    Draft title. Required.
.PARAMETER Language
    Language tag for the file extension (en / hi / hin). Default en.
.PARAMETER Content
    Body content. If empty, the file is created with the standard header
    and a place-holder so the owner can fill it.

.EXAMPLE
    .\Write-Draft.ps1 -ModuleName "04-linkedin" -Title "Survey planning" -Language en -Content "Draft copy..."
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$ModuleName,
    [Parameter(Mandatory)]
    [string]$Title,
    [string]$Language = "en",
    [string]$Content = ""
)

$ErrorActionPreference = "Stop"

# Resolve repository root.
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ScriptRoot) { $ScriptRoot = $PSScriptRoot }
if (-not $ScriptRoot) { $ScriptRoot = (Get-Location).Path }

$RootSearch = Split-Path $ScriptRoot -Parent
while ($RootSearch -and -not (Test-Path (Join-Path $RootSearch "modules"))) {
    $RootSearch = Split-Path $RootSearch -Parent
}
if (-not $RootSearch) {
    Write-Host "Could not locate repository root." -ForegroundColor Red
    exit 1
}
$RepoRoot = $RootSearch

# Build the outputs directory (gitignored).
$OutputsDir = Join-Path $RepoRoot "outputs"
if (-not (Test-Path $OutputsDir)) {
    New-Item -ItemType Directory -Path $OutputsDir -Force | Out-Null
}

# Build a safe file name.
$SafeTitle = ($Title -replace "[^\w\s-]", "" -replace "\s+", "-").Trim("-")
$FileName  = ("{0}-{1}.{2}.md" -f $ModuleName, $SafeTitle, $Language)
$OutFile   = Join-Path $OutputsDir $FileName

# Standard draft header.
$Header = @"

---
status: DRAFT
source: Start-SHAI-Center.ps1 / Write-Draft.ps1
approval_required: yes
module: $ModuleName
---

"@

$Body = if ($Content) { $Content } else {
    @"
(Please fill this draft. Keep it marked as DRAFT until an explicit
owner approval record is completed for publication.)
"@
}

$Full = $Header + $Body

try {
    $Full | Out-File -FilePath $OutFile -Encoding UTF8 -NoNewline
    Write-Host ("Draft written: {0}" -f $OutFile) -ForegroundColor Green
} catch {
    Write-Host ("Could not write draft: {0}" -f $_.Exception.Message) -ForegroundColor Red
    exit 1
}
