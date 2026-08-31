# Codex Research Loop

Codex Research Loop is a personal Codex plugin for reusable, project-local
scientific workflow orchestration.

It provides:

- Project-local research state under `.research-loop/`.
- Natural-language prompt normalization and multi-path task routing.
- `prompt-architect` Head Agent that turns rough requests such as "deep
  analysis" or "unattended" into chain-forcing prompts for deep-loop,
  mathematical abstraction, divergent hypotheses, adversarial review, P10
  escalation readiness, and watchdog continuation.
- Stable hard-problem shortcut: `开始困难问题推进` expands into unattended
  low-sample sampling-strategy advancement with deep analysis, expert/P10
  escalation readiness, math abstraction, harness registration, and
  experiment-runner validation.
- One-shot `autopilot` that turns a rough goal into a P1-P10 execution chain,
  primes control-plane records, and can start watchdog-supervised unattended
  execution without repeated confirmation.
- Adaptive research storage policies for existing and new projects.
- Content ingest for articles, local files, and standardized data packages.
- Source lookup, Zotero/BibTeX/CSL-JSON export, and llm-wiki handoff support.
- Claim-evidence structural verification.
- P1-P10 subchain head agents with chain-specific missions, tool policies,
  gate vectors, and handoff contracts.
- Deep-loop gate decisions for `route_next`, `retry_same_route`,
  `escalate_problem_loop`, and `pause_for_human`.
- Default Research Council and Adversarial Gate review inside `deep-loop`, with
  rich expert cards, killer tests, and an arbiter that converts critique back
  into the same four unattended-safe control decisions.
- OPHIS-style mechanistic research memory: observations, phenomena,
  falsifiable hypotheses, interventions, effect gates, mechanism candidates,
  and negative results.
- Advanced research nodes for stronger gates: reusable harness registries,
  ranked hypothesis portfolios, scratch-only evaluator-backed code-builder
  plans, math abstraction chains, and monitored experiment-runner reports.
- Isolated problem-loop diagnosis with generated expert panels and gated
  promotion before core project edits.
- Watchdog-supervised unattended validation/test/repair cycles connected to
  deep-loop dispatch, with legacy `auto-loop` kept as the child runner.
- Optional fail-open external supervisor review for watchdog decisions.
- Auto-routed subchain startup through configurable agent command templates.
- MCP tools and a Codex skill entrypoint.

## Layout

- `.codex-plugin/plugin.json` - Codex plugin manifest.
- `.mcp.json` - MCP server registration.
- `scripts/research_loop.py` - dependency-free CLI runtime.
- `scripts/mcp_server.py` - stdio MCP wrapper around the CLI.
- `skills/research-loop/SKILL.md` - Codex skill instructions.
- `templates/` - JSON/Markdown schemas used by the runtime.
- `portable/` - transferable Codex skills, dispatch plugin, dispatch table,
  hook scripts, installer, and portable-package manifests.

## Installation And API Pairing

After installing or cloning the plugin, pair an external DeepSeek API key only
when you want the optional supervisor layer:

```powershell
$env:DEEPSEEK_API_KEY = "<your DeepSeek API key>"
```

Persist it with your normal shell, OS secret manager, or Codex environment
setup. Do not write keys into this repository, command history snippets,
reports, prompts, or Git-tracked files.

The external supervisor is a supplemental layer. If `DEEPSEEK_API_KEY` is not
set, `--external-supervisor deepseek` records a skipped supervisor review and
falls back to the original local watchdog/deep-loop behavior. The core research
loop, routing, validation, and unattended resume flow still work without the
external API; only the external review layer has no effect.

On Windows, the runtime also checks the current user's persisted environment
variable when the current process has not inherited `DEEPSEEK_API_KEY`, which
helps a newly paired key work inside an already-running Codex desktop session.

## Portable Codex Skill And Plugin Library

This repository also carries a portable package for recreating the source
machine's Codex capability library on a fresh Windows computer:

```powershell
git clone https://github.com/sum331/codex-research-loop.git
cd codex-research-loop
powershell -ExecutionPolicy Bypass -File .\portable\scripts\install-codex-portable.ps1
```

