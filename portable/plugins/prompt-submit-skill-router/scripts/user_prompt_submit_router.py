#!/usr/bin/env python3
"""Route submitted Codex prompts through the registered capability table.

Codex calls this script as a ``UserPromptSubmit`` hook. The hook cannot force
the model to load a skill or call an MCP/app tool directly; it can inject
model-visible ``additionalContext`` before the turn starts. This script uses
that channel to recommend the capabilities that should be invoked for the
current turn.

Sources, in priority order:

1. Current hook payload prompt.
2. Optional message/transcript fields when Codex includes them.
3. Recent router log matches, only as weak continuation context.
4. The Markdown capability registry maintained by the project.
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REGISTRY_FILENAME = "codex_capability_dispatch_inventory_20260702.md"
REGISTRY_MARKER_RE = re.compile(r"<!--\s*capability-registry-id:\s*([^>]+?)\s*-->")
TABLE_ROW_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|(.+)\|$")
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_.@:/#-]*|[\u4e00-\u9fff]{2,}", re.I)
SIGNIFICANT_SHORT_TOKENS = {
    "ai",
    "api",
    "ci",
    "hf",
    "js",
    "pr",
    "ui",
}
EXTERNAL_SERVICE_TOKENS = {
    "chrome",
    "figma",
    "github",
    "google",
    "linear",
    "readwise",
}

CONTINUATION_WORDS = (
    "continue",
    "next step",
    "previous",
    "above",
    "\u7ee7\u7eed",
    "\u63a5\u7740",
    "\u4e0b\u4e00\u6b65",
    "\u4e0a\u6587",
    "\u521a\u624d",
    "\u521a\u521a",
    "\u8fd8\u662f",
)

ROUTING_WORDS = (
    "skill",
    "skills",
    "plugin",
    "plugins",
    "mcp",
    "hook",
    "hooks",
    "route",
    "routing",
    "registry",
    "dispatch",
    "\u6280\u80fd",
    "\u63d2\u4ef6",
    "\u8c03\u5ea6",
    "\u8def\u7531",
    "\u6ce8\u518c",
    "\u8c03\u5ea6\u8868",
    "\u5339\u914d",
    "\u8c03\u7528",
)

KIND_TERMS = {
    "skill": ("skill", "skills", "\u6280\u80fd"),
    "system-skill": ("skill", "skills", "\u6280\u80fd", "system"),
    "plugin": ("plugin", "plugins", "\u63d2\u4ef6", "connector", "app"),
    "personal-plugin": ("plugin", "plugins", "\u63d2\u4ef6", "router"),
    "mcp": ("mcp", "server", "connector"),
    "hook": ("hook", "hooks", "\u94a9\u5b50", "\u8fd0\u884c\u524d", "\u63d0\u4ea4\u524d"),
}

SPECIAL_TRIGGERS = {
    "skill:skill-plugin-router": (
        "route",
        "routing",
        "which skill",
        "which plugin",
        "skills/plugins",
        "\u8def\u7531",
        "\u8c03\u5ea6",
        "\u5339\u914d",
        "\u8c03\u5ea6\u8868",
    ),
    "system-skill:skill-creator": (
        "create skill",
        "update skill",
        "skill.md",
        "\u65b0\u5efa skill",
        "\u4fee\u590d skill",
        "\u66f4\u65b0 skill",
    ),
    "system-skill:plugin-creator": (
        "create plugin",
        "plugin manifest",
        ".codex-plugin",
        "\u65b0\u5efa\u63d2\u4ef6",
        "\u63d2\u4ef6 manifest",
    ),
    "plugin:prompt-submit-skill-router": (
        "userpromptsubmit",
        "prompt-submit",
        "before each run",
        "\u6bcf\u8f6e\u8fd0\u884c\u524d",
        "\u8fd0\u884c\u524d",
        "\u4e0a\u6587\u65e5\u5fd7",
    ),
    "hook:user:UserPromptSubmit:prompt-submit-skill-router": (
        "userpromptsubmit",
        "before each run",
        "\u6bcf\u8f6e\u8fd0\u884c\u524d",
        "\u8fd0\u884c\u524d hook",
        "\u5f53\u524d\u8f93\u5165",
    ),
    "plugin:browser@openai-bundled": (
        "localhost",
        "127.0.0.1",
        "browser",
        "\u6d4f\u89c8\u5668",
        "\u672c\u5730\u9875\u9762",
        "\u6253\u5f00\u672c\u5730",
    ),
    "plugin:chrome@openai-bundled": (
        "chrome",
        "cookie",
        "cookies",
        "logged-in",
        "\u767b\u5f55\u6001",
        "\u7528\u6237 chrome",
    ),
    "plugin:documents@openai-primary-runtime": (
        "docx",
        "word",
        "document",
        "\u6587\u6863",
        "\u6392\u7248",
    ),
    "plugin:presentations@openai-primary-runtime": (
        "ppt",
        "pptx",
        "slides",
        "presentation",
        "\u5e7b\u706f\u7247",
        "\u6c47\u62a5",
    ),
    "plugin:spreadsheets@openai-primary-runtime": (
        "xlsx",
        "excel",
        "csv",
        "spreadsheet",
        "\u8868\u683c",
    ),
    "skill:local-task-hooks": (
        "hook task",
        "local hook",
        "\u672c\u5730 hook",
        "\u4efb\u52a1 hook",
        "\u751f\u547d\u5468\u671f",
    ),
    "skill:z2-harness-loop": (
        "z2",
        "z2quijote",
        "quijote",
        "sobol",
        "ppr",
        "multi-fidelity",
        "multifidelity",
        "\u5f53\u524d\u8bba\u6587",
        "\u8bba\u6587\u521d\u7a3f",
        "\u7ee7\u7eed\u9879\u76ee",
    ),
    "skill:research-loop": (
        "research loop",
        "research-loop",
        "$research-loop",
        "deep-loop",
        "deep loop",
        "auto-loop",
        "auto loop",
        "auto-loop-watchdog",
        "auto loop watchdog",
        "problem-loop",
        "problem loop",
        "watchdog",
        "unattended",
        "route_next",
        "retry_same_route",
        "escalate_problem_loop",
        "continuation_contract",
        "research council",
        "adversarial gate",
        "arbiter",
        "\u79d1\u7814\u5de5\u4f5c\u6d41",
        "\u6df1\u5faa\u73af",
        "\u6df1\u94fe\u8def",
        "\u81ea\u52a8\u7eed\u8dd1",
        "\u65e0\u4eba\u503c\u5b88",
        "\u65e0\u4eba\u76d1\u7763",
        "\u4e13\u5bb6\u59d4\u5458\u4f1a",
        "\u7814\u7a76\u59d4\u5458\u4f1a",
        "\u5bf9\u6297 gate",
        "\u5bf9\u6297\u9600\u95e8",
        "\u9600\u95e8",
        "\u4ef2\u88c1",
    ),
    "skill:nature-reader": (
        "paper reader",
        "paper",
        "pdf paper",
        "\u8bba\u6587",
        "\u7cbe\u8bfb",
        "\u4e2d\u6587\u7cbe\u8bfb",
        "\u53cc\u8bed",
        "\u4e2d\u82f1\u6587",
    ),
    "skill:nature-citation": (
        "citation",
        "citations",
        "references",
        "\u5f15\u7528",
        "\u5f15\u6587",
        "\u53c2\u8003\u6587\u732e",
        "\u6587\u732e\u652f\u6301",
    ),
    "skill:academic-research-suite": (
        "literature review",
        "research",
        "academic paper",
        "manuscript",
        "\u6587\u732e\u7efc\u8ff0",
        "\u79d1\u7814",
        "\u5b66\u672f\u8bba\u6587",
        "\u5b9e\u9a8c\u8bbe\u8ba1",
    ),
    "skill:explain-complex-concepts": (
        "explain",
        "unpack",
        "clarify",
        "teach",
        "intuition",
        "complex concept",
        "conceptual explanation",
        "astronomy concept",
        "physics concept",
        "machine learning concept",
        "ml concept",
        "power spectrum",
        "residual-space learning",
        "emulator",
        "agn",
        "active galactic nucleus",
        "active galactic nuclei",
        "compton-thick",
        "compton thick",
        "j1030",
        "deep field",
        "fits",
        "wcs",
        "redshift",
        "attention",
        "attention mechanism",
        "transformer",
        "model focus",
        "euclid",
        "lsst",
        "rubin",
        "data release",
        "survey data release",
        "\u89e3\u91ca",
        "\u8bb2\u89e3",
        "\u62c6\u89e3",
        "\u6f84\u6e05",
        "\u76f4\u89c9",
        "\u6982\u5ff5",
        "\u590d\u6742\u95ee\u9898",
        "\u4e13\u4e1a\u95ee\u9898",
        "\u5929\u6587\u5b66",
        "\u5b87\u5b99\u5b66",
        "\u7269\u7406",
        "\u673a\u5668\u5b66\u4e60",
        "\u529f\u7387\u8c31",
        "\u6b8b\u5dee\u5b66\u4e60",
        "\u4eff\u771f\u5668",
        "\u6d3b\u52a8\u661f\u7cfb\u6838",
        "\u6df1\u573a",
        "\u91cd\u5ea6\u906e\u853d",
        "\u7ea2\u79fb",
        "\u6ce8\u610f\u529b",
        "\u6ce8\u610f\u529b\u673a\u5236",
        "\u6a21\u578b\u770b\u91cd\u70b9",
        "\u6570\u636e\u53d1\u5e03",
        "\u5de1\u5929",
    ),
}


@dataclass(frozen=True)
class Capability:
    registry_id: str
    kind: str
    name: str
    invocation: str
    function: str
    status: str
    path: str


@dataclass(frozen=True)
class Match:
    capability: Capability
    score: int
    reasons: tuple[str, ...]

    @property
    def confidence(self) -> str:
        if self.score >= 10:
            return "High"
        if self.score >= 5:
            return "Medium"
        return "Low"


def codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".codex"


def router_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_hook_input() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"prompt": raw}


def text_from_value(value: Any, max_chars: int = 5000) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value[-max_chars:]
    if isinstance(value, dict):
        parts: list[str] = []
        for key in ("role", "content", "text", "message", "prompt"):
            if key in value:
                parts.append(text_from_value(value[key], max_chars=max_chars))
        return " ".join(part for part in parts if part)[-max_chars:]
    if isinstance(value, list):
        parts = [text_from_value(item, max_chars=max_chars) for item in value[-8:]]
        return " ".join(part for part in parts if part)[-max_chars:]
    return str(value)[-max_chars:]


def prompt_from_payload(data: dict[str, Any]) -> str:
    for key in ("prompt", "userPrompt", "input", "message"):
        value = text_from_value(data.get(key))
        if value.strip():
            return value.strip()
    return ""


def context_from_payload(data: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("messages", "conversation", "transcript", "thread", "context"):
        value = text_from_value(data.get(key), max_chars=12000)
        if value:
            parts.append(value)
    return "\n".join(parts)[-16000:]


def roots_from_payload(data: dict[str, Any]) -> list[Path]:
    roots: list[Path] = []
    for key in ("cwd", "currentWorkingDirectory", "workspaceRoot", "repoRoot"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            roots.append(Path(value))
    roots.append(Path.cwd())
    default_project = Path(r"D:\work\pr_due_upload_files_20260317_220257")
    roots.append(default_project)
    unique: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        try:
            resolved = root.resolve()
        except OSError:
            resolved = root
        marker = str(resolved).casefold()
        if marker not in seen:
            unique.append(resolved)
            seen.add(marker)
    return unique


def registry_candidates(data: dict[str, Any]) -> list[Path]:
    candidates: list[Path] = []
    env_registry = os.environ.get("CODEX_CAPABILITY_REGISTRY")
    if env_registry:
        candidates.append(Path(env_registry))
    candidates.append(codex_home() / "docs" / REGISTRY_FILENAME)
    for root in roots_from_payload(data):
        current = root
        for _ in range(5):
            candidates.append(current / "docs" / REGISTRY_FILENAME)
            if current.parent == current:
                break
            current = current.parent
    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        marker = str(candidate).casefold()
        if marker not in seen:
            unique.append(candidate)
            seen.add(marker)
    return unique


def find_registry(data: dict[str, Any]) -> Path | None:
    for candidate in registry_candidates(data):
        if candidate.exists():
            return candidate
    return None


def clean_cell(value: str) -> str:
    value = value.strip()
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.I)
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def kind_from_registry_id(registry_id: str) -> str:
    if registry_id.startswith("system-skill:"):
        return "system-skill"
    if registry_id.startswith("skill:"):
        return "skill"
    if registry_id.startswith("plugin:prompt-submit"):
        return "personal-plugin"
    if registry_id.startswith("plugin:"):
        return "plugin"
    if registry_id.startswith("mcp:"):
        return "mcp"
    if registry_id.startswith("hook:"):
        return "hook"
    return "capability"


def name_from_registry_id(registry_id: str) -> str:
    if ":" not in registry_id:
        return registry_id
    if registry_id.startswith("hook:"):
        return registry_id.split(":", 2)[-1]
    return registry_id.split(":", 1)[1]


def path_for(capability: Capability) -> str:
    home = codex_home()
    rid = capability.registry_id
    if rid.startswith("skill:"):
        return str(home / "skills" / capability.name)
    if rid.startswith("system-skill:"):
        return str(home / "skills" / ".system" / capability.name)
    if rid.startswith("plugin:prompt-submit-skill-router"):
        return str(home / "plugins" / "prompt-submit-skill-router")
    if rid.startswith("plugin:"):
        return str(home / "config.toml")
    if rid.startswith("hook:user:"):
        return str(home / "hooks.json")
    if rid.startswith("mcp:"):
        return str(home / "config.toml")
    return capability.path


def parse_registry(path: Path) -> list[Capability]:
    capabilities: list[Capability] = []
    seen: set[str] = set()
    text = path.read_text(encoding="utf-8", errors="replace")
    for raw_line in text.splitlines():
        line = raw_line.strip()
        match = TABLE_ROW_RE.match(line)
        if not match:
            continue
        registry_id = match.group(1).strip()
        if ":" not in registry_id or registry_id in {"Registry ID", "插件 ID"}:
            continue
        cells = [clean_cell(cell) for cell in line.strip("|").split("|")]
        if len(cells) < 4 or registry_id in seen:
            continue
        invocation = cells[1]
        function = cells[2]
        status = cells[3]
        capability = Capability(
            registry_id=registry_id,
            kind=kind_from_registry_id(registry_id),
            name=name_from_registry_id(registry_id),
            invocation=invocation,
            function=function,
            status=status,
            path="",
        )
        capabilities.append(
            Capability(
                registry_id=capability.registry_id,
                kind=capability.kind,
                name=capability.name,
                invocation=capability.invocation,
                function=capability.function,
                status=capability.status,
                path=path_for(capability),
            )
        )
        seen.add(registry_id)

    marker_ids = {match.group(1).strip() for match in REGISTRY_MARKER_RE.finditer(text)}
    for registry_id in sorted(marker_ids - seen):
        capability = Capability(
            registry_id=registry_id,
            kind=kind_from_registry_id(registry_id),
            name=name_from_registry_id(registry_id),
            invocation="Registered marker only",
            function="See dispatch inventory table.",
            status="Registered",
            path="",
        )
        capabilities.append(
            Capability(
                registry_id=capability.registry_id,
                kind=capability.kind,
                name=capability.name,
                invocation=capability.invocation,
                function=capability.function,
                status=capability.status,
                path=path_for(capability),
            )
        )
    return capabilities


def fallback_capabilities() -> list[Capability]:
    home = codex_home()
    return [
        Capability(
            "skill:skill-plugin-router",
            "skill",
            "skill-plugin-router",
            "$skill-plugin-router",
            "Route prompts to skills/plugins/apps/connectors.",
            "OK",
            str(home / "skills" / "skill-plugin-router"),
        ),
        Capability(
            "system-skill:skill-creator",
            "system-skill",
            "skill-creator",
            "$skill-creator",
            "Create or update Codex skills.",
            "OK",
            str(home / "skills" / ".system" / "skill-creator"),
        ),
        Capability(
            "personal-plugin:prompt-submit-skill-router",
            "personal-plugin",
            "prompt-submit-skill-router",
            "UserPromptSubmit hook",
            "Inject routing guidance before each turn.",
            "OK",
            str(home / "plugins" / "prompt-submit-skill-router"),
        ),
    ]


def tokens(text: str) -> set[str]:
    return {match.group(0).casefold() for match in TOKEN_RE.finditer(text)}


def contains(text: str, needle: str) -> bool:
    return needle.casefold() in text.casefold()


def is_continuation(prompt: str) -> bool:
    return any(contains(prompt, word) for word in CONTINUATION_WORDS)


def recent_router_matches(limit: int = 12) -> list[str]:
    log_path = router_root() / "router.log"
    if not log_path.exists():
        return []
    try:
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]
    except OSError:
        return []
    matches: list[str] = []
    for line in lines:
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        for key in ("registry_ids", "matches"):
            values = record.get(key)
            if isinstance(values, list):
                matches.extend(str(value) for value in values)
    return matches[-limit:]


def recent_match_applies(capability: Capability, recent: Iterable[str]) -> bool:
    names = {capability.registry_id, capability.name}
    if capability.registry_id.startswith("skill:"):
        names.add(capability.registry_id.split(":", 1)[1])
    if capability.registry_id.startswith("system-skill:"):
        names.add(capability.registry_id.split(":", 1)[1])
    if capability.registry_id.startswith("plugin:"):
        names.add(capability.registry_id.split(":", 1)[1].split("@", 1)[0])
    return any(value in names for value in recent)


def score_capability(
    capability: Capability,
    prompt: str,
    context: str,
    recent: list[str],
) -> Match | None:
    prompt_norm = prompt.casefold()
    combined_context = f"{prompt}\n{context[-6000:]}".casefold()
    searchable = " ".join(
        [
            capability.registry_id,
            capability.name,
            capability.kind,
            capability.invocation,
            capability.function,
            capability.status,
        ]
    )
    capability_tokens = tokens(searchable)
    prompt_tokens = tokens(prompt)
    context_tokens = tokens(combined_context)

    score = 0
    reasons: list[str] = []

    explicit_terms = {
        capability.registry_id.casefold(),
        capability.name.casefold(),
        f"${capability.name}".casefold(),
    }
    for term in explicit_terms:
        if term and term in prompt_norm:
            score += 9
            reasons.append("explicit name/id")
            break

    for term in KIND_TERMS.get(capability.kind, ()):
        if contains(prompt, term):
            score += 1
            reasons.append(f"kind term: {term}")
            break

    special_trigger_hit = False
    for phrase in SPECIAL_TRIGGERS.get(capability.registry_id, ()):
        if contains(prompt, phrase):
            score += 6
            special_trigger_hit = True
            reasons.append(f"trigger: {phrase}")

    if capability.registry_id == "skill:nature-paper2ppt":
        has_presentation_intent = any(
            contains(prompt, phrase)
            for phrase in (
                "ppt",
                "pptx",
                "slides",
                "presentation",
                "journal club",
                "group meeting",
                "\u5e7b\u706f\u7247",
                "\u7ec4\u4f1a",
                "\u6c47\u62a5",
            )
        )
        has_paper_source = any(
            contains(prompt, phrase)
            for phrase in (
                "paper",
                "preprint",
                "article",
                "\u8bba\u6587",
                "\u6587\u732e",
                "\u79d1\u7814",
                "\u8bfb\u4e66\u62a5\u544a",
            )
        )
        if has_presentation_intent and has_paper_source:
            score += 10
            special_trigger_hit = True
            reasons.append("compound trigger: paper-to-ppt")

    if capability.registry_id == "skill:nature-polishing":
        has_edit_intent = any(
            contains(prompt, phrase)
            for phrase in (
                "polish",
                "rewrite",
                "revise",
                "translate",
                "\u6da6\u8272",
                "\u6539\u5199",
                "\u91cd\u6784",
                "\u7ffb\u8bd1",
            )
        )
        has_academic_context = any(
            contains(prompt, phrase)
            for phrase in (
                "nature",
                "academic",
                "manuscript",
                "paper",
                "\u82f1\u6587",
                "\u5b66\u672f",
                "\u8bba\u6587",
                "\u7a3f\u4ef6",
            )
        )
        if has_edit_intent and has_academic_context:
            score += 10
            special_trigger_hit = True
            reasons.append("compound trigger: academic polishing")

    prompt_overlap = capability_tokens & prompt_tokens
    useful_overlap = {
        token
        for token in prompt_overlap
        if len(token) >= 4 or token in SIGNIFICANT_SHORT_TOKENS or re.search(r"[\u4e00-\u9fff]", token)
    }
    if useful_overlap:
        score += min(6, len(useful_overlap) * 2)
        reasons.append("description overlap")

    service_overlap = prompt_tokens & capability_tokens & EXTERNAL_SERVICE_TOKENS
    if service_overlap and capability.kind in {"plugin", "personal-plugin", "skill"}:
        score += 3
        reasons.append("external service")

    if context and is_continuation(prompt):
        context_overlap = capability_tokens & context_tokens
        useful_context_overlap = {
            token
            for token in context_overlap
            if len(token) >= 5 or token in SIGNIFICANT_SHORT_TOKENS or re.search(r"[\u4e00-\u9fff]", token)
        }
        if useful_context_overlap:
            score += min(3, len(useful_context_overlap))
            reasons.append("prior-context overlap")

    if is_continuation(prompt) and recent_match_applies(capability, recent):
        score += 3
        reasons.append("recent router log")

    if any(contains(prompt, word) for word in ROUTING_WORDS) and capability.registry_id in {
        "skill:skill-plugin-router",
        "system-skill:skill-creator",
        "system-skill:plugin-creator",
        "plugin:prompt-submit-skill-router",
        "hook:user:UserPromptSubmit:prompt-submit-skill-router",
        "skill:local-task-hooks",
    }:
        score += 4
        reasons.append("routing governance task")

    threshold = 5 if special_trigger_hit or any(contains(prompt, word) for word in ROUTING_WORDS) else 6
    if score < threshold:
        return None
    return Match(capability=capability, score=score, reasons=tuple(dict.fromkeys(reasons)))


def choose_capabilities(
    capabilities: list[Capability],
    prompt: str,
    context: str,
    recent: list[str],
) -> list[Match]:
    matches: list[Match] = []
    for capability in capabilities:
        match = score_capability(capability, prompt, context, recent)
        if match is not None:
            matches.append(match)
    matches.sort(key=lambda item: (-item.score, item.capability.registry_id))

    result: list[Match] = []
    seen_prefixes: set[str] = set()
    for match in matches:
        rid = match.capability.registry_id
        prefix = rid
        if rid.startswith("hook:"):
            prefix = rid
        elif ":" in rid:
            prefix = rid.split(":", 1)[1].split("@", 1)[0]
        if prefix in seen_prefixes and len(result) >= 3:
            continue
        result.append(match)
        seen_prefixes.add(prefix)
        if len(result) >= 7:
            break
    return result


def action_for(capability: Capability) -> str:
    if capability.kind in {"skill", "system-skill"}:
        return f"Read {capability.path}\\SKILL.md before substantial work when this capability is used."
    if capability.kind in {"plugin", "personal-plugin"}:
        if capability.registry_id == "plugin:prompt-submit-skill-router":
            return "This plugin is already invoked by the UserPromptSubmit hook."
        return "Use tool_search to expose the plugin/app connector tools before calling them."
    if capability.kind == "mcp":
        if capability.registry_id == "mcp:classic:none":
            return "No classic MCP server is configured; use app connector tools when available."
        return "Verify the MCP server is configured and reachable before relying on it."
    if capability.kind == "hook":
        return "Do not manually run this hook unless debugging; verify its JSON/script entrypoint if changing it."
    return "Use the registered invocation path in the dispatch table."


def context_for(matches: list[Match], registry_path: Path | None, recent_used: bool) -> str:
    if not matches:
        return ""
    lines = [
        "Pre-run Codex capability dispatcher:",
        "Use this as advisory routing context; the latest user request remains authoritative.",
    ]
    if registry_path is not None:
        lines.append(f"Registry: {registry_path}")
    if recent_used:
        lines.append("Recent router log was used only as weak continuation context.")
    lines.append("Recommended invocation order:")
    for index, match in enumerate(matches, start=1):
        cap = match.capability
        reason = ", ".join(match.reasons[:3]) or "registry match"
        lines.append(
            f"{index}. {cap.registry_id} ({cap.kind}, {match.confidence}, score={match.score}) - "
            f"{cap.function} Invocation: {cap.invocation}. {action_for(cap)} Reason: {reason}."
        )
    lines.append(
        "Boundary: this hook cannot force-load a skill or call MCP/app tools by itself; "
        "the agent should follow the invocation instructions above before acting."
    )
    return "\n".join(lines)


def write_run_log(
    prompt: str,
    matches: list[Match],
    registry_path: Path | None,
    used_recent: bool,
) -> None:
    try:
        log_path = router_root() / "router.log"
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prompt_chars": len(prompt),
            "registry": str(registry_path) if registry_path else None,
            "used_recent_log": used_recent,
            "registry_ids": [match.capability.registry_id for match in matches],
            "matches": [match.capability.name for match in matches],
            "scores": {match.capability.registry_id: match.score for match in matches},
        }
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")
    except Exception:
        pass


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    data = read_hook_input()
    prompt = prompt_from_payload(data)
    if not prompt.strip():
        return 0

    registry_path = find_registry(data)
    capabilities = parse_registry(registry_path) if registry_path else fallback_capabilities()
    context = context_from_payload(data)
    recent = recent_router_matches()
    used_recent = bool(recent and is_continuation(prompt))
    matches = choose_capabilities(capabilities, prompt, context, recent if used_recent else [])
    write_run_log(prompt, matches, registry_path, used_recent)

    additional_context = context_for(matches, registry_path, used_recent)
    if not additional_context:
        return 0
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": additional_context,
                }
            },
            ensure_ascii=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
