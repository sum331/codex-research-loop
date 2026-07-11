---
name: research-loop
description: >
  Use a project-local research loop for Codex work: initialize .research-loop,
  record materials, claims, evidence, decisions, risks, next actions,
  checkpoints, handoffs, run logs, source metadata, Zotero/wiki bridge exports,
  and unattended test feedback loops. Trigger on research loop, loop,
  checkpoint, handoff, resume, project state, material passport, evidence
  ledger, decision log, experiment run log, rough natural-language research
  input needing normalization, Crossref/OpenAlex/arXiv lookup, content ingest
  from URLs or local files, adaptive project storage policies, standardized
  data packages, Zotero
  BibTeX/CSL-JSON/PDF attachment/dedupe exports, llm-wiki-compatible pages,
  claim-evidence verification, isolated problem diagnosis, expert-panel
  evaluation, gated adjustment promotion, deep-loop gate/review/tree routing,
  auto-loop test repair, fail-open external supervisor review, or multi-path
  routing to academic, Nature-style, PDF, Word, presentation, and research
  production skills.
---

# Research Loop

Use this skill when a research project needs durable state across Codex threads.
The loop stores local artifacts under `.research-loop/` in the active project.

## Purpose

The research loop is a coordination and audit layer. It does not replace domain
skills such as `academic-research-suite`, `nature-writing`, `nature-figure`,
`pdf`, `word`, or `presentations`. Use those skills for substantive research,
writing, review, figures, and document production. Use this skill to preserve
state, evidence, runs, decisions, checkpoints, and handoffs.

## Harness Discipline

Generalize the durable harness discipline from `z2-harness-loop` for every
research-loop task:

1. Scope the objective, files, metrics, deliverable, and stop condition.
2. Map current project state and relevant artifacts before acting.
3. Choose a validation surface before editing or running anything substantive.
4. Build the smallest coherent increment.
5. Test through the chosen harness.
6. Read back outputs, reports, logs, renders, or diffs directly.
7. Loop until the gate passes, a retry limit is reached, or a real blocker is
   recorded.
8. Report artifacts, validation evidence, remaining risks, and the next target.

Use `normalize` or `route` to classify the execution profile before starting
work. The generated `harness_protocol` distinguishes standard loops,
manuscript/artifact loops, and research experiment loops.

Typical validation surfaces include route plans, structural `validate`,
claim-evidence checks, formula/citation/layout audits, document/PDF render
inspection, metric recomputation, wrapped run logs, small representative
shards, and artifact diffs. Always inspect the resulting artifacts or logs
before claiming completion.

Do not absorb the z2 harness as a whole runner. Its project-specific candidate
selection is intentionally lightweight and weaker than this plugin's
`auto-loop`, `deep-loop`, and `problem-loop`. Instead, split its useful pieces
across the existing workflow:

- `normalize` / `route`: choose the validation surface and, when useful, define
  a case contract with id, target/input, expected gate, grader, tags, weight,
  and timeout/budget.
- `run` / `auto-loop`: execute the checks and capture logs, artifacts, stdout,
  stderr, and exit status.
- `deep-loop`: consume pass/fail, weighted score, failure tags, report paths,
  and artifact refs as gate evidence.
- `problem-loop`: use failed tags and logs to construct the expert panel and
  isolated lab plan.
- `handoff`: preserve report paths, failed tags, and next validation target for
  the next subchain.

Structured JSON harness reports can be passed to deep-loop with
`--harness-report`. The adapter accepts direct `summary` payloads, z2-style
`evaluations` reports, and auto-loop-style `rounds/tests/executors` reports. It
extracts `pass_rate`, `weighted_score`, `failures_by_tag`, failed cases,
runtime/latency, and report paths. With `--gate-result auto`, failed harness
evidence becomes a retry/problem signal; passing evidence can route to the next
subchain.

