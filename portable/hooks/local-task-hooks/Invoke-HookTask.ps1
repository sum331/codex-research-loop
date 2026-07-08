param(
    [Parameter(Mandatory = $true)]
    [string]$Command,

    [string]$Name = "task",

    [ValidateSet("powershell", "cmd")]
    [string]$Shell = "powershell",

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
$stdoutPath = Join-Path $runDirectory "stdout.log"
$stderrPath = Join-Path $runDirectory "stderr.log"
$startedAt = Get-Date
$exitCode = 1

New-Item -ItemType Directory -Force -Path $runDirectory | Out-Null

try {
    $snapshot = New-HookSnapshot -Name $Name -WorkingDirectory $resolvedWorkingDirectory
    Write-HookSnapshotFiles -Snapshot $snapshot -RunDirectory $runDirectory
    Write-HookCurrentRun -HookRoot $hookRoot -RunDirectory $runDirectory

    if ($Shell -eq "cmd") {
        $filePath = "cmd.exe"
        $argumentList = @("/d", "/s", "/c", $Command)
    }
    else {
        $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($Command))
        $filePath = "powershell.exe"
        $argumentList = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-EncodedCommand", $encoded)
    }

    $process = Start-Process `
        -FilePath $filePath `
        -ArgumentList $argumentList `
        -WorkingDirectory $resolvedWorkingDirectory `
        -NoNewWindow `
        -PassThru `
        -Wait `
        -RedirectStandardOutput $stdoutPath `
        -RedirectStandardError $stderrPath

    $exitCode = $process.ExitCode
}
catch {
    $exitCode = 1
    $_.Exception.ToString() | Set-Content -LiteralPath $stderrPath -Encoding UTF8
    if (Test-Path -LiteralPath (Join-Path $runDirectory "pre-snapshot.json")) {
        Write-HookFailure -RunDirectory $runDirectory -ExitCode $exitCode -Command $Command -ErrorMessage $_.Exception.Message | Out-Null
    }
    else {
        Write-HookSetupFailure -RunDirectory $runDirectory -Command $Command -ErrorMessage $_.Exception.Message | Out-Null
    }
}
finally {
    $endedAt = Get-Date

    if ($exitCode -ne 0 -and (Test-Path -LiteralPath (Join-Path $runDirectory "pre-snapshot.json"))) {
        Write-HookFailure -RunDirectory $runDirectory -ExitCode $exitCode -Command $Command | Out-Null
    }

    if (Test-Path -LiteralPath (Join-Path $runDirectory "pre-snapshot.json")) {
        Write-HookSummary -RunDirectory $runDirectory -ExitCode $exitCode -Command $Command -StartedAt $startedAt -EndedAt $endedAt | Out-Null
    }
}

Write-Host "Hook run: $runDirectory"
Write-Host "Summary:  $(Join-Path $runDirectory 'summary.md')"
if ($exitCode -ne 0) {
    Write-Host "Failure:  $(Join-Path $runDirectory 'failure.md')"
}

exit $exitCode
