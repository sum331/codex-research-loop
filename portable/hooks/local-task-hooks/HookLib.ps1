Set-StrictMode -Version Latest

function Get-HookTimestamp {
    return (Get-Date).ToString("yyyyMMdd-HHmmss")
}

function ConvertTo-HookSlug {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Value
    )

    $slug = $Value.ToLowerInvariant() -replace '[^a-z0-9._-]+', '-'
    $slug = $slug.Trim('-')
    if ([string]::IsNullOrWhiteSpace($slug)) {
        return "task"
    }

    if ($slug.Length -gt 48) {
        return $slug.Substring(0, 48).Trim('-')
    }

    return $slug
}

function Invoke-HookNative {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,

        [string[]]$ArgumentList = @(),

        [Parameter(Mandatory = $true)]
        [string]$WorkingDirectory
    )

    $previous = Get-Location
    try {
        Set-Location -LiteralPath $WorkingDirectory
        $output = & $FilePath @ArgumentList 2>&1
        $exitCode = $LASTEXITCODE
        return [pscustomobject]@{
            ExitCode = $exitCode
            Output = @($output)
        }
    }
    catch {
        return [pscustomobject]@{
            ExitCode = 1
            Output = @($_.Exception.Message)
        }
    }
    finally {
        Set-Location -LiteralPath $previous
    }
}

function Get-HookGitInfo {
    param(
        [Parameter(Mandatory = $true)]
        [string]$WorkingDirectory
    )

    $inside = Invoke-HookNative -FilePath "git" -ArgumentList @("rev-parse", "--is-inside-work-tree") -WorkingDirectory $WorkingDirectory
    if ($inside.ExitCode -ne 0 -or (@($inside.Output) -join "`n").Trim() -ne "true") {
        return [pscustomobject]@{
            IsRepository = $false
            Root = $null
            Branch = $null
            Head = $null
            StatusShort = @()
            DiffStat = @()
        }
    }

    $root = Invoke-HookNative -FilePath "git" -ArgumentList @("rev-parse", "--show-toplevel") -WorkingDirectory $WorkingDirectory
    $branch = Invoke-HookNative -FilePath "git" -ArgumentList @("branch", "--show-current") -WorkingDirectory $WorkingDirectory
    $head = Invoke-HookNative -FilePath "git" -ArgumentList @("rev-parse", "--short", "HEAD") -WorkingDirectory $WorkingDirectory
    $status = Invoke-HookNative -FilePath "git" -ArgumentList @("status", "--short") -WorkingDirectory $WorkingDirectory
    $diffStat = Invoke-HookNative -FilePath "git" -ArgumentList @("diff", "--stat") -WorkingDirectory $WorkingDirectory

    return [pscustomobject]@{
        IsRepository = $true
        Root = (@($root.Output) -join "`n").Trim()
        Branch = (@($branch.Output) -join "`n").Trim()
        Head = (@($head.Output) -join "`n").Trim()
        StatusShort = @($status.Output)
        DiffStat = @($diffStat.Output)
    }
}

