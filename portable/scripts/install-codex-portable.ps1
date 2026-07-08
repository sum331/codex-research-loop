[CmdletBinding()]
param(
    [string]$CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }),
    [bool]$InstallHooks = $true,
    [bool]$InstallLocalTaskHooks = $true,
    [bool]$InstallResearchLoopHooks = $true,
    [bool]$BackupHooks = $true,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Resolve-OrCreateDirectory {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        if (-not $DryRun) {
            New-Item -ItemType Directory -Force -Path $Path | Out-Null
        }
    }
    return [System.IO.Path]::GetFullPath($Path)
}

function Copy-PortableDirectory {
    param(
        [string]$Source,
        [string]$Destination
    )
    if (-not (Test-Path -LiteralPath $Source)) {
        throw "Missing portable source: $Source"
    }
    if ($DryRun) {
        Write-Host "[dry-run] copy $Source -> $Destination"
        return
    }
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    Get-ChildItem -LiteralPath $Source -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $Destination -Recurse -Force
    }
}

function New-WrapperScript {
    param(
        [string]$Path,
        [string]$Content
    )
    if ($DryRun) {
        Write-Host "[dry-run] write wrapper $Path"
        return
    }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Path) | Out-Null
    Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
}

function New-CommandHookEntry {
    param(
        [string]$Command,
        [int]$Timeout,
        [string]$StatusMessage
    )
    return [pscustomobject]@{
        hooks = @(
            [pscustomobject]@{
                type = "command"
                command = $Command
                timeout = $Timeout
                statusMessage = $StatusMessage
            }
        )
    }
}

function Get-HookCommandText {
    param($Entry)
    if (-not $Entry -or -not $Entry.PSObject.Properties["hooks"]) {
        return ""
    }
    return (@($Entry.hooks) | ForEach-Object { $_.command }) -join "`n"
}

function Set-HookEvent {
    param(
        $HooksRoot,
        [string]$EventName,
        [object[]]$NewEntries,
        [string[]]$ReplaceMarkers
    )
    if (-not $HooksRoot.PSObject.Properties[$EventName]) {
        $HooksRoot | Add-Member -MemberType NoteProperty -Name $EventName -Value @()
    }

    $kept = @()
    foreach ($entry in @($HooksRoot.$EventName)) {
        $commandText = Get-HookCommandText $entry
        $replace = $false
        foreach ($marker in $ReplaceMarkers) {
            if ($commandText -like "*$marker*") {
                $replace = $true
                break
            }
        }
        if (-not $replace) {
            $kept += $entry
        }
    }
    $HooksRoot.$EventName = @($kept + $NewEntries)
}

function Load-HooksJson {
    param([string]$Path)
    if (Test-Path -LiteralPath $Path) {
        $loaded = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    } else {
        $loaded = [pscustomobject]@{}
    }
    if (-not $loaded.PSObject.Properties["hooks"]) {
        $loaded | Add-Member -MemberType NoteProperty -Name "hooks" -Value ([pscustomobject]@{})
    }
    return $loaded
}

function Save-HooksJson {
    param(
        $Hooks,
        [string]$Path
    )
    if ($DryRun) {
        Write-Host "[dry-run] write hooks $Path"
        return
    }
    $Hooks | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $Path -Encoding UTF8
}

$portableRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $portableRoot ".."))
$codexHomePath = Resolve-OrCreateDirectory $CodexHome

$skillsSource = Join-Path $portableRoot "skills"
$pluginsSource = Join-Path $portableRoot "plugins"
$dispatchSource = Join-Path $portableRoot "dispatch"
$hooksSource = Join-Path $portableRoot "hooks"

$skillsDest = Resolve-OrCreateDirectory (Join-Path $codexHomePath "skills")
$pluginsDest = Resolve-OrCreateDirectory (Join-Path $codexHomePath "plugins")
$docsDest = Resolve-OrCreateDirectory (Join-Path $codexHomePath "docs")
$hooksDest = Resolve-OrCreateDirectory (Join-Path $codexHomePath "hooks")

Copy-PortableDirectory $skillsSource $skillsDest
Copy-PortableDirectory $pluginsSource $pluginsDest
Copy-PortableDirectory $dispatchSource $docsDest
Copy-PortableDirectory $hooksSource $hooksDest

