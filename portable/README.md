# Codex Portable Skills And Plugins

This folder packages the local Codex capability library that should travel with
`codex-research-loop`.

Included:

- `skills/` - user/system skill folders copied from the source machine.
- `plugins/prompt-submit-skill-router/` - the UserPromptSubmit routing plugin.
- `dispatch/codex_capability_dispatch_inventory_20260702.md` - the routing table.
- `hooks/local-task-hooks/` - reusable lifecycle hook scripts.
- `scripts/install-codex-portable.ps1` - Windows installer for a fresh Codex home.
- `manifests/` - package inventory and excluded managed-plugin cache summary.

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

Run without hook registration when you only want to copy the library:

```powershell
powershell -ExecutionPolicy Bypass -File .\portable\scripts\install-codex-portable.ps1 -InstallHooks:$false
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