The portable installer copies local skills, the prompt-submit dispatch plugin,
the dispatch table, and reusable lifecycle hook scripts into `%CODEX_HOME%`
when set, otherwise `%USERPROFILE%\.codex`. It rewrites `hooks.json` with the
new computer's paths and backs up the previous hooks file before changing it.
It also sets the user-level `CODEX_RESEARCH_LOOP_HOME` environment variable to
the cloned repository path, so installed skills can invoke
`scripts/research_loop.py` without hard-coded machine paths. Restart Codex after
the first install if the current session does not see the new environment
variable.
It also reads `portable/manifests/plugin-install-channels.json` to configure
local plugin marketplace entries, attempt managed plugin installs through
`codex plugin add`, and enable bundled/runtime plugins in `config.toml`.

Managed Codex plugin caches, appserver caches, runtime logs, orphan workspaces,
databases, Git metadata, and API keys are intentionally excluded from the
package. Reinstall official plugins/connectors through Codex on the new
computer; see `portable/manifests/local-plugin-inventory.json` for the local
cache inventory that was present on the source machine. The installer is
fail-open: if a managed channel is unavailable, local skills/hooks and runtime
configuration still complete.

## Quick Smoke Test

```powershell
python scripts/research_loop.py --cwd "D:\Loop\scratch\research-loop-smoke" auto-loop-watchdog --goal "smoke test" --skip-validate --skip-deep-loop --test-command "cmd /c exit /b 0" --format json
python scripts/research_loop.py --cwd "D:\Loop\scratch\prompt-architect-smoke" prompt-architect --input "Deep analysis with mathematical modeling, divergent hypotheses, adversarial review, and unattended continuation" --write --format json
python scripts/research_loop.py --cwd "D:\Loop\scratch\hard-problem-smoke" prompt-architect --input "开始困难问题推进" --write --format json
python scripts/research_loop.py --cwd "D:\Loop\scratch\autopilot-smoke" autopilot --goal "Complete this research task end-to-end and produce the final report" --prime --write --format json
python scripts/research_loop.py --cwd "D:\Loop\scratch\hard-problem-autopilot" autopilot --goal "开始困难问题推进" --prime --write --format json
```

## Prompt Architect Head Agent

Use `prompt-architect` as the first entry component when a user gives a vague
or overloaded request. It reads the project state, classifies the task, and
writes a chain-forcing prompt contract under `.research-loop/prompt-architect/`.

When the input says "deep analysis", it forces the strongest analysis route:
`P3` hypothesis portfolio, `P4/P6` math abstraction, `P8` Research Council and
Adversarial Gate, and `P10` problem-loop readiness. When the input says
"unattended", it adds autopilot/watchdog continuation rules and the human pause
boundary.

When the input is exactly or includes `开始困难问题推进`, the Prompt Architect
treats it as a stable preset for the user's recurring difficult-research task:
continue a matched-precision, lower-sample-count sampling scheme; run
unattended; force deep analysis, divergent hypotheses, adversarial review,
Research Council, Arbiter, P10/problem-loop readiness, math abstraction, harness
registration, and experiment-runner validation; and do not ask for manual
continuation while an executable next action exists.

```powershell
python scripts/research_loop.py --cwd "D:\Project" prompt-architect `
  --input "Deep analysis: build a full problem frame, mathematical model, adversarial critique, divergent hypotheses, and solution plan" `
  --write `
  --format json

python scripts/research_loop.py --cwd "D:\Project" prompt-architect `
  --input "Run unattended until the project is complete; do not ask me to continue while a next action exists" `
  --write `
  --format markdown

python scripts/research_loop.py --cwd "D:\Project" prompt-architect `
  --input "开始困难问题推进" `
  --write `
  --format json
```

## One-Shot Autopilot

Use `autopilot` when the user gives a broad or incomplete goal and expects a
usable result instead of repeated clarification. It normalizes the request,
builds a routed P1-P10 chain, emits concrete trigger actions, and can prime
default harnesses, hypothesis portfolios, code-builder plans, math abstractions,
and experiment-runner reports before unattended execution starts.

```powershell
python scripts/research_loop.py --cwd "D:\Project" autopilot `
  --goal "Complete this research question and produce a reliable final report" `
  --prime `
  --write `
  --format json

python scripts/research_loop.py --cwd "D:\Project" autopilot `
  --goal "Repair the analysis code, validate the math, and write the final report" `
  --test-command "python -m pytest -q" `
  --prime `
  --start-watchdog `
  --external-supervisor none `
  --format json