When MCP tools from this plugin are available, prefer them for routine state
operations instead of shelling out manually. Pass the active project directory
as `cwd` for every tool call. Available tool names mirror the CLI surface:
`research_loop_status`, `research_loop_route`, `research_loop_passport`,
`research_loop_profile`, `research_loop_question`, `research_loop_material`,
`research_loop_claim`, `research_loop_evidence`, `research_loop_decision`,
`research_loop_risk`, `research_loop_next`, `research_loop_update`,
`research_loop_capabilities`, `research_loop_normalize`,
`research_storage_policy`, `research_loop_deep_loop`,
`research_source_hub`, `research_content_ingest`, `research_zotero_bridge`,
`research_problem_loop`, `research_problem_promote`,
`research_loop_auto_loop`, `research_loop_auto_loop_watchdog`,
`research_claim_evidence_verify`,
`research_loop_checkpoint`,
`research_loop_handoff`, `research_loop_resume`, `research_loop_validate`, and
`research_loop_run`.

## Core Commands

The portable installer sets `CODEX_RESEARCH_LOOP_HOME` to the cloned plugin
root. If you are running from a manual clone before installing, set it first:

```powershell
$env:CODEX_RESEARCH_LOOP_HOME = (Get-Location).Path
```

Then call the runtime through that variable:

```powershell
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" init
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" status
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" storage
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" storage --init-dirs --write
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" resume
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" normalize --input "rough user request"
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" route --intent "write the paper"
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" route --intent "write the paper" --format json
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" deep-loop --intent "write the paper" --current-subchain P7 --gate-result pass --write
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" deep-loop --intent "verify evidence" --current-subchain P3 --gate-result fail --gate-issue "unsupported claim remains" --write
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" deep-loop --intent "verify harness report" --current-subchain P6 --gate-result auto --harness-report "reports\harness.json" --write
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" capabilities
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" source-hub --query "10.1038/s41586-020-2649-2" --provider auto
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" content-ingest --source "paper.html" --mode article --record-materials --write
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" content-ingest --source "data.csv" --mode data --record-materials --write
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" problem-loop --problem "tests fail after data ingest" --test-command "python -m pytest -q" --write
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" problem-promote --case-id "prob-case-id"
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" zotero-bridge --collection "Project Literature" --format all --write
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" zotero-bridge --collection "Project Literature" --wiki-root "D:\path\to\wiki" --write-wiki --write
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" claim-evidence --format json --write
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" profile --target-venue "Nature" --citation-style "Nature" --verification-strictness strict
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" checkpoint --stage SCOPING --note "Research question narrowed."
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" handoff --note "Ready for literature review."
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" run -- python -m pytest -q
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" auto-loop-watchdog --goal "tests pass" --test-command "python -m pytest -q" --max-rounds 5
```

Install lifecycle hooks once:

```powershell
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\install_hooks.py"
```

## Project Artifacts

The project-local directory is:

```text
.research-loop/
  state.json
  material-passport.json
  evidence-ledger.jsonl
  decision-log.jsonl
  artifact-registry.jsonl
  lifecycle-events.jsonl
  storage-policy.json
  runs/
  checkpoints/
  handoffs/
  ingest/
  deep-loops/
  problem-cases/
  problem-reports/
  promotions/
  reports/
  storage-reports/
```

Read `material-passport.json`, `state.json`, and the latest handoff before
resuming work in a new thread.

`.research-loop/` is the control plane. Project-facing research materials are
placed according to `.research-loop/storage-policy.json`, not hard-coded into
the control directory.

## Storage Policy

Use `storage` before ingesting materials into a new or unfamiliar project:

```powershell
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" storage
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" storage --style adaptive --init-dirs --write
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" storage --style canonical --rebuild --init-dirs
```

Storage styles:

- `adaptive`: detect existing directories such as `data/`, `datasets/`,
  `papers/`, `references/`, `figures/`, `artifacts/figures/`, `manuscript/`,
  or `public_release/`, then map buckets without moving files.