function Get-HookDirectoryInventory {
    param(
        [Parameter(Mandatory = $true)]
        [string]$WorkingDirectory,

        [int]$Limit = 300
    )

    $files = @(Get-ChildItem -LiteralPath $WorkingDirectory -Recurse -File -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch '\\.hook(\\|$)' } |
        Sort-Object FullName)

    $workingRoot = $WorkingDirectory.TrimEnd('\', '/')
    $totalBytes = 0
    foreach ($file in $files) {
        $totalBytes += $file.Length
    }

    $shown = @($files | Select-Object -First $Limit | ForEach-Object {
        $path = $_.FullName
        if ($path.StartsWith($workingRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
            $path = $path.Substring($workingRoot.Length).TrimStart('\', '/')
        }

        [pscustomobject]@{
            Path = $path
            Length = $_.Length
            LastWriteTimeUtc = $_.LastWriteTimeUtc.ToString("o")
        }
    })

    return [pscustomobject]@{
        FileCount = $files.Count
        TotalBytes = $totalBytes
        Limit = $Limit
        Files = $shown
    }
}

function Write-HookSetupFailure {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RunDirectory,

        [Parameter(Mandatory = $true)]
        [string]$Command,

        [Parameter(Mandatory = $true)]
        [string]$ErrorMessage
    )

    New-Item -ItemType Directory -Force -Path $RunDirectory | Out-Null

    $failurePath = Join-Path $RunDirectory "failure.md"
    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add("# Setup Failure")
    $lines.Add("")
    $lines.Add("- Failed at UTC: $((Get-Date).ToUniversalTime().ToString("o"))")
    $lines.Add("- Command: ``$Command``")
    $lines.Add("- Error: $ErrorMessage")
    $lines.Add("")
    $lines.Add("The task command did not run because hook setup failed before the pre-change snapshot was written.")

    $lines | Set-Content -LiteralPath $failurePath -Encoding UTF8
    return $failurePath
}

function New-HookSnapshot {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [string]$WorkingDirectory
    )

    $resolvedWorkingDirectory = (Resolve-Path -LiteralPath $WorkingDirectory).Path
    $git = Get-HookGitInfo -WorkingDirectory $resolvedWorkingDirectory
    $inventory = Get-HookDirectoryInventory -WorkingDirectory $resolvedWorkingDirectory

    return [pscustomobject]@{
        Name = $Name
        CreatedAt = (Get-Date).ToUniversalTime().ToString("o")
        WorkingDirectory = $resolvedWorkingDirectory
        Machine = $env:COMPUTERNAME
        User = $env:USERNAME
        Git = $git
        Inventory = $inventory
    }
}

function Write-HookSnapshotFiles {
    param(
        [Parameter(Mandatory = $true)]
        [pscustomobject]$Snapshot,

        [Parameter(Mandatory = $true)]
        [string]$RunDirectory
    )

    New-Item -ItemType Directory -Force -Path $RunDirectory | Out-Null

    $jsonPath = Join-Path $RunDirectory "pre-snapshot.json"
    $mdPath = Join-Path $RunDirectory "pre-snapshot.md"

    $Snapshot | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $jsonPath -Encoding UTF8

    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add("# Pre-change Snapshot")
    $lines.Add("")
    $lines.Add("- Name: $($Snapshot.Name)")
    $lines.Add("- Created at UTC: $($Snapshot.CreatedAt)")
    $lines.Add("- Working directory: $($Snapshot.WorkingDirectory)")
    $lines.Add("- Machine: $($Snapshot.Machine)")
    $lines.Add("- User: $($Snapshot.User)")
    $lines.Add("")

    if ($Snapshot.Git.IsRepository) {
        $lines.Add("## Git")
        $lines.Add("")
        $lines.Add("- Root: $($Snapshot.Git.Root)")
        $lines.Add("- Branch: $($Snapshot.Git.Branch)")
        $lines.Add("- Head: $($Snapshot.Git.Head)")
        $lines.Add("")
        $lines.Add("### Status")
        $lines.Add("")
        if (@($Snapshot.Git.StatusShort).Count -gt 0) {
            $lines.Add("``````text")
            @($Snapshot.Git.StatusShort) | ForEach-Object { $lines.Add($_) }
            $lines.Add("``````")
        }
        else {
            $lines.Add("Clean working tree.")
        }
        $lines.Add("")
        $lines.Add("### Diff Stat")
        $lines.Add("")
        if (@($Snapshot.Git.DiffStat).Count -gt 0) {
            $lines.Add("``````text")
            @($Snapshot.Git.DiffStat) | ForEach-Object { $lines.Add($_) }
            $lines.Add("``````")
        }
        else {
            $lines.Add("No unstaged diff.")
        }
        $lines.Add("")
    }

    $lines.Add("## Directory Inventory")
    $lines.Add("")
    $lines.Add("- File count: $($Snapshot.Inventory.FileCount)")
    $lines.Add("- Total bytes: $($Snapshot.Inventory.TotalBytes)")
    $lines.Add("- Listed files: $(@($Snapshot.Inventory.Files).Count) of $($Snapshot.Inventory.FileCount)")
    $lines.Add("")

    if (@($Snapshot.Inventory.Files).Count -gt 0) {
        $lines.Add("``````text")
        @($Snapshot.Inventory.Files) | ForEach-Object {
            $lines.Add("$($_.Path) ($($_.Length) bytes)")
        }
        $lines.Add("``````")
    }

    $lines | Set-Content -LiteralPath $mdPath -Encoding UTF8
}

