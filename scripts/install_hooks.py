#!/usr/bin/env python3
"""Install or update Codex lifecycle hooks for codex-research-loop."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


PLUGIN_NAME = "codex-research-loop"
HOOK_SCRIPT = Path(__file__).resolve().parent / "codex_research_lifecycle_hook.py"
HOOKS_PATH = Path.home() / ".codex" / "hooks.json"
BUNDLED_PYTHON = Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies" / "python" / "python.exe"


def ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def python_executable() -> Path:
    if BUNDLED_PYTHON.exists():
        return BUNDLED_PYTHON
    if sys.executable:
        return Path(sys.executable)
    found = shutil.which("python")
    if found:
        return Path(found)
    raise RuntimeError("Could not locate a Python executable.")


def hook_command(event: str) -> str:
    py = ps_quote(str(python_executable()))
    script = ps_quote(str(HOOK_SCRIPT))
    return f'powershell -NoProfile -ExecutionPolicy Bypass -Command "& {py} {script} {event}"'


def load_config() -> dict:
    if not HOOKS_PATH.exists():
        return {"hooks": {}}
    try:
        data = json.loads(HOOKS_PATH.read_text(encoding="utf-8"))
    except Exception:
        backup = HOOKS_PATH.with_suffix(".json.bak-codex-research-loop")
        backup.write_text(HOOKS_PATH.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
        return {"hooks": {}}
    if not isinstance(data, dict):
        return {"hooks": {}}
    hooks = data.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        data["hooks"] = {}
    return data


def is_research_loop_block(block: dict) -> bool:
    hooks = block.get("hooks")
    if not isinstance(hooks, list):
        return False
    for hook in hooks:
        if isinstance(hook, dict):
            command = str(hook.get("command", ""))
            if PLUGIN_NAME in command or "codex_research_lifecycle_hook.py" in command:
                return True
    return False


def set_event(config: dict, event: str, timeout: int, status: str) -> None:
    hooks = config.setdefault("hooks", {})
    blocks = hooks.setdefault(event, [])
    if not isinstance(blocks, list):
        blocks = []
    blocks = [block for block in blocks if not (isinstance(block, dict) and is_research_loop_block(block))]
    blocks.append(
        {
            "hooks": [
                {
                    "type": "command",
                    "command": hook_command(event),
                    "timeout": timeout,
                    "statusMessage": status,
                }
            ]
        }
    )
    hooks[event] = blocks


def main() -> int:
    if not HOOK_SCRIPT.exists():
        print(f"Missing hook script: {HOOK_SCRIPT}", file=sys.stderr)
        return 2
    config = load_config()
    set_event(config, "SessionStart", 10, "Starting research loop snapshot")
    set_event(config, "PostToolUse", 10, "Recording research loop tool event")
    set_event(config, "Stop", 10, "Writing research loop checkpoint")
    HOOKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    HOOKS_PATH.write_text(json.dumps(config, indent=2, ensure_ascii=True), encoding="utf-8")
    print(f"Installed {PLUGIN_NAME} hooks in {HOOKS_PATH}")
    print(f"Hook script: {HOOK_SCRIPT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