- `canonical`: initialize a clean research layout with `sources/`,
  `sources/articles/`, `data/raw/`, `data/external/`, `data/interim/`,
  `data/processed/`, `data/packages/`, `scripts/`, `notebooks/`,
  `analysis/`, `outputs/figures/`, `outputs/tables/`, `manuscripts/`,
  `reports/`, `releases/`, and `scratch/`.
- `minimal`: use a compact subset suitable for lightweight projects.
- `loop-local`: keep generated material packages under `.research-loop/` for
  backward-compatible or disposable workflows.

The policy is stored as `.research-loop/storage-policy.json`. It records bucket
ids, project-relative paths, absolute paths, purpose, creation behavior, and git
policy. `storage --init-dirs` creates directories; it does not migrate or delete
existing files.

## Research Records

Use these commands to keep the project state machine grounded in auditable
records:

```powershell
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" passport --title "Project title" --domain "field" --question "Main research question" --target paper
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" material --kind paper --title "Source title" --source "doi-or-url" --status external
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" claim --text "Key claim" --status proposed
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" evidence --kind citation --source "doi-or-url" --claim-id claim-id --status verified
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" decision --decision "Use method X" --rationale "Why X is appropriate"
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" risk --text "Citation support is incomplete" --severity high
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" next --text "Verify the remaining sources" --stage LITERATURE
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" update --kind risk --id risk-id --status mitigated --note "Verified by source audit"
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" update --kind next --id next-id --status done
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" update --kind evidence --id evidence-id --status verified
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" validate
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" claim-evidence --fail-on-issue
```

Record IDs printed by `claim`, `evidence`, `material`, and `decision` should be
used when connecting evidence to claims. Do not invent IDs.

## Prompt Normalization

When a user gives rough, incomplete, or low-structure natural language, run
`normalize` before choosing a domain workflow:

```powershell
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" normalize --input "current user request"
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" normalize --input "current user request" --format json
```

`normalize` reads the current project state and passport, classifies the task,
assigns chain depth, reports missing slots, and emits a downstream prompt that
future Codex threads can use directly. Use it when the user's request is
ambiguous, skips project context, mixes several tasks, or assumes unstated
materials. `route` also embeds the normalized prompt in its output.

## Content Ingest

Use `content-ingest` for explicit URLs or local files that need to enter the
research loop as reusable materials:

```powershell
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" content-ingest --source "https://example.org/paper.html" --mode auto --record-materials --write
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" content-ingest --source "paper.pdf" --mode article --record-materials --write
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" content-ingest --source "data.csv" --mode data --record-materials --write --wiki-root "D:\path\to\wiki" --write-wiki
```

Article-like inputs are routed to `article-processing-chain`, stored in the
`articles` bucket from `.research-loop/storage-policy.json` (canonical default:
`sources/articles/`), converted to `content.md` when lightweight text extraction
is possible, and recorded as `article` materials. PDF articles keep the raw file
and should then be processed with `pdf`, `nature-reader`, or the project's
dedicated article-processing chain for layout-aware extraction.

Data-like inputs are routed to `standard-data-package` and stored under
the `data_packages` bucket from `.research-loop/storage-policy.json`
(canonical default: `data/packages/<package>/`) with this contract:

```text
raw/
metadata.json
schema.json
README.md
```

`metadata.json` stores provenance, source, byte count, hash, family, route
target, storage policy, and storage bucket. `schema.json` stores lightweight
inferred columns and samples for CSV, TSV, and JSON where possible. `README.md`
documents the storage contract so downstream analysis uses the package instead
of temporary ad hoc paths. Imported data is recorded as `dataset` materials when
`--record-materials` is set.

This command deliberately crawls only explicit sources supplied by the user. It
does not recursively spider websites by default. Use `--max-bytes` to bound
large downloads, and write llm-wiki-compatible source pages only when a
`--wiki-root` is supplied. Run `storage --init-dirs` first when starting an
independent new project that should follow the canonical outer layout.

## Problem Loop