function Get-HookCurrentState {
    param(
        [Parameter(Mandatory = $true)]
        [string]$WorkingDirectory
    )

    $resolvedWorkingDirectory = (Resolve-Path -LiteralPath $WorkingDirectory).Path
    return [pscustomobject]@{
        CapturedAt = (Get-Date).ToUniversalTime().ToString("o")
        WorkingDirectory = $resolvedWorkingDirectory
        Git = Get-HookGitInfo -WorkingDirectory $resolvedWorkingDirectory
        Inventory = Get-HookDirectoryInventory -WorkingDirectory $resolvedWorkingDirectory
    }
}

function Compare-HookInventory {
    param(
        [Parameter(Mandatory = $true)]
        [pscustomobject]$Before,

        [Parameter(Mandatory = $true)]
        [pscustomobject]$After
    )

    $beforeMap = @{}
    foreach ($file in @($Before.Files)) {
        $beforeMap[$file.Path] = $file
    }

    $afterMap = @{}
    foreach ($file in @($After.Files)) {
        $afterMap[$file.Path] = $file
    }

    $added = @($afterMap.Keys | Where-Object { -not $beforeMap.ContainsKey($_) } | Sort-Object)
    $removed = @($beforeMap.Keys | Where-Object { -not $afterMap.ContainsKey($_) } | Sort-Object)
    $changed = @($afterMap.Keys | Where-Object {
        $beforeMap.ContainsKey($_) -and (
            $beforeMap[$_].Length -ne $afterMap[$_].Length -or
            $beforeMap[$_].LastWriteTimeUtc -ne $afterMap[$_].LastWriteTimeUtc
        )
    } | Sort-Object)

    return [pscustomobject]@{
        Added = $added
        Removed = $removed
        Changed = $changed
    }
}

function Read-HookSnapshot {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RunDirectory
    )

    $snapshotPath = Join-Path $RunDirectory "pre-snapshot.json"
    if (-not (Test-Path -LiteralPath $snapshotPath)) {
        throw "Missing snapshot: $snapshotPath"
    }

    return Get-Content -LiteralPath $snapshotPath -Raw -Encoding UTF8 | ConvertFrom-Json
}

function Get-HookTail {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [int]$Lines = 80
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return @()
    }

    $raw = Get-Content -LiteralPath $Path -Raw -ErrorAction SilentlyContinue
    if (-not [string]::IsNullOrWhiteSpace($raw) -and $raw.TrimStart().StartsWith("#< CLIXML")) {
        $decoded = Convert-HookCliXmlLines -Raw $raw
        return @($decoded | Select-Object -Last $Lines)
    }

    return @(Get-Content -LiteralPath $Path -Tail $Lines -ErrorAction SilentlyContinue)
}

function Convert-HookCliXmlLines {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Raw
    )

    try {
        $xmlText = ($Raw -replace '^\s*#< CLIXML\s*', '').Trim()
        [xml]$xml = $xmlText
        $stringNodes = @($xml.SelectNodes("//*[local-name()='S']"))
        $lines = New-Object System.Collections.Generic.List[string]

        foreach ($node in $stringNodes) {
            $stream = $node.Attributes["S"]
            if ($null -ne $stream -and $stream.Value -notin @("Error", "Warning", "Verbose", "Debug", "Information")) {
                continue
            }

            $text = [regex]::Replace($node.InnerText, '_x([0-9A-Fa-f]{4})_', {
                param($match)
                return [string]([char][Convert]::ToInt32($match.Groups[1].Value, 16))
            })

            foreach ($line in ($text -split "`r?`n")) {
                if (-not [string]::IsNullOrWhiteSpace($line)) {
                    $lines.Add($line.TrimEnd())
                }
            }
        }

        return @($lines)
    }
    catch {
        return @($Raw -split "`r?`n")
    }
}

