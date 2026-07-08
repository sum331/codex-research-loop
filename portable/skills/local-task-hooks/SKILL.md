---
name: local-task-hooks
description: Use local PowerShell task hooks to wrap commands or manual workflows with pre-change snapshots, completion summaries, stdout/stderr capture, and failure logs. Trigger when the user asks to use hook, hook task, local hook, capture a snapshot before work, summarize a completed command, collect failure logs, or make a task reproducible across Codex threads.
---

# Local Task Hooks

Use the bundled PowerShell scripts in `scripts/` to run local tasks with durable artifacts. Prefer these scripts when the user wants a command or workflow wrapped with:

- `pre-snapshot.md` / `pre-snapshot.json`
- `summary.md`
- `stdout.log` / `stderr.log`
- `failure.md` on non-zero exit

The global installation also registers `codex_lifecycle_hook.py` in `C:\Users\ROG\.codex\hooks.json` for:

- `SessionStart`: capture a pre-change snapshot for a Codex thread workspace.
- `PostToolUse`: collect failure payloads after tool calls.
- `Stop`: write a lifecycle summary before Codex ends the turn.

## Wrapped Command

Use `Invoke-HookTask.ps1` when Codex controls the command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\ROG\.codex\skills\local-task-hooks\scripts\Invoke-HookTask.ps1 -Name "task-name" -WorkingDirectory "C:\path\to\project" -Command "pytest -q"
```

Use `-Shell cmd` for legacy `.bat` or `cmd.exe` commands:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\ROG\.codex\skills\local-task-hooks\scripts\Invoke-HookTask.ps1 -Name "legacy-build" -Shell cmd -WorkingDirectory "C:\path\to\project" -Command "build.bat"
```

## Manual Flow

Use `Start-HookTask.ps1` and `Complete-HookTask.ps1` when another tool or human action performs the real work:

```powershell
$run = powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\ROG\.codex\skills\local-task-hooks\scripts\Start-HookTask.ps1 -Name "manual-task" -WorkingDirectory "C:\path\to\project"

# Real work happens here.

powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\ROG\.codex\skills\local-task-hooks\scripts\Complete-HookTask.ps1 -RunDirectory $run -WorkingDirectory "C:\path\to\project" -ExitCode 0 -Command "manual task"
```

If `-RunDirectory` is omitted, `Complete-HookTask.ps1` uses `.hook/current-run.json` under the working directory.

## Artifact Location

Each run writes artifacts under the target working directory:

```text
.hook\runs\<timestamp>-<task-name>\
```

Runtime hook artifacts are intentionally local to the target project. Do not commit `.hook/runs/` unless the user explicitly asks to preserve them in version control.

## Validation

For changes to these scripts, run at least:

```powershell
$ErrorActionPreference = "Stop"
Get-ChildItem -Path C:\Users\ROG\.codex\skills\local-task-hooks\scripts -File |
  Where-Object { $_.Extension -eq ".ps1" } |
  ForEach-Object {
    $tokens = $null
    $parseErrors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($_.FullName, [ref]$tokens, [ref]$parseErrors) | Out-Null
    if ($parseErrors) { throw $parseErrors[0] }
  }
```

When feasible, also run one success command, one failing command, one file-changing command, and one manual start/complete flow.