Use `problem-loop` when an existing project has failures, blockers, unclear
root causes, or a self-started project is stalled before touching core project
files:

```powershell
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" problem-loop --problem "project tests fail after data ingest" --test-command "python -m pytest -q" --write
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" problem-promote --case-id "problem-case-id"
```

The chain reads project context, route graph, storage policy, passport summary,
manifest snippets, and top-level repository structure. It then constructs a
multi-expert panel from fixed workflow roles plus on-demand experts inferred
from the actual problem signal, writes expert prompts, captures supplied test
commands, drafts an adjustment plan, and evaluates a promotion gate.

All analysis, test logs, candidate notes, and adjustment files stay outside the
core chain in the storage policy scratch bucket, canonically
`scratch/research-loop-labs/<case-id>/`. The control plane only records the case
under `.research-loop/problem-cases/` and optional reports under
`.research-loop/problem-reports/`.

Do not edit core project files from a problem case until `problem-promote`
records an approved gate, promotion decision, and next action. If the gate is
`hold` or `analysis_only`, continue diagnosis inside the lab or record an
explicit forced promotion rationale before making traceable core edits.

## Research Source Hub

Use `source-hub` for lightweight public scholarly metadata lookup before
recording sources or evidence:

```powershell
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" source-hub --query "paper title or DOI" --provider auto --rows 3
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" source-hub --query "paper title or DOI" --record-materials
```

The first implementation queries Crossref, OpenAlex, and arXiv through public
HTTP APIs and returns normalized JSON/Markdown. Treat results as metadata
candidates until a citation or source locator is independently verified. Use
`--record-materials` only when the returned items are relevant enough to store
as `source-metadata` materials.

## Zotero Bridge

Use `zotero-bridge` after `source-hub --record-materials` or after manually
recording paper/reference materials:

```powershell
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" zotero-bridge --collection "Project Literature" --format plan
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" zotero-bridge --collection "Project Literature" --format csl-json --write
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" zotero-bridge --collection "Project Literature" --format bibtex --write
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" zotero-bridge --collection "Project Literature" --format all --include-attachments --write
```

The first implementation is an offline bridge. It reads recorded
`source-metadata`, `paper`, `article`, `reference`, `citation`, and PDF-like
materials from `.research-loop/material-passport.json`, deduplicates them by DOI
or title, and writes Zotero-compatible artifacts under `.research-loop/zotero/`:
collection plan JSON, CSL-JSON, BibTeX, attachment plan, dedupe report, and a
markdown report. It deliberately does not write directly to Zotero SQLite.
Direct Zotero Web API writes require explicit library id, write-capable API key,
and the attachment upload handshake.

For knowledge-base integration with the existing `llm-wiki` skill, write
wiki-compatible pages:

```powershell
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" zotero-bridge --collection "Project Literature" --wiki-root "D:\path\to\wiki" --write-wiki --write
```

This creates markdown pages in `sources/` and a `topics/zotero-paper-library.md`
hub using `[[links]]`, so the wiki graph can index the papers after the normal
llm-wiki graph rebuild. Treat these pages as materialized source pages, not as a
replacement for llm-wiki ingestion adapters.

## Claim Evidence Verifier

Use `claim-evidence` before drafting, review, revision, and finalization:

```powershell
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" claim-evidence
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" claim-evidence --format json --write
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" claim-evidence --fail-on-issue
```

The verifier is a deterministic structure gate. It checks active claims in
`.research-loop/material-passport.json` against evidence records in
`.research-loop/evidence-ledger.jsonl` and reports whether each claim has
evidence ids, whether each evidence id exists, and whether each evidence record
has source, locator, and status. Verdicts are `verified`, `partial`,
`unsupported`, or `failed`.

It does not prove that a cited passage semantically supports a claim. For
semantic support, page-level locator extraction and source reading must happen
through `pdf`, `nature-reader`, `nature-academic-search`, or a future semantic
claim verifier. `validate --fail-on-issue` runs this structural verifier by
default so `auto-loop` can catch broken evidence chains.

