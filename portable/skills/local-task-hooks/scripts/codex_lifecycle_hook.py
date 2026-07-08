#!/usr/bin/env python3
"""Codex lifecycle hook for local task snapshots, summaries, and failure logs.

This script is intentionally quiet: it reads the Codex hook payload from stdin,
writes local artifacts, and exits 0 so it does not block normal Codex work.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKIP_DIRS = {
    ".git",
    ".hook",
    ".hook-acceptance",
    ".hook-global-acceptance",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "artifacts",
    "temp_analysis",
    "build",
    "dist",
}
INVENTORY_LIMIT = int(os.environ.get("CODEX_HOOK_INVENTORY_LIMIT", "800"))
INVENTORY_TIME_BUDGET_SECONDS = float(os.environ.get("CODEX_HOOK_INVENTORY_SECONDS", "2.0"))
PAYLOAD_LIMIT = 24000


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def slug(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", value.lower()).strip("-")
    return (text or "codex-lifecycle")[:64].strip("-") or "codex-lifecycle"


def read_payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {"payload": data}
    except json.JSONDecodeError:
        return {"raw_stdin": raw[:PAYLOAD_LIMIT]}


def iter_values(data: Any):
    if isinstance(data, dict):
        for key, value in data.items():
            yield key, value
            yield from iter_values(value)
    elif isinstance(data, list):
        for value in data:
            yield from iter_values(value)


def resolve_cwd(data: dict[str, Any]) -> Path:
    preferred = {
        "cwd",
        "workingDirectory",
        "working_directory",
        "projectRoot",
        "project_root",
        "workspaceRoot",
        "workspace_root",
        "repoPath",
        "repositoryPath",
    }
    for key, value in iter_values(data):
        if key in preferred and isinstance(value, str):
            path = Path(value).expanduser()
            if usable_workspace_path(path):
                return path.resolve()
    for env_name in ("CODEX_WORKSPACE_ROOT", "CODEX_PROJECT_ROOT", "PWD", "INIT_CWD"):
        raw = os.environ.get(env_name)
        if raw:
            path = Path(raw).expanduser()
            if usable_workspace_path(path):
                return path.resolve()
    try:
        cwd = Path.cwd().resolve()
        if usable_workspace_path(cwd):
            return cwd
    except Exception:
        pass
    return orphan_workspace(data)


def is_codex_app_install_dir(path: Path) -> bool:
    parts = {part.lower() for part in path.parts}
    return "windowsapps" in parts and any(part.lower().startswith("openai.codex_") for part in path.parts)


def usable_workspace_path(path: Path) -> bool:
    try:
        resolved = path.resolve()
        if is_codex_app_install_dir(resolved):
            return False
        if not resolved.exists() or not resolved.is_dir():
            return False
        hook_dir = resolved / ".hook"
        hook_dir.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def orphan_workspace(data: dict[str, Any]) -> Path:
    raw = json.dumps(data, sort_keys=True, ensure_ascii=True, default=str)[:4000]
    digest = hashlib.sha256(raw.encode("utf-8", "replace")).hexdigest()[:16]
    path = Path.home() / ".codex" / "hooks" / "local-task-hooks" / "orphan-workspaces" / digest
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def session_key(data: dict[str, Any], cwd: Path) -> str:
    preferred = {
        "session_id",
        "sessionId",
        "conversation_id",
        "conversationId",
        "thread_id",
        "threadId",
    }
    for key, value in iter_values(data):
        if key in preferred and isinstance(value, str) and value.strip():
            return slug(value.strip())
    digest = hashlib.sha256(str(cwd).encode("utf-8", "replace")).hexdigest()[:16]
    return f"default-{digest}"


def hook_root(cwd: Path) -> Path:
    return cwd / ".hook"


def current_file(cwd: Path) -> Path:
    return hook_root(cwd) / "lifecycle-current.json"


def run_dir_root(cwd: Path) -> Path:
    return hook_root(cwd) / "runs"


def read_current(cwd: Path) -> dict[str, Any]:
    path = current_file(cwd)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_current(cwd: Path, state: dict[str, Any]) -> None:
    path = current_file(cwd)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=True), encoding="utf-8")


def run_git(cwd: Path, args: list[str], timeout: float = 1.0) -> list[str]:
    try:
        proc = subprocess.run(
            ["git", "-c", "core.longpaths=true", *args],
            cwd=str(cwd),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except Exception as exc:
        return [f"<git failed: {exc}>"]
    text = proc.stdout if proc.stdout.strip() else proc.stderr
    return text.splitlines()


def git_info(cwd: Path) -> dict[str, Any]:
    inside = run_git(cwd, ["rev-parse", "--is-inside-work-tree"])
    if not inside or inside[0].strip() != "true":
        return {"is_repository": False}
    return {
        "is_repository": True,
        "root": "\n".join(run_git(cwd, ["rev-parse", "--show-toplevel"])).strip(),
        "branch": "\n".join(run_git(cwd, ["branch", "--show-current"])).strip(),
        "head": "\n".join(run_git(cwd, ["rev-parse", "--short", "HEAD"])).strip(),
        "status_short": run_git(cwd, ["status", "--short"]),
        "diff_stat": run_git(cwd, ["diff", "--stat"]),
    }


def inventory(cwd: Path) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    truncated = False
    timed_out = False
    total_count = 0
    total_bytes = 0
    started = time.monotonic()

    def onerror(_error: OSError) -> None:
        return None

    for root, dirs, names in os.walk(cwd, onerror=onerror):
        if time.monotonic() - started > INVENTORY_TIME_BUDGET_SECONDS:
            truncated = True
            timed_out = True
            break
        dirs[:] = [name for name in dirs if name not in SKIP_DIRS]
        root_path = Path(root)
        for name in names:
            if time.monotonic() - started > INVENTORY_TIME_BUDGET_SECONDS:
                truncated = True
                timed_out = True
                break
            path = root_path / name
            try:
                stat = path.stat()
            except OSError:
                continue
            total_count += 1
            total_bytes += stat.st_size
            if len(files) >= INVENTORY_LIMIT:
                truncated = True
                continue
            try:
                rel = str(path.relative_to(cwd))
            except ValueError:
                rel = str(path)
            files.append(
                {
                    "path": rel,
                    "length": stat.st_size,
                    "last_write_time_utc": datetime.fromtimestamp(
                        stat.st_mtime, timezone.utc
                    ).isoformat(),
                }
            )
        if timed_out:
            break

    files.sort(key=lambda item: item["path"].lower())
    return {
        "file_count": total_count,
        "total_bytes": total_bytes,
        "listed_count": len(files),
        "truncated": truncated,
        "timed_out": timed_out,
        "time_budget_seconds": INVENTORY_TIME_BUDGET_SECONDS,
        "files": files,
    }


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True), encoding="utf-8")


def write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def compact_payload(data: dict[str, Any]) -> str:
    text = json.dumps(data, indent=2, ensure_ascii=True, default=str)
    if len(text) > PAYLOAD_LIMIT:
        return text[:PAYLOAD_LIMIT] + "\n... truncated ..."
    return text


def create_snapshot(cwd: Path, key: str, event: str, data: dict[str, Any]) -> Path:
    run_dir = run_dir_root(cwd) / f"{timestamp()}-codex-lifecycle-{key[:12]}"
    snap = {
        "name": "codex-lifecycle",
        "event": event,
        "session_key": key,
        "created_at": utc_now(),
        "working_directory": str(cwd),
        "git": git_info(cwd),
        "inventory": inventory(cwd),
    }
    write_json(run_dir / "pre-snapshot.json", snap)
    write_json(run_dir / "session-start-payload.json", data)

    lines = [
        "# Pre-change Snapshot",
        "",
        f"- Event: {event}",
        f"- Session key: {key}",
        f"- Created at UTC: {snap['created_at']}",
        f"- Working directory: {cwd}",
        "",
    ]
    git = snap["git"]
    if git.get("is_repository"):
        lines.extend(
            [
                "## Git",
                "",
                f"- Root: {git.get('root', '')}",
                f"- Branch: {git.get('branch', '')}",
                f"- Head: {git.get('head', '')}",
                "",
                "### Status",
                "",
                "```text",
                *(git.get("status_short", []) or ["Clean working tree."]),
                "```",
                "",
            ]
        )
    inv = snap["inventory"]
    lines.extend(
        [
            "## Inventory",
            "",
            f"- File count: {inv['file_count']}",
            f"- Total bytes: {inv['total_bytes']}",
            f"- Listed files: {inv['listed_count']}",
            f"- Truncated: {inv['truncated']}",
        ]
    )
    write_lines(run_dir / "pre-snapshot.md", lines)

    state = read_current(cwd)
    sessions = state.setdefault("sessions", {})
    sessions[key] = {"run_directory": str(run_dir), "updated_at": utc_now()}
    state["last_session_key"] = key
    write_current(cwd, state)
    return run_dir


def create_minimal_run_dir(cwd: Path, key: str, event: str, data: dict[str, Any]) -> Path:
    run_dir = run_dir_root(cwd) / f"{timestamp()}-codex-lifecycle-{key[:12]}"
    snap = {
        "name": "codex-lifecycle",
        "event": event,
        "session_key": key,
        "created_at": utc_now(),
        "working_directory": str(cwd),
        "git": git_info(cwd),
        "inventory": {
            "file_count": 0,
            "total_bytes": 0,
            "listed_count": 0,
            "truncated": True,
            "timed_out": False,
            "time_budget_seconds": 0.0,
            "files": [],
        },
        "minimal": True,
    }
    write_json(run_dir / "pre-snapshot.json", snap)
    write_json(run_dir / f"{slug(event)}-payload.json", data)
    write_lines(
        run_dir / "pre-snapshot.md",
        [
            "# Pre-change Snapshot",
            "",
            f"- Event: {event}",
            f"- Session key: {key}",
            f"- Created at UTC: {snap['created_at']}",
            f"- Working directory: {cwd}",
            "- Mode: minimal fallback; no full inventory was captured.",
        ],
    )
    state = read_current(cwd)
    sessions = state.setdefault("sessions", {})
    sessions[key] = {"run_directory": str(run_dir), "updated_at": utc_now()}
    state["last_session_key"] = key
    write_current(cwd, state)
    return run_dir


def find_run_dir(cwd: Path, key: str) -> Path | None:
    state = read_current(cwd)
    session = state.get("sessions", {}).get(key)
    if isinstance(session, dict) and isinstance(session.get("run_directory"), str):
        path = Path(session["run_directory"])
        if path.exists():
            return path
    last = state.get("last_session_key")
    if isinstance(last, str):
        session = state.get("sessions", {}).get(last)
        if isinstance(session, dict) and isinstance(session.get("run_directory"), str):
            path = Path(session["run_directory"])
            if path.exists():
                return path
    return None


def ensure_run_dir(cwd: Path, key: str, event: str, data: dict[str, Any]) -> Path:
    return find_run_dir(cwd, key) or create_snapshot(cwd, key, event, data)


def is_failure_payload(data: dict[str, Any]) -> bool:
    for key, value in iter_values(data):
        lowered = str(key).lower()
        if lowered in {"exit_code", "exitcode", "status_code"}:
            try:
                if int(value) != 0:
                    return True
            except Exception:
                pass
        if lowered in {"status", "outcome", "result"} and isinstance(value, str):
            if value.lower() in {"failed", "failure", "error", "errored"}:
                return True
        if lowered in {"error", "stderr", "exception"}:
            if isinstance(value, str) and value.strip():
                return True
            if isinstance(value, dict) and value:
                return True
    return False


def post_tool_use(cwd: Path, key: str, event: str, data: dict[str, Any]) -> None:
    if not is_failure_payload(data):
        return
    run_dir = find_run_dir(cwd, key) or create_minimal_run_dir(cwd, key, event, data)
    failures = run_dir / "failures"
    failure_path = failures / f"{timestamp()}-post-tool-use.md"
    write_json(failures / f"{timestamp()}-post-tool-use.json", data)
    lines = [
        "# Tool Failure",
        "",
        f"- Event: {event}",
        f"- Captured at UTC: {utc_now()}",
        f"- Working directory: {cwd}",
        "",
        "## Payload",
        "",
        "```json",
        compact_payload(data),
        "```",
    ]
    write_lines(failure_path, lines)


def compare_inventory(before: dict[str, Any], after: dict[str, Any]) -> dict[str, list[str]]:
    before_files = {item["path"]: item for item in before.get("files", [])}
    after_files = {item["path"]: item for item in after.get("files", [])}
    added = sorted(set(after_files) - set(before_files))
    removed = sorted(set(before_files) - set(after_files))
    changed = sorted(
        path
        for path in set(before_files) & set(after_files)
        if before_files[path].get("length") != after_files[path].get("length")
        or before_files[path].get("last_write_time_utc")
        != after_files[path].get("last_write_time_utc")
    )
    return {"added": added, "removed": removed, "changed": changed}


def stop_summary(cwd: Path, key: str, event: str, data: dict[str, Any]) -> None:
    run_dir = find_run_dir(cwd, key) or create_minimal_run_dir(cwd, key, event, data)
    snapshot_path = run_dir / "pre-snapshot.json"
    if not snapshot_path.exists():
        return
    try:
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except Exception:
        return

    after = {"git": git_info(cwd), "inventory": inventory(cwd), "captured_at": utc_now()}
    write_json(run_dir / "stop-payload.json", data)
    write_json(run_dir / "post-state.json", after)
    changes = compare_inventory(snapshot.get("inventory", {}), after["inventory"])
    failure_files = sorted((run_dir / "failures").glob("*.md")) if (run_dir / "failures").exists() else []

    lines = [
        "# Codex Lifecycle Summary",
        "",
        f"- Event: {event}",
        f"- Session key: {key}",
        f"- Started at UTC: {snapshot.get('created_at', '')}",
        f"- Ended at UTC: {after['captured_at']}",
        f"- Working directory: {cwd}",
        "",
    ]
    git = after["git"]
    if git.get("is_repository"):
        lines.extend(
            [
                "## Git After Turn",
                "",
                f"- Branch: {git.get('branch', '')}",
                f"- Head: {git.get('head', '')}",
                "",
                "```text",
                *(git.get("status_short", []) or ["Clean working tree."]),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## File Inventory Changes",
            "",
            f"- Added: {len(changes['added'])}",
            f"- Changed: {len(changes['changed'])}",
            f"- Removed: {len(changes['removed'])}",
            f"- Failure logs: {len(failure_files)}",
            "",
        ]
    )
    for title, items in [
        ("Added", changes["added"]),
        ("Changed", changes["changed"]),
        ("Removed", changes["removed"]),
    ]:
        if items:
            lines.extend([f"### {title}", "", "```text"])
            lines.extend(items[:120])
            if len(items) > 120:
                lines.append("... truncated ...")
            lines.extend(["```", ""])
    if failure_files:
        lines.extend(["## Failure Logs", ""])
        for path in failure_files:
            lines.append(f"- {path.name}")
    write_lines(run_dir / "summary.md", lines)


def append_debug_log(cwd: Path, event: str, data: dict[str, Any]) -> None:
    log_path = hook_root(cwd) / "lifecycle-events.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": utc_now(),
        "event": event,
        "cwd": str(cwd),
        "keys": sorted(data.keys()),
    }
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=True) + "\n")


def main() -> int:
    event = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    data = read_payload()
    cwd = resolve_cwd(data)
    key = session_key(data, cwd)
    try:
        append_debug_log(cwd, event, data)
        if event.lower() == "sessionstart":
            create_snapshot(cwd, key, event, data)
        elif event.lower() == "posttooluse":
            post_tool_use(cwd, key, event, data)
        elif event.lower() == "stop":
            stop_summary(cwd, key, event, data)
    except Exception as exc:
        fallback = Path.home() / ".codex" / "hooks" / "local-task-hooks" / "errors.log"
        fallback.parent.mkdir(parents=True, exist_ok=True)
        with fallback.open("a", encoding="utf-8") as handle:
            handle.write(f"{utc_now()} {event} {cwd} {exc!r}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
