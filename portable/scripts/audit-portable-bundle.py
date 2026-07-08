from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    ROOT / "manifests" / "codex-portable-manifest.json",
    ROOT / "dispatch" / "codex_capability_dispatch_inventory_20260702.md",
    ROOT / "plugins" / "prompt-submit-skill-router" / ".codex-plugin" / "plugin.json",
    ROOT / "plugins" / "prompt-submit-skill-router" / "scripts" / "user_prompt_submit_router.py",
    ROOT / "skills" / "skill-plugin-router" / "SKILL.md",
    ROOT / "skills" / "local-task-hooks" / "SKILL.md",
    ROOT / "hooks" / "local-task-hooks" / "codex_lifecycle_hook.py",
    ROOT / "scripts" / "install-codex-portable.ps1",
]

FORBIDDEN_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "orphan-workspaces"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".log", ".tmp", ".sqlite", ".db", ".pem", ".pfx"}
LIKELY_SECRET_PATTERNS = [
    re.compile(r"sk-[0-9a-fA-F]{24,}"),
    re.compile(r"(?i)(DEEPSEEK_API_KEY|OPENAI_API_KEY)\s*=\s*[\"']?sk-[0-9a-fA-F]{16,}"),
]


def is_text(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:4096]
    except OSError:
        return False
    return b"\0" not in chunk


def main() -> int:
    errors: list[str] = []
    for required in REQUIRED_PATHS:
        if not required.exists():
            errors.append(f"missing required path: {required.relative_to(ROOT)}")

    manifest_path = ROOT / "manifests" / "codex-portable-manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        for skill in ["skill-plugin-router", "local-task-hooks", "z2-harness-loop"]:
            if skill not in manifest.get("packaged_skills", []):
                errors.append(f"manifest missing skill: {skill}")
        if manifest.get("includes_secrets") is not False:
            errors.append("manifest must declare includes_secrets=false")

    for path in ROOT.rglob("*"):
        relative_parts = set(path.relative_to(ROOT).parts)
        if relative_parts & FORBIDDEN_PARTS:
            errors.append(f"forbidden cache/git path: {path.relative_to(ROOT)}")
            continue
        if path.is_file() and path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f"forbidden generated file: {path.relative_to(ROOT)}")
            continue
        if path.is_file() and is_text(path):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in LIKELY_SECRET_PATTERNS:
                if pattern.search(text):
                    errors.append(f"likely secret pattern in: {path.relative_to(ROOT)}")
                    break

    print(
        json.dumps(
            {
                "portable_root": str(ROOT),
                "file_count": sum(1 for item in ROOT.rglob("*") if item.is_file()),
                "errors": errors,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