## Unattended Auto Loop

Use `auto-loop-watchdog` when a test or validation gate should automatically
trigger the next round instead of stopping after the first failure. The legacy
`research_loop_auto_loop` MCP tool also maps to watchdog by default; set
`legacy_auto_loop=true` only for the old bare child-runner behavior.

```powershell
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" auto-loop-watchdog --goal "project tests pass" --test-command "python -m pytest -q" --max-rounds 5
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" auto-loop-watchdog --goal "lint and tests pass" --test-command "python -m pytest -q" --test-command "python -m ruff check ." --repair-command "python scripts/repair.py" --max-rounds 8
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" auto-loop-watchdog --goal "data pipeline is reproducible" --current-subchain P5 --test-command "python -m pytest tests/data -q" --repair-command "python scripts/repair_data_pipeline.py" --max-rounds 5
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" auto-loop-watchdog --goal "finish current research stage" --current-subchain P7 --next-subchain P8 --route-depth-budget 3 --test-command "python -m pytest -q" --max-rounds 8 --max-resumes 8
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" auto-loop-watchdog --goal "complete the research project end to end" --current-subchain P1 --test-command "python -m pytest -q" --allow-unbounded-routes --allow-unbounded-resumes --max-minutes 360
```

Each round runs `validate --fail-on-issue` unless `--skip-validate` is set, then
runs every `--test-command`. By default, every round also writes a `deep-loop`
gate under `.research-loop/deep-loops/` and acts on its decision:

- `route_next`: by default, consume the generated prompt, start the next
  subchain inside the same run through the configured route agent, and execute
  each `--route-agent-command` before running validation/tests for that
  subchain. Use `--no-auto-route-next` only when a manual checkpoint is
  required after writing the handoff; when a next target exists this reports
  `route-next-handoff-required`, not `passed`.
- `retry_same_route`: run any `--repair-command`, then consume the generated
  retry prompt through the route agent and start the next round inside the same
  subchain. With automatic continuation disabled, stop as
  `retry-same-route-handoff-required`.
- `escalate_problem_loop`: automatically create an isolated `problem-loop` case
  unless `--skip-problem-escalation` is set. When the case exits successfully
  with an approved gate, consume the generated P10 prompt and continue into the
  problem-resolution chain as `problem-loop-auto-started`.
- `pause_for_human`: stop unattended execution and leave a blocked next action.

Use `--current-subchain P1..P10` when the caller knows which chain is being
tested, and repeat `--next-subchain` to force the next route after a passing
gate. Use `--skip-deep-loop` only for legacy one-level retry behavior. Defaults
are bounded by `--max-rounds` and `--route-depth-budget`; the deep-loop retry
budget can be overridden with `--deep-loop-max-rounds`. For long unattended
runs, pair `--allow-unbounded-routes` with an explicit wall-clock or round
safety limit.

The default `--route-agent codex` executor auto-discovers the user-level Codex
CLI, passes the generated deep-loop prompt through stdin to `codex exec -`, and
runs with `--cd`, `--sandbox workspace-write`, and `--ask-for-approval never`
unless overridden. It also passes
`--skip-git-repo-check` by default so non-Git research folders can run; add
`--route-codex-require-git` for Git-root enforcement. Use `--route-codex-path`
or `RESEARCH_LOOP_CODEX_CLI` when auto-discovery finds the wrong executable.

Custom agent command templates receive `{cwd}`, `{subchain}`, `{goal}`,
`{prompt}`, `{prompt_file}`, and `{round}`. Prefer `{prompt_file}` for CLIs
because deep-loop prompts are multiline. If automatic route consumption is
enabled and neither the default Codex executor nor `--route-agent-command` can
run, the loop stops with `route-next-executor-missing` rather than pretending
the next subchain ran. If a configured route agent starts but exits non-zero,
the loop stops with `route-agent-failed` and records the executor logs and
target subchain in the auto-loop report before any downstream validation gates
run. If the route agent becomes silent longer than
`--route-agent-idle-timeout`, auto-loop kills the process tree and reports
`route-agent-timeout`; this is a resumable state, not a terminal project
failure. Use `--route-agent-idle-timeout 0` only for executors that can be
silent for a long time and are supervised outside this loop.

