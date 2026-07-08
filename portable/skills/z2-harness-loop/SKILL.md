---
name: z2-harness-loop
description: Use for the user's z2quijote research-project work, especially when the request mentions z2, z2quijote, Quijote manuscript, current paper, paper draft, long-running work, continue the project, complete workflow execution, harness/loop, paragraph audit, manuscript audit, translation, citations, figures, tables, Word manuscript production, result verification, project planning, multi-fidelity upgrade planning, generalized NN model design, Sobol/PPR comparison checks, or continuous audit-and-revision. This skill separates smoke tests from real work, routes manuscript tasks to the formal z2 translation harness, and structures future project work as measurable design-build-test loops. Do not use for casual explanations or expensive Quijote/GP/NN runs unless the user explicitly asks to run them.
---

# Z2 Research Harness Loop

## Purpose

Use this as the durable workflow skill for the z2quijote research project. It supports two families of work:

- Near-term paper work: translation, polishing, formulas, citations, references, figures, tables, Word/PDF layout, and manuscript consistency.
- Continuing research work: result verification, experiment design, multi-fidelity planning, generalized NN model design, ablations, reproducibility, and project-roadmap execution.

Load `references/project-map.md` when the task needs path orientation, paper assets, known project goals, or experiment-context reminders.

## Decision Gate

Classify intent before running commands.

- Smoke only: the user asks whether the system works, how to trigger it, or asks for a quick readiness check.
- Manuscript loop: the user asks for long work on writing, translation, formulas, references, figures, Word output, or paragraph-by-paragraph audit.
- Research loop: the user asks for project planning, metric checks, experiment design, multi-fidelity upgrades, NN models, sampling design, or comparisons such as PPR versus Sobol.
- Expensive run: the user explicitly asks to launch training, GP/NN jobs, sampling optimization, or full numerical experiments.

For smoke only, do not run real manuscript audits or expensive jobs. For manuscript or research loops, inspect artifacts first, then execute the smallest loop that can produce evidence.

## Core Loop

Use this sequence for any long task:

1. Scope: restate the objective, files, metric, deliverable, and stop condition.
2. Map: inspect current repo state and relevant artifacts. Read `references/project-map.md` if paths or project context matter.
3. Harness: choose a validation surface before editing or running: unit test, smoke command, report, figure render, document render, metric recomputation, or artifact diff.
4. Build: make the smallest coherent change or draft increment.
5. Test: run the chosen harness. Prefer smoke/dry-run before long jobs.
6. Readback: inspect outputs, reports, logs, or rendered artifacts directly.
7. Loop: revise and re-test until the stop condition is met or a real blocker appears.
8. Report: summarize what changed, what passed, where outputs live, and what remains.

## Manuscript Harness

Use the formal z2 manuscript harness for translation and formula-retention audits.

Smoke tests:

```powershell
cd D:\work\pr_due_upload_files_20260317_220257
python versions\z2quijote\run.py translation-harness --help
python -m pytest versions\z2quijote\tests\test_translation_harness_loop.py -q
```

Full manuscript audit:

```powershell
cd D:\work\pr_due_upload_files_20260317_220257
python versions\z2quijote\run.py translation-harness
```

Custom manuscript audit:

```powershell
python versions\z2quijote\run.py translation-harness `
  --source "path\to\source_cn.md" `
  --candidate "path\to\candidate_en.md" `
  --out-dir "path\to\reports"
```

Read outputs in this order:

```text
versions\z2quijote\docs\translation_harness_reports\z2_translation_harness_loop_report.json
versions\z2quijote\docs\translation_harness_reports\z2_translation_harness_loop_report.md
versions\z2quijote\docs\translation_harness_reports\z2_translation_paragraph_audit.md
```

Use `--strict` only when the user wants a hard pass/fail signal.

## Paper Work Rules

- Preserve LaTeX formulas. Inline math stays in `\( ... \)` and display math stays in `\[ ... \]`.
- Prioritize missing display math, then inline math, key numbers, figure markers, key terms, citations, and paragraph coverage.
- For Word/PDF layout work, render and visually inspect representative pages before claiming completion.
- For citations, verify bibliographic reality and prefer journal versions when available.
- Keep report outputs near the z2 manuscript unless the user gives another target path.

## Research Work Rules

- Lock the metric before comparing methods. Record the target transform, validation set, bands, seeds, and training flow.
- When comparing designs such as PPR and Sobol64, verify whether only the sample-point distribution changed or whether training, preprocessing, hyperparameters, targets, or evaluation changed too.
- Treat multi-fidelity and generalized NN design as architecture plus evidence: define fidelity levels, transfer mechanism, uncertainty/bias target, data budget, ablations, and acceptance metrics.
- Prefer independent smoke tests, dry-runs, or small representative shards before long numerical runs.
- Do not launch expensive training or full simulations unless the user explicitly authorizes that level of work.

## Reporting Format

For manuscript loops, report:

- Files checked or edited.
- Pass rate, weighted score, display math count, missing inline math count, and Chinese residue count when available.
- Report paths.
- Next revision target.

For research loops, report:

- Hypothesis or design decision.
- Artifacts inspected.
- Validation method.
- Evidence found.
- Next build or experiment step.