if ($InstallHooks) {
    $hooksPath = Join-Path $codexHomePath "hooks.json"
    if ((Test-Path -LiteralPath $hooksPath) -and $BackupHooks -and -not $DryRun) {
        $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        Copy-Item -LiteralPath $hooksPath -Destination "$hooksPath.bak-$timestamp" -Force
    }

    $wrapperDir = Resolve-OrCreateDirectory (Join-Path $hooksDest "codex-portable")
    $dispatchPath = Join-Path $docsDest "codex_capability_dispatch_inventory_20260702.md"
    $routerPath = Join-Path $pluginsDest "prompt-submit-skill-router\scripts\user_prompt_submit_router.py"
    $localHookPath = Join-Path $hooksDest "local-task-hooks\codex_lifecycle_hook.py"
    $researchLoopHookPath = Join-Path $repoRoot "scripts\codex_research_lifecycle_hook.py"

    $routerWrapper = Join-Path $wrapperDir "run-prompt-router.ps1"
    $localHookWrapper = Join-Path $wrapperDir "run-local-task-hook.ps1"
    $researchLoopWrapper = Join-Path $wrapperDir "run-research-loop-hook.ps1"

    New-WrapperScript $routerWrapper @"
`$ErrorActionPreference = "Stop"
`$env:CODEX_CAPABILITY_REGISTRY = "$dispatchPath"
`$router = "$routerPath"
`$python = `$env:PYTHON
if (-not `$python) {
    `$cmd = Get-Command python -ErrorAction SilentlyContinue
    if (`$cmd) { `$python = `$cmd.Source }
}
if (`$python) {
    & `$python `$router
    exit `$LASTEXITCODE
}
`$py = Get-Command py -ErrorAction SilentlyContinue
if (`$py) {
    & `$py.Source -3 `$router
    exit `$LASTEXITCODE
}
throw "Python is required to run the prompt-submit skill router."
"@

    New-WrapperScript $localHookWrapper @"
param([string]`$EventName)
`$ErrorActionPreference = "Stop"
`$hook = "$localHookPath"
`$python = `$env:PYTHON
if (-not `$python) {
    `$cmd = Get-Command python -ErrorAction SilentlyContinue
    if (`$cmd) { `$python = `$cmd.Source }
}
if (`$python) {
    & `$python `$hook `$EventName
    exit `$LASTEXITCODE
}
`$py = Get-Command py -ErrorAction SilentlyContinue
if (`$py) {
    & `$py.Source -3 `$hook `$EventName
    exit `$LASTEXITCODE
}
throw "Python is required to run local task hooks."
"@

    New-WrapperScript $researchLoopWrapper @"
param([string]`$EventName)
`$ErrorActionPreference = "Stop"
`$hook = "$researchLoopHookPath"
if (-not (Test-Path -LiteralPath `$hook)) {
    exit 0
}
`$python = `$env:PYTHON
if (-not `$python) {
    `$cmd = Get-Command python -ErrorAction SilentlyContinue
    if (`$cmd) { `$python = `$cmd.Source }
}
if (`$python) {
    & `$python `$hook `$EventName
    exit `$LASTEXITCODE
}
`$py = Get-Command py -ErrorAction SilentlyContinue
if (`$py) {
    & `$py.Source -3 `$hook `$EventName
    exit `$LASTEXITCODE
}
exit 0
"@

    $hooksJson = Load-HooksJson $hooksPath
    $routerCommand = "powershell -NoProfile -ExecutionPolicy Bypass -File `"$routerWrapper`""
    Set-HookEvent $hooksJson.hooks "UserPromptSubmit" @(
        New-CommandHookEntry $routerCommand 10 "Routing prompt to skills/plugins"
    ) @("prompt-submit-skill-router", "run-prompt-router.ps1")

    foreach ($eventName in @("SessionStart", "PostToolUse", "Stop")) {
        $entries = @()
        if ($InstallLocalTaskHooks) {
            $localCommand = "powershell -NoProfile -ExecutionPolicy Bypass -File `"$localHookWrapper`" $eventName"
            $entries += New-CommandHookEntry $localCommand 10 "Running local task hook"
        }
        if ($InstallResearchLoopHooks) {
            $researchCommand = "powershell -NoProfile -ExecutionPolicy Bypass -File `"$researchLoopWrapper`" $eventName"
            $entries += New-CommandHookEntry $researchCommand 10 "Recording research loop lifecycle event"
        }
        if ($entries.Count -gt 0) {
            Set-HookEvent $hooksJson.hooks $eventName $entries @("local-task-hooks", "codex-research-loop", "run-local-task-hook.ps1", "run-research-loop-hook.ps1")
        }
    }

    Save-HooksJson $hooksJson $hooksPath
}

$result = [ordered]@{
    codex_home = $codexHomePath
    skills_destination = $skillsDest
    plugins_destination = $pluginsDest
    dispatch_destination = $docsDest
    hooks_installed = $InstallHooks
    dry_run = [bool]$DryRun
}

$result | ConvertTo-Json -Depth 5
