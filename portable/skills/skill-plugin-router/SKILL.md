---
name: skill-plugin-router
description: Route a draft or submitted Codex request to the right skills, plugin-backed skills, apps, connectors, and install/search actions. Use when the user asks which skills/plugins should trigger, wants a preflight for a draft prompt, says skill routing/plugin routing/capability routing, or asks in Chinese such as 技能匹配, 插件匹配, 自动识别应该触发的 skills/plugins, 路由这个请求, 根据上下文选择技能, 判断该用哪个插件.
---

# Skill Plugin Router

## Purpose

Identify the smallest useful set of Codex capabilities for a user request by combining the latest message, prior thread context, file/workspace clues, explicit mentions, and the available skills/plugins visible in the current session.

Important boundary: a skill cannot intercept unsent text in the compose box, change Codex's built-in trigger engine, or force-load another skill before the message is sent. It can route a submitted request or a pasted draft, and it can tell the agent which skills/plugins to use next.

Handle Chinese-language routing requests directly; do not require the user to translate trigger words such as "match skills", "match plugins", "route this request", or "choose capabilities from context".

## Routing Workflow

1. Restate the effective request in one sentence, giving priority to the newest user message over older thread context.
2. Build the capability inventory from the visible Skills/Plugins/App context. If the user asks for installed/local availability, or the visible context is incomplete, run:

```bash
python scripts/scan_codex_capabilities.py --format markdown
```

3. Read `references/routing-rubric.md` when the routing is ambiguous, multi-skill, plugin-heavy, or user-facing.
4. Select only capabilities that materially change how the agent should work. Prefer fewer, high-confidence triggers over a long adjacent list.
5. If execution is requested, load or consult the selected skill instructions before acting when their `SKILL.md` path is available. For connector/app/plugin tools that are not currently callable, use tool discovery where available instead of assuming the tool exists.

## Selection Rules

- Treat explicit `$skill`, plugin, connector, file-type, or app mentions as strong signals.
- Match by task behavior, not by product name alone. If a product name only has a near-match skill, label it as a near match.
- Prefer plugin-backed skills when the task depends on a connected service, such as GitHub, Google Drive, Linear, documents, presentations, or spreadsheets.
- Use multiple skills only when each covers a distinct part of the workflow. State the order.
- Do not revive older context when the newest request narrows or changes scope.
- If the task needs current product/API facts, route to an official-docs workflow and verify current docs before answering.
- If a required connector/plugin is missing, recommend search/install only when the user explicitly needs that external service.

## Output Format

For a routing-only request, keep the answer compact:

```markdown
**Recommended Route**
- `$skill-a` or `plugin:skill`: confidence, why, when to use it
- `Plugin/App`: confidence, why, required action such as use/search/install

**Invocation**
Use `$skill-a` and `$skill-b` to ...

**Notes**
One or two constraints, missing inputs, or boundary notes if they affect the route.
```

For a request that asks to both route and execute, give the route first in one or two lines, then proceed with the work.

## Local Inventory Script

Use `scripts/scan_codex_capabilities.py` to inspect this machine's local Codex capability folders. It reports:

- skills found under `CODEX_HOME/skills` or `~/.codex/skills`;
- plugin-cached skills found under `~/.codex/plugins/cache`;
- local plugin manifests found under `.codex-plugin/plugin.json`;
- plugin marketplace entries under `.agents/plugins/marketplace.json` when present.

The script is advisory. The active session context still decides which tools and connectors are actually callable.