function Write-HookSummary {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RunDirectory,

        [int]$ExitCode = 0,

        [string]$Command = "",

        [object]$StartedAt = $null,

        [object]$EndedAt = $null
    )

    $snapshot = Read-HookSnapshot -RunDirectory $RunDirectory
    $state = Get-HookCurrentState -WorkingDirectory $snapshot.WorkingDirectory
    $comparison = Compare-HookInventory -Before $snapshot.Inventory -After $state.Inventory

    $summaryPath = Join-Path $RunDirectory "summary.md"
    $hasStartedAt = $null -ne $StartedAt -and $StartedAt -is [datetime]
    $hasEndedAt = $null -ne $EndedAt -and $EndedAt -is [datetime]
    $ended = if ($hasEndedAt) { [datetime]$EndedAt } else { Get-Date }
    $startedText = if ($hasStartedAt) { ([datetime]$StartedAt).ToUniversalTime().ToString("o") } else { $snapshot.CreatedAt }
    $durationText = "n/a"
    if ($hasStartedAt) {
        $durationText = [string]([Math]::Round(($ended - ([datetime]$StartedAt)).TotalSeconds, 2)) + "s"
    }

    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add("# Hook Summary")
    $lines.Add("")
    $lines.Add("- Name: $($snapshot.Name)")
    $lines.Add("- Started at UTC: $startedText")
    $lines.Add("- Ended at UTC: $($ended.ToUniversalTime().ToString("o"))")
    $lines.Add("- Duration: $durationText")
    $lines.Add("- Exit code: $ExitCode")
    $lines.Add("- Working directory: $($snapshot.WorkingDirectory)")
    if (-not [string]::IsNullOrWhiteSpace($Command)) {
        $lines.Add("- Command: ``$Command``")
    }
    $lines.Add("")

    if ($state.Git.IsRepository) {
        $lines.Add("## Git After Task")
        $lines.Add("")
        $lines.Add("- Branch: $($state.Git.Branch)")
        $lines.Add("- Head: $($state.Git.Head)")
        $lines.Add("")
        $lines.Add("### Status")
        $lines.Add("")
        if (@($state.Git.StatusShort).Count -gt 0) {
            $lines.Add("``````text")
            @($state.Git.StatusShort) | ForEach-Object { $lines.Add($_) }
            $lines.Add("``````")
        }
        else {
            $lines.Add("Clean working tree.")
        }
        $lines.Add("")
        $lines.Add("### Diff Stat")
        $lines.Add("")
        if (@($state.Git.DiffStat).Count -gt 0) {
            $lines.Add("``````text")
            @($state.Git.DiffStat) | ForEach-Object { $lines.Add($_) }
            $lines.Add("``````")
        }
        else {
            $lines.Add("No unstaged diff.")
        }
        $lines.Add("")
    }

    $lines.Add("## File Inventory Changes")
    $lines.Add("")
    $lines.Add("- Added: $(@($comparison.Added).Count)")
    $lines.Add("- Changed: $(@($comparison.Changed).Count)")
    $lines.Add("- Removed: $(@($comparison.Removed).Count)")
    $lines.Add("- File count before: $($snapshot.Inventory.FileCount)")
    $lines.Add("- File count after: $($state.Inventory.FileCount)")
    $lines.Add("")

    foreach ($section in @(
        @{ Title = "Added"; Items = @($comparison.Added) },
        @{ Title = "Changed"; Items = @($comparison.Changed) },
        @{ Title = "Removed"; Items = @($comparison.Removed) }
    )) {
        if (@($section.Items).Count -gt 0) {
            $lines.Add("### $($section.Title)")
            $lines.Add("")
            $lines.Add("``````text")
            @($section.Items) | Select-Object -First 120 | ForEach-Object { $lines.Add($_) }
            if (@($section.Items).Count -gt 120) {
                $lines.Add("... truncated ...")
            }
            $lines.Add("``````")
            $lines.Add("")
        }
    }

    $lines.Add("## Artifacts")
    $lines.Add("")
    foreach ($name in @("pre-snapshot.md", "pre-snapshot.json", "stdout.log", "stderr.log", "failure.md")) {
        $path = Join-Path $RunDirectory $name
        if (Test-Path -LiteralPath $path) {
            $lines.Add("- $name")
        }
    }

    $lines | Set-Content -LiteralPath $summaryPath -Encoding UTF8
    return $summaryPath
}