python scripts/research_loop.py --cwd "D:\Project" autopilot `
  --goal "开始困难问题推进" `
  --prime `
  --start-watchdog `
  --external-supervisor none `
  --format json
```

The generated plan records a `watchdog_command`, a chain sequence, and
auto-start actions. Human confirmation is reserved for credentials, restricted
data, payment, explicit approval boundaries, or irreversible external
publication.

## OPHIS Mechanistic Layer

The mechanism layer is a cross-cutting control plane for deep scientific
judgment. It follows the OPHIS pattern:

```text
Observation -> Problem -> Hypothesis -> Intervention -> Speed-up
```

In this plugin, that becomes durable project-local records:

- `observe`: writes observations from metrics, logs, artifacts, reviews, data,
  or failures.
- `hypothesis`: writes falsifiable mechanism hypotheses with predictions and
  falsifiers.
- `intervention`: writes minimal interventions with expected effect,
  validation, rollback, and unattended-safety flags.
- `ophi-cycle`: writes a full observation, phenomenon, hypothesis,
  intervention, pending effect gate, and mechanism candidate.
- `mechanism`: writes reusable mechanisms and negative results.

Example:

```powershell
python scripts/research_loop.py --cwd "D:\Project" ophi-cycle `
  --observation "analysis passes smoke data but fails held-out reports" `
  --problem "promotion gate may be insensitive to variance" `
  --hypothesis "the current gate overweights artifact readiness and underweights uncertainty" `
  --intervention "add a variance-sensitive harness check before P7 promotion" `
  --expected-effect "unstable outputs retry P6 instead of advancing to writing" `
  --validation "replay two harness reports and compare route decisions" `
  --subchain P6 `
  --write `
  --format json
```

Records are stored under `.research-loop/observations/`,
`.research-loop/phenomena/`, `.research-loop/hypotheses/`,
`.research-loop/interventions/`, `.research-loop/effect-gates/`, and
`.research-loop/mechanisms/`. They guide deep-loop, problem-loop, expert
review, and future routing; they do not mutate core project files directly.

`deep-loop` consumes this mechanism memory on every gate:

- Pending effect gates raise uncertainty and failure-mode risk. A passing hard
  gate is converted to `retry_same_route` with semantic reason
  `mechanism_validation_pending` until the effect gate has a validation
  outcome.
- Supported mechanisms are inserted into the `continuation_contract`,
  `required_reads`, and next-work prompt as `Mechanism Memory To Reuse`.
- Rejected mechanisms and negative results are surfaced as failure-mode
  warnings so a later subchain does not repeat a failed intervention.
- Research Council adds `mechanism_memory_auditor` whenever mechanism memory is
  relevant, and Adversarial Gate adds killer tests for pending effect gates.

## Advanced Research Nodes

Use these commands when a project needs deeper analysis, better divergence,
more stable code construction, or mathematical abstraction before a gate can
pass:

```powershell
python scripts/research_loop.py --cwd "D:\Project" harness-registry `
  --name "analysis harness" `
  --subchain P6 `
  --command "python -m pytest tests/test_analysis.py" `
  --metric weighted_score `
  --failure-tag analysis `
  --promotion-threshold 0.85 `
  --write

python scripts/research_loop.py --cwd "D:\Project" hypothesis-portfolio `
  --problem "analysis passes smoke tests but fails robustness review" `
  --subchain P6 `
  --write

python scripts/research_loop.py --cwd "D:\Project" code-builder `
  --goal "repair the failing parser" `
  --subchain P5 `
  --harness-id harness-id `
  --candidate "minimal regression-tested patch" `
  --write

python scripts/research_loop.py --cwd "D:\Project" math-abstraction `
  --problem "prove the reported metric is invariant under target normalization" `
  --subchain P6 `
  --definition "metric m is computed after normalization n" `
  --assumption "n is monotone" `
  --write

python scripts/research_loop.py --cwd "D:\Project" experiment-runner `
  --name "analysis smoke" `
  --subchain P6 `
  --command "python -m pytest tests/test_analysis.py -q" `
  --retry 1 `
  --execute `
  --write `
  --format json
```

Records are stored under `.research-loop/harnesses/`,
`.research-loop/hypothesis-portfolios/`, `.research-loop/code-builders/`, and
`.research-loop/math-abstractions/`; experiment reports are stored under
`.research-loop/experiment-runs/`. `deep-loop` reads them automatically and adds
corresponding dynamic experts, gate-vector signals, adversarial killer tests,
and continuation prompt sections. These nodes are control-plane records: they
do not mutate core project files.