When an unattended run stops for a resumable control reason, resume it instead
of asking the user for the next manual command:

```powershell
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" auto-loop-resume --latest --extra-rounds 8 --extra-route-depth 4 --max-minutes 180
```

Use `auto-loop-resume` for `route-depth-budget-exhausted`, `round-limit`,
`timeout`, `route-next-handoff-required`,
`retry-same-route-handoff-required`, `route-agent-failed`,
`route-agent-timeout`, and compatible approved problem-loop handoffs. The resume
command reads the previous
`*-auto-loop.json`, reconstructs the next prompt from the continuation contract
or last auto-route record, starts the route agent first, then runs validation and
deep-loop gates again.

For long unattended work, use `auto-loop-watchdog` over a bare `auto-loop`.
The watchdog starts `auto-loop`, reads the child report, and automatically runs
`auto-loop-resume --latest` while the child status is resumable or the child
report contains an unattended-safe continuation contract. It records live state
in `.research-loop/watchdog/active-run.json` and writes a
`*-auto-loop-watchdog.json` report. Use `--allow-unbounded-resumes` when resume
count should not be the stopping condition; otherwise use `--max-resumes`,
`--resume-extra-rounds`, and `--resume-extra-route-depth` to control depth. Use
`--child-idle-timeout` or `--child-wall-timeout` when the parent auto-loop
process itself must be killed if it hangs before writing a report.

For stronger long-run review, add `--external-supervisor deepseek` to
`auto-loop-watchdog`. This is a fail-open, read-only compatibility layer: it
reviews the compact child auto-loop report, writes supervisor reports under
`.research-loop/supervisor/`, and preserves the local watchdog decision if the
API key is missing, the API times out, or the response is invalid. Read the
credential from `DEEPSEEK_API_KEY` only; never place API keys in prompts,
commands, reports, docs, or repository files.

## Routing Protocol

Before starting substantive research, writing, review, figure, conversion, or
revision work, run:

```powershell
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" route --intent "current user task"
```

`route` now emits a multi-path task graph rather than a single linear next step.
It classifies the task, assigns a chain depth, selects one or more P1-P10
subchains, lists shared dispatcher nodes, maps available skills/apps, and names
missing tools that should be added later. Use `--format json` when another tool
needs the structured graph.

Use the route plan to choose the next domain skill:

- `INTAKE` / `SCOPING`: route to `academic-research-suite` deep-research
  `socratic`; use `nature-academic-search` once search terms are specific.
- `LITERATURE`: route to `academic-research-suite` deep-research `lit-review`,
  `nature-academic-search`, and `pdf` for local papers.
- `DESIGN`: route to `academic-research-suite` experiment-agent and
  `nature-data`.
- `EXECUTION`: wrap commands with `research-loop run`; use
  `academic-research-suite` experiment-agent for experiment interpretation.
- `ANALYSIS`: route to experiment-agent, `nature-figure`, and `spreadsheets`
  as appropriate.
- `SYNTHESIS` / `WRITING`: route to `academic-research-suite` academic-paper,
  `nature-writing`, `nature-citation`, and `word` as needed.
- `REVIEW`: route to `academic-research-suite` academic-paper-reviewer,
  `nature-reviewer`, and `research-loop validate`.
- `REVISION_FINALIZE`: route to academic-paper revision/format-convert,
  `nature-response`, `nature-polishing`, `pdf`, `word`, and `presentations`.

## Deep Loop Protocol

Use `deep-loop` when a subchain round has produced a result and the loop needs
to decide whether to continue inside the same subchain or move to another one:

