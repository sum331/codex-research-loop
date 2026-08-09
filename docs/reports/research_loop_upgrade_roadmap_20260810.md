# Research Loop Upgrade Roadmap - 2026-08-10

## Current Fix

The deep-loop Arbiter now upgrades `retry_same_route` to
`escalate_problem_loop` when the Research Council or Adversarial Gate requests
P10 and the gate vector shows high diagnostic risk, fatal objections, repeated
failure, or an unknown root cause. This keeps local retry for narrow failures
but makes the expert problem-resolution chain easier to trigger during
unattended long runs.

## Recent Technical Signals Reviewed

- Google Co-Scientist and the Nature Co-Scientist paper emphasize a
  multi-agent scientific loop: generation, critique, ranking, evolution,
  meta-review, literature grounding, tool verification, and test-time compute
  scaling.
  Sources:
  https://research.google/blog/accelerating-scientific-breakthroughs-with-an-ai-co-scientist/
  https://www.nature.com/articles/s41586-026-10644-y
- Sakana AI Scientist-v2 points to progressive agentic tree search, autonomous
  experiment design/execution/analysis/writing, and VLM feedback for figure and
  manuscript refinement.
  Source: https://arxiv.org/abs/2504.08066
- AlphaEvolve shows that stable code-building and scientific discovery improve
  when LLM creativity is bound to executable evaluators, evolutionary search,
  and program-level verification.
  Sources:
  https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/
  https://arxiv.org/abs/2506.13131
- DeepSeek-Prover-V2 highlights recursive subgoal decomposition, synthesis of
  solved subgoals, reinforcement learning, and Lean 4 verification as a useful
  template for mathematical abstraction.
  Source: https://arxiv.org/abs/2504.21801
- AlphaProof/AlphaGeometry 2 and later formal-proof-search work emphasize
  grounded verifier feedback, candidate generation, problem-specific search,
  high variance accounting, and expert validation of generated proofs.
  Sources:
  https://www.nature.com/articles/s41586-025-09833-y
  https://arxiv.org/html/2605.22763v1
  https://arxiv.org/html/2607.07779v1
- Recent critiques of autonomous AI scientists warn that shallow end-to-end
  loops often miss tacit failure knowledge, compress diversity too early, and
  lack experimental feedback. This supports our design choice to keep
  hypothesis portfolios, experiment-runner reports, and adversarial gates as
  first-class control-plane inputs.
  Source: https://arxiv.org/html/2605.08956v1
- AlphaGeometry2 adds symbolic engines, synthetic data, knowledge sharing
  between search trees, and natural-language-to-formal-problem progress.
  Source: https://arxiv.org/abs/2502.03544
- OpenAI FrontierScience and proof-submission notes emphasize expert-written
  tasks, rubric grading, longer reasoning budgets, formal/proof verification
  where possible, and explicit limits around uncontrolled human selection.
  Sources:
  https://openai.com/index/frontierscience/
  https://openai.com/index/first-proof-submissions/

## Near-Term Plugin Upgrades

1. Harness Registry

Status: implemented in the 2026-08-10 build as `harness-registry`.

Add a project-local `.research-loop/harnesses/` registry for test surfaces:
commands, expected artifacts, scoring rubrics, timeouts, resource ceilings,
failure tags, and promotion thresholds. Deep-loop and problem-loop should read
this registry before deciding retry versus P10.

2. Hypothesis Portfolio

Status: implemented in the 2026-08-10 build as `hypothesis-portfolio`.

Add a hypothesis population layer under OPHIS:
`generate -> critique -> rank -> evolve -> validate`. Each candidate should
carry assumptions, expected observations, falsifiers, required data, and a
minimal validation command or source check. This directly improves divergent
thinking and prevents premature convergence on the first plausible plan.

3. Expert Council Profiles

Replace short dynamic expert blurbs with richer expert cards stored under
`.research-loop/experts/profiles/`. Each expert should include scope,
required reads, admissible evidence, preferred tests, red flags, failure modes,
and an output schema. Runtime expert construction can still happen, but it
should be grounded in reusable profile templates plus project-specific context.

4. Evolutionary Code Builder

