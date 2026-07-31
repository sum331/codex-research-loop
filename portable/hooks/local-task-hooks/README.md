# Local Hook Toolkit

This folder contains a small PowerShell hook toolkit for local tasks.

It provides three workflow features:

- Pre-change snapshots before a task starts.
- Completion summaries after a task finishes.
- Failure log collection when a wrapped command exits non-zero.

It is also registered with Codex lifecycle hooks:

- `SessionStart`: captures a pre-change snapshot for the thread workspace.
- `PostToolUse`: records failure payloads after tool calls.
- `Stop`: writes a lifecycle summary before Codex ends the turn.

## Quick Start

Global install path:

```text
$env:USERPROFILE\.codex\hooks\local-task-hooks\
```

Codex lifecycle registration:

```text
$env:USERPROFILE\.codex\hooks.json
```

Run any command through the wrapper:

```powershell
.\hooks\Invoke-HookTask.ps1 -Name "pytest-smoke" -Command "pytest -q"
```

From any Codex thread, use the global wrapper:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\local-task-hooks\Invoke-HookTask.ps1" -Name "pytest-smoke" -WorkingDirectory "C:\path\to\project" -Command "pytest -q"
```

Run a command in a specific directory:

```powershell
.\hooks\Invoke-HookTask.ps1 -Name "build" -Command "npm run build" -WorkingDirectory "E:\work\my-project"
```

Use `cmd.exe` instead of PowerShell:

```powershell
.\hooks\Invoke-HookTask.ps1 -Name "legacy-build" -Shell cmd -Command "build.bat"
```

Each run writes artifacts under:

```text
.hook\runs\<timestamp>-<task-name>\
```

The most useful files are:

- `pre-snapshot.md` and `pre-snapshot.json`
- `summary.md`
- `stdout.log`
- `stderr.log`
- `failure.md` when the command fails

## Manual Hook Flow

If another tool already runs the command, use the manual start/finish scripts:

```powershell
$run = .\hooks\Start-HookTask.ps1 -Name "manual-edit"

# Run your real work here.

.\hooks\Complete-HookTask.ps1 -RunDirectory $run
```

When `-RunDirectory` is omitted, `Complete-HookTask.ps1` uses `.hook\current-run.json`.

## Notes

- Git metadata is captured when the target directory is inside a Git repository.
- Outside Git, the snapshot falls back to directory inventory and timestamps.
- Runtime artifacts are ignored by `.gitignore`.