```powershell
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" deep-loop --intent "current task" --current-subchain P2 --gate-result pass --write
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" deep-loop --intent "current task" --current-subchain P3 --gate-result fail --gate-issue "claim has no verified evidence" --write
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" deep-loop --intent "current task" --current-subchain P6 --gate-result auto --quality-score 0.72 --artifact "outputs/figures/main.png" --write
python "$env:CODEX_RESEARCH_LOOP_HOME\scripts\research_loop.py" --cwd "C:\path\to\project" deep-loop --intent "current task" --current-subchain P6 --gate-result auto --harness-report "reports\harness.json" --write
```

`deep-loop` reads the current route graph, selected P1-P10 subchain, project
profile, route blockers, supplied gate issues, optional artifacts, and optional
quality score. If `--harness-report` is supplied, it also parses structured
report evidence and injects pass/fail, weighted score, failed tags, failed
cases, and report paths into the gate. It emits one of four decisions:

- `route_next`: the subchain passed; first run `review_for_transition`, then
  hand off to the next subchain.
- `retry_same_route`: the gate failed but the retry budget remains; first run
  `review_for_retry`, then repeat the same subchain with a narrower plan.
- `escalate_problem_loop`: retry budget is exhausted or the failure needs an
  isolated lab; route to `P10` / `problem-loop` before core edits.
- `pause_for_human`: restricted data, credentials, authorization, terminal
  finalization, or other owner-only decisions require a human checkpoint.

Reports are written under `.research-loop/deep-loops/`. With `--write`, the
command records a `deep_loop_gate` decision, a `deep_loop_report` artifact, and
a next action containing the generated review/handoff prompt. The command is a
dispatcher: it does not directly mutate core research files.

## Multi-Path Subchains

Use these canonical subchains when interpreting route output:

- `P1` scoping-question-chain: topic intake, RQ narrowing, scope boundaries.
- `P2` literature-evidence-chain: source discovery, article ingest, PDF ingest, metadata, evidence records.
- `P3` claim-contribution-chain: hypotheses, novelty, claim-evidence alignment.
- `P4` method-experiment-compliance-chain: protocol, study design, data/compliance planning.
- `P5` data-code-execution-chain: standardized data ingest, datasets, code, wrapped runs, failures, reproducibility.
- `P6` analysis-statistics-figure-chain: statistics, tables, figures, legends.
- `P7` writing-citation-format-chain: outline, manuscript, citations, DOCX/LaTeX/PDF.
- `P8` review-revision-integrity-chain: reviewer simulation, rebuttal, revision, integrity gates.
- `P9` submission-publication-reuse-chain: submission package, slides, patent, release, reuse.
- `P10` problem-resolution-expert-chain: blockers, failures, expert panel, isolated tests, adjustment plan, promotion gate.

Each subchain is fronted by a corresponding Head Agent. The Head Agent is the
chain owner for that round: it reads the project state and latest handoff,
applies its chain-specific mission, limits tool use to the chain's tool policy,
checks required outputs, and writes a handoff contract before another subchain
continues. Deep-loop reports expose this as `subchain_agent`.

Deep-loop gates use a `gate_vector`, not a single score. The dimensions are
`objective_gap`, `evidence_integrity`, `artifact_readiness`,
`method_validity`, `analysis_validity`, `novelty_risk`, `uncertainty_level`,
`failure_mode_risk`, `handoff_completeness`, and `human_blocker`. Treat high
late-stage risk in P6-P9 as a reason to route into P10 problem/expert review
before continuing unattended.

Every deep-loop report also includes a `continuation_contract` with the next
target subchains, next Head Agent, required reads, artifact refs, blocking
dimensions, and unattended safety flags. Auto-loop consumes this contract when
starting the next subchain.

The generated next-work prompt embeds the target Head Agent contract directly.
When auto-loop starts Codex CLI or a custom route executor, that executor should
follow the embedded mission, required reads, tool policy, required outputs,
quality vector, failure policy, and handoff contract before doing substantive
work.