Status: implemented as a scratch-only planning and promotion-gate node in the
2026-08-10 build as `code-builder`. It does not execute variants yet.

Add an optional code-builder mode for stable implementation work:
create variants in scratch, run the harness registry, keep a small archive of
champions and failures, summarize deltas, and promote only the best passing
candidate. This follows the AlphaEvolve pattern without mutating core files
before the promotion gate.

5. Math Abstraction Chain

Status: implemented as a definition-assumption-subgoal-verifier planning node
in the 2026-08-10 build as `math-abstraction`. Formal proof execution remains
optional and external.

Add a math-specific subchain or P10 branch:
natural-language problem -> definitions -> assumptions -> lemma graph ->
symbolic/computational model -> verifier/proof assistant attempt -> reviewed
derivation. Initial tools can be lightweight: SymPy for algebra, Z3 for
constraints, property tests for identities, and optional Lean 4 for formal
proofs when available.

6. Frontier-Style Research Grading

Add rubric-driven grading for open research tasks. A report should not only
pass tests; it should score dimensions such as novelty, evidence grounding,
method validity, mathematical consistency, artifact reproducibility,
counterfactual coverage, and communication quality.

## 2026-08-10 Implemented Build

- Added CLI commands: `harness-registry`, `hypothesis-portfolio`,
  `code-builder`, `math-abstraction`, `experiment-runner`, and `autopilot`.
- Added MCP tools: `research_harness_registry`,
  `research_hypothesis_portfolio`, `research_code_builder`, and
  `research_math_abstraction`, `research_experiment_runner`, and
  `research_goal_autopilot`.
- Added project-local control directories:
  `.research-loop/harnesses/`, `.research-loop/hypothesis-portfolios/`,
  `.research-loop/code-builders/`, `.research-loop/math-abstractions/`,
  `.research-loop/experiment-runs/`, and `.research-loop/autopilot/`.
- Deep-loop now reads these records through `mechanistic_context`, injects them
  into gate vectors, continuation prompts, Research Council, and Adversarial
  Gate killer tests.
- Dynamic expert construction now adds specialized experts for harness design,
  hypothesis tournaments, scratch-only evolutionary code building, and
  mathematical abstraction when those records exist. It also adds an
  experiment-runner reproducibility auditor when monitored runs are present.
- `autopilot` now turns rough natural-language goals into a no-confirmation
  trigger plan with route sequence, auto-start actions, primed control-plane
  records, and an optional `auto-loop-watchdog` launch.
- `experiment-runner` now plans or executes monitored commands with environment
  fingerprints, retry history, stdout/stderr logs, artifact readback,
  harness-compatible summaries, and deep-loop-readable reports.
- New tests cover advanced-context ingestion into deep-loop, scratch-only code
  builder planning, autopilot trigger plans, experiment-runner feedback into
  deep-loop experts, capability matrix exposure, and MCP mapping.

Remaining high-value work:

- Batch/leaderboard extensions for experiment-runner-plus: multiple named
  candidates, normalized resource usage, comparative ranking, and promotion
  packets for code-builder champions.
- A frontier-style rubric grader that scores novelty, evidence grounding,
  method validity, mathematical consistency, reproducibility, counterfactual
  coverage, and communication quality.
- Optional formal-verifier adapters for Lean 4, SymPy, Z3, and property-test
  generation when those tools are installed.

## Medium-Term Design Direction

- Convert the current linear deep-loop into an explicit tree search controller:
  route candidates are nodes, harness results are edge weights, and P10 is the
  diagnostic expansion branch for high-risk failures.
- Use external supervisors only as fail-open reviewers, never as single points
  of failure.
- Keep all exploratory variants, expert debates, generated hypotheses, and
  failed proofs in scratch/lab space until promotion.
- Require every long unattended run to publish a compact state packet:
  current node, active subchain, candidate queue, last gate vector, best
  validated artifact, blocker status, and next automatic command.

## Priority Mapping

- Stable code construction: Harness Registry + Evolutionary Code Builder.
- Deep analysis: OPHIS Hypothesis Portfolio + richer Expert Council Profiles.
- Divergent problem solving: tree search controller + tournament ranking.
- Mathematical abstraction: Math Abstraction Chain + verifier-backed proof or
  computation checks.
