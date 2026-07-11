# Codex Portable Skills And Plugins

This folder packages the local Codex capability library that should travel with
`codex-research-loop`.

Included:

- `skills/` - user/system skill folders copied from the source machine.
- `plugins/prompt-submit-skill-router/` - the UserPromptSubmit routing plugin.
- `dispatch/codex_capability_dispatch_inventory_20260702.md` - the routing table.
- `hooks/local-task-hooks/` - reusable lifecycle hook scripts.
- `scripts/install-codex-portable.ps1` - Windows installer for a fresh Codex home.
- `manifests/` - package inventory, plugin install channels, and excluded
  managed-plugin cache summary.

Not included:

- API keys, tokens, `.env` files, local databases, logs, `__pycache__`, Git
  metadata, runtime orphan workspaces, and appserver/plugin-marketplace caches.
- Managed plugin caches under `~/.codex/plugins/cache`. Reinstall official
  plugins/connectors through Codex on the new computer; this package records the
  local cache inventory but does not redistribute those managed artifacts.

## Fresh Windows Install

```powershell
git clone https://github.com/sum331/codex-research-loop.git
cd codex-research-loop
powershell -ExecutionPolicy Bypass -File .\portable\scripts\install-codex-portable.ps1
```

The installer copies this package into `%CODEX_HOME%` when set, otherwise into
`%USERPROFILE%\.codex`. It also rewrites `hooks.json` using the new computer's
paths, backs up any existing `hooks.json`, and registers:

- prompt-submit skill/plugin routing;
- local lifecycle task hooks;
- research-loop lifecycle hooks pointing to this cloned repo.

The installer also writes the user-level `CODEX_RESEARCH_LOOP_HOME` environment
variable to the cloned repository path. Restart Codex after the first install if
the current session does not immediately see the variable. Use
`-SkipResearchLoopHomeEnv` only when you want to manage that path yourself.

By default it also reads `manifests/plugin-install-channels.json` and configures
plugin channels:

- local marketplace entries in `%USERPROFILE%\.agents\plugins\marketplace.json`
  for `codex-research-loop@personal` and
  `prompt-submit-skill-router@personal`;
- managed plugin install attempts through `codex plugin add`, including
  `github@openai-curated-remote`, `google-drive@openai-curated-remote`,
  `gmail@openai-curated-remote`, `figma@openai-curated-remote`,
  `linear@openai-curated-remote`, `hugging-face@openai-curated-remote`,
  `openai-developers@openai-curated-remote`,
  `codex-security@openai-curated-remote`,
  `creative-production@openai-curated-remote`, and
  `superpowers@openai-curated-remote`;
- runtime plugin enablement in `%CODEX_HOME%\config.toml`, including
  `documents@openai-primary-runtime`, `pdf@openai-primary-runtime`,
  `spreadsheets@openai-primary-runtime`, `presentations@openai-primary-runtime`,
  `template-creator@openai-primary-runtime`, `browser@openai-bundled`,
  `chrome@openai-bundled`, `computer-use@openai-bundled`, and
  `latex@openai-bundled`.

Plugin install is fail-open: if `codex` CLI is unavailable or a managed channel
is not visible on that machine yet, the installer records the failure in its JSON
result but still completes the local skills/hooks setup.

Run without hook registration when you only want to copy the library:

```powershell
powershell -ExecutionPolicy Bypass -File .\portable\scripts\install-codex-portable.ps1 -SkipHooks
```

Run without managed plugin auto-install when you want only marketplace/config
setup:

```powershell
powershell -ExecutionPolicy Bypass -File .\portable\scripts\install-codex-portable.ps1 -SkipAutoInstallPlugins
```

Run without any plugin-channel configuration:

```powershell
powershell -ExecutionPolicy Bypass -File .\portable\scripts\install-codex-portable.ps1 -SkipPluginChannels
```

## External API Pairing

The DeepSeek supervisor layer is optional. Pair it locally on the new computer
only if you want that extra review layer:

```powershell
[Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", "<your DeepSeek API key>", "User")
```

Do not commit API keys to this repository. If the key is absent or invalid, the
research loop falls back to the built-in local watchdog/deep-loop path.

## Audit

Before pushing or after changing the portable package:

```powershell
python .\portable\scripts\audit-portable-bundle.py
python -m unittest tests.test_deep_loop_subagents.DeepLoopSubagentTests.test_portable_bundle_contains_skills_dispatch_plugin_and_installer
```
