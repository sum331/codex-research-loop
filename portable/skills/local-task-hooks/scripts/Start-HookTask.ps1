param(
    [string]$Name = "manual-task",
    [string]$WorkingDirectory = (Get-Location).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptRoot "HookLib.ps1")

$resolvedWorkingDirectory = (Resolve-Path -LiteralPath $WorkingDirectory).Path
$hookRoot = Join-Path $resolvedWorkingDirectory ".hook"
$runsRoot = Join-Path $hookRoot "runs"
$runName = "$(Get-HookTimestamp)-$(ConvertTo-HookSlug -Value $Name)"
$runDirectory = Join-Path $runsRoot $runName

New-Item -ItemType Directory -Force -Path $runDirectory | Out-Null

$snapshot = New-HookSnapshot -Name $Name -WorkingDirectory $resolvedWorkingDirectory
Write-HookSnapshotFiles -Snapshot $snapshot -RunDirectory $runDirectory
Write-HookCurrentRun -HookRoot $hookRoot -RunDirectory $runDirectory

Write-Output $runDirectory
