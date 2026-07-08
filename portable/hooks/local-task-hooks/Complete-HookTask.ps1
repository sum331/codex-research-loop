param(
    [string]$RunDirectory = "",
    [int]$ExitCode = 0,
    [string]$Command = "",
    [string]$WorkingDirectory = (Get-Location).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptRoot "HookLib.ps1")

$resolvedWorkingDirectory = (Resolve-Path -LiteralPath $WorkingDirectory).Path
$hookRoot = Join-Path $resolvedWorkingDirectory ".hook"

if ([string]::IsNullOrWhiteSpace($RunDirectory)) {
    $RunDirectory = Get-HookCurrentRunDirectory -HookRoot $hookRoot
}

$summaryPath = Write-HookSummary -RunDirectory $RunDirectory -ExitCode $ExitCode -Command $Command
Write-Output $summaryPath
