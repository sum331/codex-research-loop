# Z2 Project Map

Use this reference only when path orientation or project context matters.

## Roots

- Repo root: `D:\work\pr_due_upload_files_20260317_220257`
- Formal z2 project: `D:\work\pr_due_upload_files_20260317_220257\versions\z2quijote`
- Main z2 runner: `versions\z2quijote\run.py`
- Generic hloop package: `versions\z2quijote\src\z2quijote\hloop`
- Manuscript harness script: `versions\z2quijote\scripts\run_translation_harness_loop.py`
- Manuscript harness reports: `versions\z2quijote\docs\translation_harness_reports`

## Paper Assets

- Current Word-oriented manuscript candidate: `versions\z2quijote\docs\manuscript_word\z2quijote_full_manuscript_20260701.md`
- Chinese manuscript source candidate: `versions\z2quijote\docs\paper_manuscript_20260701\chinese_source\z2quijote_manuscript_sections_1_2_cn_20260701.md`
- Reference library directory: `versions\z2quijote\docs\paper_references`
- Current BibTeX: `versions\z2quijote\docs\paper_references\current_manuscript_references.bib`
- Figure gallery root: `H:\DATA\z2quijote\paper_figures\main_results_20260701\numbered_gallery`
- Figure images: `H:\DATA\z2quijote\paper_figures\main_results_20260701\numbered_gallery\figures`
- Tables: `H:\DATA\z2quijote\paper_figures\main_results_20260701\numbered_gallery\tables`
- Source data: `H:\DATA\z2quijote\paper_figures\main_results_20260701\numbered_gallery\source_data`

## Near-Term Paper Goals

- Produce a clear English manuscript from the Chinese draft while preserving formulas and paragraph coverage.
- Integrate verified citations, figures, tables, captions, and Word-ready layout.
- Keep figure/table sizing professional: single-column for local explanatory graphics, paired small panels when two figures jointly explain one point, and wider placement only for central multi-panel results.
- Maintain a reportable audit trail through the translation harness outputs.

## Continuing Research Goals

- Extend the current method into a multi-fidelity version.
- Design generalized NN models where appropriate.
- Verify result comparisons, especially claims such as improvement over Sobol64, by checking whether the training flow is identical and only point distributions differ.
- Build future work as measurable loops: plan, artifact inspection, small smoke run, controlled experiment, report, and next iteration.

## Validation Principles

- Prefer actual file/artifact inspection over memory-only answers.
- Use smoke tests or dry-runs before long jobs.
- Lock metric definitions before interpreting scientific deltas. For cosmology residuals, keep target transform and evaluation bands explicit.
- Avoid widening comparison scope unless the user asks; keep best-vs-baseline comparisons pinned to the requested design pair.
