[CmdletBinding()]
param(
    [string]$CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }),
    [bool]$InstallHooks = $true,
    [bool]$InstallLocalTaskHooks = $true,
    [bool]$InstallResearchLoopHooks = $true,
    [bool]$InstallPluginChannels = $true,
    [bool]$AutoInstallPlugins = $true,
    [bool]$EnableRuntimePlugins = $true,
    [bool]$BackupHooks = $true,
    [bool]$BackupConfig = $true,
    [string]$AgentsPluginHome = $(Join-Path $HOME ".agents\plugins"),
    [string]$CodexCliPath = $(if ($env:CODEX_CLI_PATH) { $env:CODEX_CLI_PATH } else { "" }),
    [switch]$SkipHooks,
    [switch]$SkipPluginChannels,
    [switch]$SkipAutoInstallPlugins,
    [switch]$SkipRuntimePlugins,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

if ($SkipHooks) { $InstallHooks = $false }
if ($SkipPluginChannels) { $InstallPluginChannels = $false }
if ($SkipAutoInstallPlugins) { $AutoInstallPlugins = $false }
if ($SkipRuntimePlugins) { $EnableRuntimePlugins = $false }

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
    $robocopy = Get-Command robocopy -ErrorAction SilentlyContinue
    if ($robocopy) {
        & $robocopy.Source $Source $Destination /E /COPY:DAT /DCOPY:DAT /R:2 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
        $exitCode = $LASTEXITCODE
        if ($exitCode -gt 7) {
            throw "robocopy failed with exit code $exitCode while copying $Source -> $Destination"
        }
        return
    }
    Get-ChildItem -LiteralPath $Source -Recurse -Force | ForEach-Object {
        $relative = $_.FullName.Substring($Source.Length).TrimStart("\", "/")
        $target = Join-Path $Destination $relative
        if ($_.PSIsContainer) {
            New-Item -ItemType Directory -Force -Path $target | Out-Null
        } else {
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
            Copy-Item -LiteralPath $_.FullName -Destination $target -Force
        }
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

function Read-JsonFile {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Missing JSON file: $Path"
    }
    return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

function Expand-PortableTemplate {
    param(
        [string]$Value,
        [string]$RepoRoot,
        [string]$CodexHome
    )
    return $Value.Replace("{REPO_ROOT}", $RepoRoot).Replace("{CODEX_HOME}", $CodexHome)
}

function Get-CodexCli {
    param([string]$PreferredPath)
    if ($PreferredPath -and (Test-Path -LiteralPath $PreferredPath)) {
        return [System.IO.Path]::GetFullPath($PreferredPath)
    }
    $cmd = Get-Command codex -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($cmd) {
        return $cmd.Source
    }
    return ""
}

function Invoke-CodexPluginAdd {
    param(
        [string]$CodexCli,
        [string]$InstallSpec
    )
    if (-not $CodexCli) {
        return [pscustomobject]@{
            spec = $InstallSpec
            status = "skipped"
            reason = "codex-cli-not-found"
            output = ""
        }
    }
    if ($DryRun) {
        return [pscustomobject]@{
            spec = $InstallSpec
            status = "dry-run"
            reason = ""
            output = ""
        }
    }
    try {
        $output = & $CodexCli plugin add $InstallSpec 2>&1 | Out-String
        $exitCode = $LASTEXITCODE
        return [pscustomobject]@{
            spec = $InstallSpec
            status = $(if ($exitCode -eq 0) { "ok" } else { "failed" })
            exit_code = $exitCode
            reason = ""
            output = $output.Trim()
        }
    } catch {
        return [pscustomobject]@{
            spec = $InstallSpec
            status = "failed"
            exit_code = $null
            reason = $_.Exception.Message
            output = ""
        }
    }
}

function Update-PersonalMarketplace {
    param(
        $Channels,
        [string]$MarketplaceHome,
        [string]$RepoRoot,
        [string]$CodexHome
    )
    $marketplacePath = Join-Path $MarketplaceHome "marketplace.json"
    $marketplaceName = if ($Channels.personal_marketplace.name) { $Channels.personal_marketplace.name } else { "personal" }
    $displayName = if ($Channels.personal_marketplace.display_name) { $Channels.personal_marketplace.display_name } else { "Personal" }

    if (Test-Path -LiteralPath $marketplacePath) {
        $marketplace = Get-Content -LiteralPath $marketplacePath -Raw | ConvertFrom-Json
    } else {
        $marketplace = [pscustomobject]@{
            name = $marketplaceName
            interface = [pscustomobject]@{ displayName = $displayName }
            plugins = @()
        }
    }
    if (-not $marketplace.PSObject.Properties["name"]) {
        $marketplace | Add-Member -MemberType NoteProperty -Name "name" -Value $marketplaceName
    }
    if (-not $marketplace.PSObject.Properties["interface"]) {
        $marketplace | Add-Member -MemberType NoteProperty -Name "interface" -Value ([pscustomobject]@{ displayName = $displayName })
    }
    if (-not $marketplace.PSObject.Properties["plugins"]) {
        $marketplace | Add-Member -MemberType NoteProperty -Name "plugins" -Value @()
    }

    $plugins = @($marketplace.plugins)
    $updatedNames = @()
    foreach ($plugin in @($Channels.local_plugins)) {
        $sourcePath = Expand-PortableTemplate $plugin.source.path_template $RepoRoot $CodexHome
        $entry = [pscustomobject]@{
            name = $plugin.name
            source = [pscustomobject]@{
                source = $plugin.source.source
                path = $sourcePath
            }
            policy = [pscustomobject]@{
                installation = $plugin.policy.installation
                authentication = $plugin.policy.authentication
            }
            category = $plugin.category
        }
        $plugins = @($plugins | Where-Object { $_.name -ne $plugin.name })
        $plugins += $entry
        $updatedNames += $plugin.name
    }
    $marketplace.plugins = $plugins

    if ($DryRun) {
        Write-Host "[dry-run] write marketplace $marketplacePath"
    } else {
        New-Item -ItemType Directory -Force -Path $MarketplaceHome | Out-Null
        $marketplace | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $marketplacePath -Encoding UTF8
    }

    return [pscustomobject]@{
        path = $marketplacePath
        name = $marketplace.name
        updated_plugins = $updatedNames
    }
}

function Enable-CodexConfigPlugin {
    param(
        [string]$ConfigPath,
        [string]$PluginId
    )
    $section = "[plugins.""$PluginId""]"
    if ($DryRun) {
        Write-Host "[dry-run] enable $PluginId in $ConfigPath"
        return
    }
    if (Test-Path -LiteralPath $ConfigPath) {
        $lines = New-Object System.Collections.Generic.List[string]
        foreach ($line in [System.IO.File]::ReadAllLines($ConfigPath)) {
            $lines.Add($line)
        }
    } else {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $ConfigPath) | Out-Null
        $lines = New-Object System.Collections.Generic.List[string]
    }

    $sectionIndex = -1
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i].Trim() -eq $section) {
            $sectionIndex = $i
            break
        }
    }

    if ($sectionIndex -lt 0) {
        if ($lines.Count -gt 0 -and $lines[$lines.Count - 1].Trim() -ne "") {
            $lines.Add("")
        }
        $lines.Add($section)
        $lines.Add("enabled = true")
    } else {
        $nextSection = $lines.Count
        for ($i = $sectionIndex + 1; $i -lt $lines.Count; $i++) {
            if ($lines[$i].Trim().StartsWith("[") -and $lines[$i].Trim().EndsWith("]")) {
                $nextSection = $i
                break
            }
        }
        $enabledIndex = -1
        for ($i = $sectionIndex + 1; $i -lt $nextSection; $i++) {
            if ($lines[$i].Trim().StartsWith("enabled")) {
                $enabledIndex = $i
                break
            }
        }
        if ($enabledIndex -ge 0) {
            $lines[$enabledIndex] = "enabled = true"
        } else {
            $lines.Insert($sectionIndex + 1, "enabled = true")
        }
    }
    [System.IO.File]::WriteAllLines($ConfigPath, $lines)
}

$portableRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $portableRoot ".."))
$codexHomePath = Resolve-OrCreateDirectory $CodexHome

$skillsSource = Join-Path $portableRoot "skills"
$pluginsSource = Join-Path $portableRoot "plugins"
$dispatchSource = Join-Path $portableRoot "dispatch"
$hooksSource = Join-Path $portableRoot "hooks"
$pluginChannelsPath = Join-Path $portableRoot "manifests\plugin-install-channels.json"

$skillsDest = Resolve-OrCreateDirectory (Join-Path $codexHomePath "skills")
$pluginsDest = Resolve-OrCreateDirectory (Join-Path $codexHomePath "plugins")
$docsDest = Resolve-OrCreateDirectory (Join-Path $codexHomePath "docs")
$hooksDest = Resolve-OrCreateDirectory (Join-Path $codexHomePath "hooks")

Copy-PortableDirectory $skillsSource $skillsDest
Copy-PortableDirectory $pluginsSource $pluginsDest
Copy-PortableDirectory $dispatchSource $docsDest
Copy-PortableDirectory $hooksSource $hooksDest

$pluginChannelReport = [ordered]@{
    enabled = $InstallPluginChannels
    marketplace = $null
    local_plugin_installs = @()
    managed_plugin_installs = @()
    runtime_plugins_enabled = @()
}

if ($InstallPluginChannels -and (Test-Path -LiteralPath $pluginChannelsPath)) {
    $channels = Read-JsonFile $pluginChannelsPath
    $configPath = Join-Path $codexHomePath "config.toml"
    if ((Test-Path -LiteralPath $configPath) -and $BackupConfig -and -not $DryRun) {
        $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        Copy-Item -LiteralPath $configPath -Destination "$configPath.bak-$timestamp" -Force
    }

    $marketplaceResult = Update-PersonalMarketplace $channels $AgentsPluginHome $repoRoot $codexHomePath
    $pluginChannelReport.marketplace = $marketplaceResult

    if ($EnableRuntimePlugins) {
        foreach ($plugin in @($channels.runtime_plugins)) {
            if ($plugin.enable_in_config) {
                Enable-CodexConfigPlugin $configPath $plugin.id
                $pluginChannelReport.runtime_plugins_enabled += $plugin.id
            }
        }
    }

    if ($AutoInstallPlugins) {
        $codexCli = Get-CodexCli $CodexCliPath
        foreach ($plugin in @($channels.local_plugins)) {
            if ($plugin.auto_install) {
                $spec = "$($plugin.name)@$($marketplaceResult.name)"
                $pluginChannelReport.local_plugin_installs += Invoke-CodexPluginAdd $codexCli $spec
            }
        }
        foreach ($plugin in @($channels.managed_plugins)) {
            if (-not $plugin.auto_install) {
                continue
            }
            $attempts = @()
            $installed = $false
            foreach ($spec in @($plugin.candidate_install_specs)) {
                $result = Invoke-CodexPluginAdd $codexCli $spec
                $attempts += $result
                if ($result.status -eq "ok") {
                    $installed = $true
                    break
                }
            }
            $pluginChannelReport.managed_plugin_installs += [pscustomobject]@{
                id = $plugin.id
                installed = $installed
                attempts = $attempts
            }
        }
    }
}

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
    plugin_channels = $pluginChannelReport
    dry_run = [bool]$DryRun
}

$result | ConvertTo-Json -Depth 5
