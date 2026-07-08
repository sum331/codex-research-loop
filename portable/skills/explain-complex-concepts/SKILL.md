---
name: explain-complex-concepts
description: Use when the user asks to explain, unpack, teach, clarify, build intuition for, or interpret complex astronomy, physics, statistics, machine-learning, data-analysis, or research-paper concepts, including equations, figures, methods, jargon, FITS/WCS, cosmology, power spectra, emulators, or residual learning; not for pure polishing, citation formatting, or literature review unless explanation is primary.
---

# Explain Complex Concepts

## Overview

Produce Chinese-first explanations of complex scientific and technical ideas for a learner with basic physics, beginner astronomy training, and limited machine-learning background. The goal is understanding, not merely translation, summary, or stylistic polishing.

## Load References

Read only the reference files needed for the current request:

- `references/learner-profile.md`: use when the user does not specify an audience, or when the explanation must fit the default astronomy learner.
- `references/explanation-modes.md`: use when selecting the output shape, depth, or teaching mode.
- `references/evidence-policy.md`: use when explaining papers, current missions, datasets, software, model results, citations, or any claim that may need verification.
- `references/astronomy-ml-bridge.md`: use when the concept touches astronomy, cosmology, observational data, statistics, machine learning, emulators, spectra, coordinates, or scientific data formats.
- `references/acceptance-tests.md`: use before editing, validating, or deploying this skill.

## Routing Boundary

Use this skill when explanation is the main deliverable. Do not use it as the primary skill for pure manuscript polishing, citation formatting, slide creation, code implementation, bibliography management, or a full literature review. If those tasks contain a difficult concept that must be explained first, use this skill for the explanation phase, then switch to the appropriate task skill.

When a request says "translate", "summarize", or "rewrite", inspect intent. If the user wants to understand what a paragraph, equation, method, or term means, use this skill. If they only want fluent wording, do not use this skill.

## Core Workflow

1. Identify the concept, the learner gap, the source status, and the desired depth.
2. Choose an explanation mode from `references/explanation-modes.md`; default to `deep-intuition` when the user does not specify depth.
3. State the short answer first, then build intuition before formalism.
4. Introduce definitions, equations, assumptions, variables, and units only as needed for the selected mode.
5. Connect the concept to an astronomy, physics, statistics, or ML example when helpful.
6. Separate established knowledge, source-grounded claims, current facts, and your own inference.
7. End with common misconceptions and a small self-check unless the user asked for a very short answer.

## Default Explanation Contract

For normal complex questions, structure the answer in this order:

1. **问题定位**: name the exact concept and what confusion it likely causes.
2. **一句话版本**: give the most compact correct answer.
3. **直观图景**: explain the idea with a concrete physical or data-analysis picture.
4. **严格说法**: give the formal definition, boundary condition, or mathematical object.
5. **公式层**: include equations only when they clarify the concept.
6. **天文学连接**: connect to cosmology, observation, instruments, spectra, images, coordinates, or simulation when relevant.
7. **ML/统计连接**: connect to modeling, inference, likelihood, residual learning, emulators, or uncertainty when relevant.
8. **常见误解**: list the traps that would lead to a wrong understanding.
9. **自检问题**: provide one or two short questions the learner can answer to test understanding.
10. **证据状态**: state whether the explanation is stable textbook knowledge, based on user-provided source text, current verified information, or inference.

Short answers may compress the contract, but must preserve the short answer, intuition, caveat, and evidence status.

## Multi-Question Rule

When the user asks several explanation questions in one message, apply a compact contract to each numbered answer:

1. short answer;
2. mechanism or intuition;
3. formula with symbol definitions when useful;
4. misconception or limitation;
5. evidence status.

Add explicit evidence-status and self-check fields. Prefer natural Chinese labels generated in the answer, but if exact non-ASCII label copying may be unsafe, use the ASCII-safe labels `Evidence status:` and `Self-check:`. A batched educational answer is incomplete if it has no evidence-status field or no self-check field. Do not drop these fields just because the response is batched.

## Formula Rules

Use renderable Markdown LaTeX for all mathematics:

- Inline formula source must use `\( ... \)`.
- Display formula source must use `\[ ... \]`.
- Do not use dollar-delimited math.
- Do not write formulas as plain-text variables when they are mathematical expressions.
- Define every nontrivial symbol, subscript, unit, and assumption near the equation.
- Use `\mathrm{}` for English-word subscripts, such as \(P_{\mathrm{truth}}\), \(k_{\mathrm{max}}\), or \(D_{\mathrm{L}}\).

If the formula depends on a convention or model, state it before interpreting the result. For example, a cosmological distance formula depends on the assumed background model and parameters, not just on redshift.

## Language Rules

- Answer in Simplified Chinese unless the user explicitly asks otherwise.
- Preserve important English technical terms on first use, for example "红移（redshift）" or "功率谱（power spectrum）".
- Avoid jargon cascades. If three or more specialized terms are needed in one sentence, define or split them.
- Do not sound patronizing. Assume basic physics literacy, but do not assume astronomy, cosmology, statistics, or ML fluency beyond beginner level.
- Use analogies as scaffolding, not as proof. After an analogy, state where it breaks.

## Evidence Rules

When the user asks about a specific paper, dataset, mission, software package, release, leaderboard, API, or "latest/current/today" fact, verify with primary or reliable sources when available. If verification is not possible in the current environment, say so and distinguish stable background explanation from unverified current claims.

For current or versioned facts, include concrete dates and source labels or links in the answer. Do not silently rely on memory or an unstated lookup.

Never invent citations, DOI, arXiv IDs, page numbers, figure numbers, numerical results, or mission statuses. If the user provided text is the only source, say "基于你给出的段落" instead of implying independent confirmation.

## Common Failures To Avoid

| Failure | Correction |
| --- | --- |
| Translating terminology without explaining the mechanism | Explain what problem the concept solves and how it behaves. |
| Starting with equations before intuition | Give the one-sentence version and physical picture first unless `formula-first` is requested. |
| Giving an analogy as if it were exact | State the analogy's useful part and failure point. |
| Omitting variable definitions or units | Define symbols and assumptions next to the formula. |
| Treating a paper's claim as established fact | Label it as source-grounded and verify when needed. |
| Overloading the answer with unrelated textbook material | Stay centered on the user's exact confusion. |

## Final Self-Check

Before responding, check:

- The answer teaches the concept rather than only restating it.
- The depth matches the learner profile and selected mode.
- All formulas use `\( ... \)` or `\[ ... \]`.
- Variables, assumptions, and units are defined.
- Current, paper-specific, or software-specific claims are verified or clearly marked.
- The answer contains no fabricated citations, identifiers, or numerical claims.