function Write-HookFailure {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RunDirectory,

        [Parameter(Mandatory = $true)]
        [int]$ExitCode,

        [Parameter(Mandatory = $true)]
        [string]$Command,

        [string]$ErrorMessage = ""
    )

    $snapshot = Read-HookSnapshot -RunDirectory $RunDirectory
    $state = Get-HookCurrentState -WorkingDirectory $snapshot.WorkingDirectory
    $stdoutPath = Join-Path $RunDirectory "stdout.log"
    $stderrPath = Join-Path $RunDirectory "stderr.log"
    $failurePath = Join-Path $RunDirectory "failure.md"

    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add("# Failure Log")
    $lines.Add("")
    $lines.Add("- Name: $($snapshot.Name)")
    $lines.Add("- Failed at UTC: $((Get-Date).ToUniversalTime().ToString("o"))")
    $lines.Add("- Exit code: $ExitCode")
    $lines.Add("- Working directory: $($snapshot.WorkingDirectory)")
    $lines.Add("- Command: ``$Command``")
    if (-not [string]::IsNullOrWhiteSpace($ErrorMessage)) {
        $lines.Add("- Error: $ErrorMessage")
    }
    $lines.Add("")

    $lines.Add("## Environment")
    $lines.Add("")
    $lines.Add("- PowerShell: $($PSVersionTable.PSVersion)")
    $lines.Add("- OS: $([System.Environment]::OSVersion.VersionString)")
    $lines.Add("- User: $env:USERNAME")
    $lines.Add("- Machine: $env:COMPUTERNAME")
    $lines.Add("")

    if ($state.Git.IsRepository) {
        $lines.Add("## Git State")
        $lines.Add("")
        $lines.Add("- Branch: $($state.Git.Branch)")
        $lines.Add("- Head: $($state.Git.Head)")
        $lines.Add("")
        if (@($state.Git.StatusShort).Count -gt 0) {
            $lines.Add("``````text")
            @($state.Git.StatusShort) | ForEach-Object { $lines.Add($_) }
            $lines.Add("``````")
        }
        else {
            $lines.Add("Clean working tree.")
        }
        $lines.Add("")
    }

    $lines.Add("## stderr Tail")
    $lines.Add("")
    $stderrTail = Get-HookTail -Path $stderrPath
    if (@($stderrTail).Count -gt 0) {
        $lines.Add("``````text")
        $stderrTail | ForEach-Object { $lines.Add($_) }
        $lines.Add("``````")
    }
    else {
        $lines.Add("No stderr captured.")
    }
    $lines.Add("")

    $lines.Add("## stdout Tail")
    $lines.Add("")
    $stdoutTail = Get-HookTail -Path $stdoutPath
    if (@($stdoutTail).Count -gt 0) {
        $lines.Add("``````text")
        $stdoutTail | ForEach-Object { $lines.Add($_) }
        $lines.Add("``````")
    }
    else {
        $lines.Add("No stdout captured.")
    }

    $lines | Set-Content -LiteralPath $failurePath -Encoding UTF8
    return $failurePath
}

function Write-HookCurrentRun {
    param(
        [Parameter(Mandatory = $true)]
        [string]$HookRoot,

        [Parameter(Mandatory = $true)]
        [string]$RunDirectory
    )

    $currentPath = Join-Path $HookRoot "current-run.json"
    [pscustomobject]@{
        RunDirectory = $RunDirectory
        UpdatedAt = (Get-Date).ToUniversalTime().ToString("o")
    } | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $currentPath -Encoding UTF8
}

function Get-HookCurrentRunDirectory {
    param(
        [Parameter(Mandatory = $true)]
        [string]$HookRoot
    )

    $currentPath = Join-Path $HookRoot "current-run.json"
    if (-not (Test-Path -LiteralPath $currentPath)) {
        throw "No current run file found: $currentPath"
    }

    $current = Get-Content -LiteralPath $currentPath -Raw -Encoding UTF8 | ConvertFrom-Json
    return $current.RunDirectory
}