## Research Council And Adversarial Gate

`deep-loop` now runs three review layers by default:

- The hard gate preserves non-negotiable constraints such as human authority,
  explicit blockers, low quality scores, and retry-budget exhaustion.
- The Research Council constructs fixed and dynamic expert cards with
  `required_reads`, `diagnostic_frame`, `red_flags`, and `output_contract`
  fields, then recommends whether to transition, retry, reroute, escalate, or
  pause.
- The Adversarial Gate attacks premature convergence with fatal objections,
  missing counterfactuals, and killer tests. The Arbiter combines hard gate,
  council, and adversarial findings into `route_next`, `retry_same_route`,
  `escalate_problem_loop`, or `pause_for_human`.

With `--write`, the main directive remains under `.research-loop/deep-loops/`.
Supplemental council reports are written under
`.research-loop/experts/councils/`, and adversarial reports under
`.research-loop/adversarial-gates/`. These are control-plane review artifacts;
they do not mutate project core files.

For debugging only, direct `deep-loop` calls can temporarily disable either
supplemental layer:

```powershell
python scripts/research_loop.py --cwd "D:\Project" deep-loop `
  --intent "debug a gate" `
  --current-subchain P3 `
  --skip-research-council `
  --skip-adversarial-gate
```

## Auto-Routed Agent Startup

Use `auto-loop-watchdog` for unattended work. It starts `auto-loop` as a child,
then resumes automatically whenever the child writes a report with a resumable
status or an unattended-safe continuation contract:

```powershell
python scripts/research_loop.py --cwd "D:\Project" auto-loop-watchdog `
  --goal "finish current research stage" `
  --test-command "python -m pytest" `
  --current-subchain P7 `
  --next-subchain P8 `
  --route-depth-budget 3 `
  --max-resumes 8
```

The MCP compatibility tool `research_loop_auto_loop` also maps to
`auto-loop-watchdog` by default. Set `legacy_auto_loop=true` only when a caller
intentionally needs the old bare `auto-loop` behavior.

The command template is executed at the start of each auto-routed subchain.
Available variables are `{cwd}`, `{subchain}`, `{goal}`, `{prompt}`,
`{prompt_file}`, and `{round}`. Prefer `{prompt_file}` for Codex or other agent
CLIs because deep-loop prompts are multiline.

The built-in `--route-agent codex` executor is the default. It auto-discovers
the user-level Codex CLI, then runs the generated prompt through `codex exec -`
with
`--cd "{cwd}"`, `--sandbox workspace-write`, and `--ask-for-approval never`.
It passes `--skip-git-repo-check` by default so non-Git research folders can
run; add `--route-codex-require-git` when you want Codex's Git-root guard.
Override discovery with `--route-codex-path` or `RESEARCH_LOOP_CODEX_CLI`.

Use `--no-auto-route-next` when you want a manual checkpoint after the current
subchain instead of unattended continuation. When deep-loop has a next target,
this exits as `route-next-handoff-required` rather than `passed`, so intermediate
handoffs cannot be mistaken for completed projects. Use `--route-agent none`
together with one or more `--route-agent-command` templates when another local
runner should consume the generated prompt.

If the next-subchain route agent cannot be configured, the run stops as
`route-next-executor-missing`. If the configured route agent starts but exits
non-zero, the run stops as `route-agent-failed` and records the executor command,
stdout/stderr logs, target subchain, and route handoff in the auto-loop report.
If the route agent becomes silent longer than `--route-agent-idle-timeout`, the
process tree is killed and the run stops as `route-agent-timeout`, which is
treated as resumable by `auto-loop-resume` and `auto-loop-watchdog`. Set
`--route-agent-idle-timeout 0` only for executors that are expected to be silent
for a long time and are supervised elsewhere.

The same continuation mechanism now applies to all unattended-safe gate
decisions:

- `route_next` starts the next subchain.
- `retry_same_route` starts another round inside the current subchain with the
  retry prompt generated by deep-loop.
- `escalate_problem_loop` creates the isolated problem-loop case; when that case
  exits successfully with an approved gate, auto-loop starts P10 instead of
  stopping at the problem report.

For long unattended runs where route depth should not be the stopping condition,
combine automatic routing with an explicit wall-clock or round safety limit:

