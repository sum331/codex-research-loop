# Codex Research Loop

Codex Research Loop is a personal Codex plugin for reusable, project-local
scientific workflow orchestration.

It provides:

- Project-local research state under `.research-loop/`.
- Natural-language prompt normalization and multi-path task routing.
- Adaptive research storage policies for existing and new projects.
- Content ingest for articles, local files, and standardized data packages.
- Source lookup, Zotero/BibTeX/CSL-JSON export, and llm-wiki handoff support.
- Claim-evidence structural verification.
- Deep-loop gate decisions for `route_next`, `retry_same_route`,
  `escalate_problem_loop`, and `pause_for_human`.
- Isolated problem-loop diagnosis with generated expert panels and gated
  promotion before core project edits.
- Unattended `auto-loop` validation/test/repair cycles connected to deep-loop
  dispatch.
- MCP tools and a Codex skill entrypoint.

## Layout

- `.codex-plugin/plugin.json` - Codex plugin manifest.
- `.mcp.json` - MCP server registration.
- `scripts/research_loop.py` - dependency-free CLI runtime.
- `scripts/mcp_server.py` - stdio MCP wrapper around the CLI.
- `skills/research-loop/SKILL.md` - Codex skill instructions.
- `templates/` - JSON/Markdown schemas used by the runtime.

## Quick Smoke Test

```powershell
python scripts/research_loop.py --cwd "D:\Loop\scratch\research-loop-smoke" auto-loop --goal "smoke test" --skip-validate --test-command "cmd /c exit /b 0" --current-subchain P5 --next-subchain P6 --format json
```

## Notes

This repository stores the plugin source only. Runtime project ledgers, smoke
test outputs, scratch labs, and local caches are intentionally ignored.
