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
- Auto-routed subchain startup through configurable agent command templates.
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

## Auto-Routed Agent Startup

`auto-loop` can consume a `deep-loop` `route_next` decision and start the next
subchain in the same unattended run:

```powershell
python scripts/research_loop.py --cwd "D:\Project" auto-loop `
  --goal "finish current research stage" `
  --test-command "python -m pytest" `
  --current-subchain P7 `
  --next-subchain P8 `
  --auto-route-next `
  --route-depth-budget 3 `
  --route-agent codex
```

The command template is executed at the start of each auto-routed subchain.
Available variables are `{cwd}`, `{subchain}`, `{goal}`, `{prompt}`,
`{prompt_file}`, and `{round}`. Prefer `{prompt_file}` for Codex or other agent
CLIs because deep-loop prompts are multiline.

The built-in `--route-agent codex` executor auto-discovers the user-level
Codex CLI, then runs the generated prompt through `codex exec -` with
`--cd "{cwd}"`, `--sandbox workspace-write`, and `--ask-for-approval never`.
It passes `--skip-git-repo-check` by default so non-Git research folders can
run; add `--route-codex-require-git` when you want Codex's Git-root guard.
Override discovery with `--route-codex-path` or `RESEARCH_LOOP_CODEX_CLI`.

## Notes

This repository stores the plugin source only. Runtime project ledgers, smoke
test outputs, scratch labs, and local caches are intentionally ignored.