Shared nodes `N0`-`N9` handle state reads, intake, depth assignment, preflight
gates, dispatch, artifact registration, ledger updates, quality gates,
checkpoint/handoff, and failure feedback dispatch. If a gate fails, route back
through `N9` to the subchain named in the route graph instead of continuing
linearly.

## Capability Matrix

Run `capabilities` when a task asks which tools are already available or what
needs to be added. The matrix separates available skills/apps from missing tool
gaps. Built-in local tools now include `prompt-normalizer`,
`storage-policy`, `research-source-hub`, `content-ingest`, `zotero-bridge`,
`claim-evidence-verifier`, `deep-loop-router`, `problem-loop`, and
`auto-loop-runner` with `auto-loop-watchdog`. Current missing tool gaps are
advisory until implemented:

- `repository-publisher` for Zenodo/OSF release and DOI/provenance backfill.
- `research-kg-builder` for project knowledge graphs.
- `experiment-runner-plus` for environment hashes, resource logging, retries, and batch jobs.
- `ethics-compliance-gate` for IRB/privacy/reporting/disclosure checks.
- `literature-monitor` for scheduled new-paper and citation monitoring.

If `route` reports blocking issues, do not advance to a later stage until the
issue is fixed or a user-approved defer/override decision is recorded with
`decision`.

Project profile changes route behavior:

- `--verification-strictness strict` blocks writing/review/finalization when
  evidence is partial or unverified.
- `--data-sensitivity sensitive|restricted` adds local-processing warnings.
- `--route-mode quick` shortens recommendations; `--route-mode strict` adds
  validation after each routed stage.
- `--target-venue` and `--citation-style` should be set before writing or
  final formatting work.

## Stages

Use these canonical stages:

- `INTAKE`
- `SCOPING`
- `LITERATURE`
- `DESIGN`
- `EXECUTION`
- `ANALYSIS`
- `SYNTHESIS`
- `WRITING`
- `REVIEW`
- `REVISION_FINALIZE`

Update the stage with `checkpoint --stage <STAGE>` when the project moves
between phases.

## Operating Rules

- Treat `.research-loop/` as the source of workflow state, not as the research
  evidence itself.
- Use `.research-loop/storage-policy.json` as the path contract for articles,
  datasets, figures, tables, manuscripts, reports, releases, and scratch files.
- Do not fabricate references, experiment results, or file provenance.
- If a claim, citation, result, or artifact cannot be verified, record it as
  unverified rather than silently accepting it.
- Use `run -- <command>` for experiments, tests, conversions, and figure
  generation whenever reproducibility matters.
- When a project is blocked or failing, run `problem-loop` before touching core
  files. Keep analysis, tests, and adjustment artifacts in the isolated scratch
  lab, then promote an approved case before implementing core changes.
- Use `handoff` before ending a major phase or opening a new Codex thread.
- If the user asks for substantive literature search, paper drafting, review,
  revision, Nature-style figures, or document conversion, route to the
  corresponding domain skill after updating the loop state.

## Resume Protocol

When the user asks to resume:

1. Run `status`.
2. Run `resume` unless the user only wants raw file inspection.
3. Run `route --intent "<current task>"` before selecting a domain skill.
4. Read `.research-loop/material-passport.json`.
5. Read the latest handoff from `.research-loop/handoffs/` if present.
6. Read the latest checkpoint from `.research-loop/checkpoints/`.
7. State the current stage, known materials, open questions, and the safest next
   action before making edits.

If `validate` reports high-severity issues, address or explicitly record the
user's decision to defer them before moving to a later research stage.

## Lifecycle Hooks

After `install_hooks.py` has run, Codex lifecycle events write:

- pre-snapshots at `SessionStart`
- tool failure records at `PostToolUse`
- session summaries and automatic checkpoints at `Stop`

Hook failures must not block user work; errors are written under
`$env:USERPROFILE\.codex\hooks\codex-research-loop\errors.log`.