```powershell
python scripts/research_loop.py --cwd "D:\Project" auto-loop-watchdog `
  --goal "complete the research project end to end" `
  --test-command "python -m pytest" `
  --current-subchain P1 `
  --allow-unbounded-routes `
  --allow-unbounded-resumes `
  --max-minutes 360
```

If a run stops because a safety budget is exhausted, a route handoff is required,
or a route executor needs to be retried, resume from the last auto-loop report:

```powershell
python scripts/research_loop.py --cwd "D:\Project" auto-loop-resume `
  --latest `
  --extra-rounds 8 `
  --extra-route-depth 4 `
  --max-minutes 180
```

`auto-loop-resume` reads the previous `*-auto-loop.json`, reconstructs the next
subchain or same-subchain retry prompt from the stored continuation contract,
starts the route agent before validation, and records the source report under
`resume` in the new auto-loop report.

For fully unattended sessions, prefer `auto-loop-watchdog`. It starts the first
`auto-loop`, reads the produced report, and automatically calls
`auto-loop-resume --latest` while the child status is resumable:

```powershell
python scripts/research_loop.py --cwd "D:\Project" auto-loop-watchdog `
  --goal "complete the research project end to end" `
  --test-command "python -m pytest" `
  --current-subchain P1 `
  --allow-unbounded-routes `
  --allow-unbounded-resumes `
  --max-minutes 360 `
  --max-resumes 6 `
  --resume-extra-rounds 8 `
  --resume-extra-route-depth 4
```

The watchdog writes `.research-loop/watchdog/active-run.json` while running and
a `*-auto-loop-watchdog.json` report when it stops. It resumes statuses such as
`route-depth-budget-exhausted`, `route-agent-failed`, `route-agent-timeout`,
`round-limit`, `timeout`, route handoff states, and any report containing an
unattended-safe continuation contract. Use `--allow-unbounded-resumes` when
resume count should not be the stopping condition. If the child process itself
hangs before it can write a report, `--child-idle-timeout` and
`--child-wall-timeout` can terminate it and leave a watchdog failure report.

### External Supervisor

`auto-loop-watchdog` can add a fail-open DeepSeek supervisor layer that reviews
each child report before the watchdog decides whether to resume:

```powershell
$env:DEEPSEEK_API_KEY = "<set outside the repo>"
python scripts/research_loop.py --cwd "D:\Project" auto-loop-watchdog `
  --goal "complete the research project end to end" `
  --test-command "python -m pytest" `
  --current-subchain P1 `
  --allow-unbounded-routes `
  --allow-unbounded-resumes `
  --max-minutes 360 `
  --external-supervisor deepseek `
  --external-supervisor-model deepseek-v4-flash
```

The supervisor is advisory and read-only. It receives a compact child-report
excerpt and returns JSON with a recommendation, risk flags, and optional prompt
patch text. It never writes project files and never replaces the local gate. If
the API key is missing, the API times out, returns invalid JSON, or is otherwise
unavailable, watchdog records the supervisor status as `skipped` or `failed`
under `.research-loop/supervisor/` and continues with the original local
decision. Do not put API keys in commands, reports, docs, or Git; use the
`DEEPSEEK_API_KEY` environment variable only.

## Subchain Head Agents

Every P1-P10 subchain is fronted by a head agent. The head agent reads the
project state, defines the chain-specific work contract, selects allowed tools,
and evaluates a multi-dimensional gate vector before handing off. Deep-loop
reports now include:

- `subchain_agent`: the active head agent id and contract.
- `gate_vector`: objective gap, evidence integrity, artifact readiness, method
  validity, analysis validity, novelty risk, uncertainty, failure-mode risk,
  handoff completeness, and human blocker signals.
- `continuation_contract`: the next target subchain, next agent, required
  reads, artifact refs, blocking dimensions, and unattended safety flags.

High-risk late-stage work in P6-P9 can escalate to P10 before repeated failures
when the gate vector shows missing artifacts, analysis validity risk, evidence
breaks, or unresolved uncertainty.

The next work prompt consumed by `auto-loop` embeds the target Head Agent
contract directly, so a routed Codex CLI or custom route executor receives the
mission, required reads, tool policy, required outputs, quality vector, failure
policy, and handoff contract before starting the next subchain.

## Notes

This repository stores the plugin source only. Runtime project ledgers, smoke
test outputs, scratch labs, and local caches are intentionally ignored.
