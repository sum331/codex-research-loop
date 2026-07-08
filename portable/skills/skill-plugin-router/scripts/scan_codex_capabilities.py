#!/usr/bin/env python3
"""Scan local Codex skill and plugin metadata.

This helper is intentionally read-only. It gives the routing skill a current
inventory without assuming every discovered capability is active in the session.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


def codex_home() -> Path:
    raw = os.environ.get("CODEX_HOME")
    if raw:
        return Path(raw).expanduser()
    return Path.home() / ".codex"


def parse_frontmatter(path: Path) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    frontmatter: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        frontmatter.append(line)

    data: dict[str, str] = {}
    i = 0
    while i < len(frontmatter):
        line = frontmatter[i]
        if ":" not in line or line.startswith((" ", "\t")):
            i += 1
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if value in {">", "|", ">-", "|-"}:
            block: list[str] = []
            i += 1
            while i < len(frontmatter):
                candidate = frontmatter[i]
                if candidate and not candidate.startswith((" ", "\t")) and ":" in candidate:
                    i -= 1
                    break
                block.append(candidate.strip())
                i += 1
            value = " ".join(part for part in block if part).strip()
        if key in {"name", "description"}:
            data[key] = value
        i += 1
    return data


def rel(path: Path) -> str:
    try:
        return str(path.resolve())
    except OSError:
        return str(path)


def scan_skills(home: Path) -> list[dict[str, str]]:
    roots = [home / "skills", home / "plugins" / "cache"]
    found: dict[Path, dict[str, str]] = {}
    for root in roots:
        if not root.exists():
            continue
        for skill_md in root.rglob("SKILL.md"):
            meta = parse_frontmatter(skill_md)
            name = meta.get("name") or skill_md.parent.name
            found[skill_md] = {
                "name": name,
                "description": meta.get("description", ""),
                "path": rel(skill_md.parent),
                "source": "plugin-cache" if "plugins" in skill_md.parts else "skills",
            }
    return sorted(found.values(), key=lambda item: (item["name"], item["path"]))


def load_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def scan_plugin_manifests(home: Path, extra_roots: list[Path]) -> list[dict[str, Any]]:
    roots = [home / "plugins", home / "plugins" / "cache", Path.cwd(), *extra_roots]
    manifests: dict[Path, dict[str, Any]] = {}
    for root in roots:
        if not root.exists():
            continue
        for manifest in root.rglob(".codex-plugin/plugin.json"):
            data = load_json(manifest)
            if not isinstance(data, dict):
                continue
            manifests[manifest] = {
                "name": data.get("name") or manifest.parent.parent.name,
                "path": rel(manifest.parent.parent),
                "description": data.get("description") or data.get("interface", {}).get("description", ""),
            }
    return sorted(manifests.values(), key=lambda item: (str(item["name"]), item["path"]))


def scan_marketplaces(home: Path, extra_roots: list[Path]) -> list[dict[str, Any]]:
    roots = [home, Path.cwd(), *extra_roots]
    entries: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for root in roots:
        marketplace = root / ".agents" / "plugins" / "marketplace.json"
        if marketplace in seen or not marketplace.exists():
            continue
        seen.add(marketplace)
        data = load_json(marketplace)
        if not isinstance(data, dict):
            continue
        for plugin in data.get("plugins", []):
            if not isinstance(plugin, dict):
                continue
            entries.append(
                {
                    "marketplace": rel(marketplace),
                    "name": plugin.get("name", ""),
                    "category": plugin.get("category", ""),
                    "installation": plugin.get("policy", {}).get("installation", ""),
                    "authentication": plugin.get("policy", {}).get("authentication", ""),
                    "source": plugin.get("source", {}),
                }
            )
    return sorted(entries, key=lambda item: (item["name"], item["marketplace"]))


def as_markdown(data: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# Codex Capability Inventory")
    lines.append("")
    lines.append(f"- Codex home: `{data['codex_home']}`")
    lines.append(f"- Skills: {len(data['skills'])}")
    lines.append(f"- Plugin manifests: {len(data['plugin_manifests'])}")
    lines.append(f"- Marketplace entries: {len(data['marketplace_entries'])}")
    lines.append("")

    lines.append("## Skills")
    for item in data["skills"]:
        desc = f" - {item['description']}" if item.get("description") else ""
        lines.append(f"- `{item['name']}` ({item['source']}): `{item['path']}`{desc}")
    if not data["skills"]:
        lines.append("- None found")
    lines.append("")

    lines.append("## Plugin Manifests")
    for item in data["plugin_manifests"]:
        desc = f" - {item['description']}" if item.get("description") else ""
        lines.append(f"- `{item['name']}`: `{item['path']}`{desc}")
    if not data["plugin_manifests"]:
        lines.append("- None found")
    lines.append("")

    lines.append("## Marketplace Entries")
    for item in data["marketplace_entries"]:
        policy = "/".join(part for part in [item.get("installation"), item.get("authentication")] if part)
        policy_text = f" [{policy}]" if policy else ""
        lines.append(f"- `{item['name']}` ({item.get('category', '')}){policy_text}: `{item['marketplace']}`")
    if not data["marketplace_entries"]:
        lines.append("- None found")
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Scan local Codex skills and plugin metadata.")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument("--root", action="append", default=[], help="Extra root to scan for plugins/marketplaces.")
    args = parser.parse_args()

    home = codex_home()
    extra_roots = [Path(raw).expanduser() for raw in args.root]
    data = {
        "codex_home": rel(home),
        "skills": scan_skills(home),
        "plugin_manifests": scan_plugin_manifests(home, extra_roots),
        "marketplace_entries": scan_marketplaces(home, extra_roots),
    }
    if args.format == "markdown":
        print(as_markdown(data))
    else:
        print(json.dumps(data, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
