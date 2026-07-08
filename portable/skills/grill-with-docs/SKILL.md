---
name: grill-with-docs
description: >
  Grill a plan/design against the existing codebase docs and domain model:
  inspect CONTEXT.md, CONTEXT-MAP.md, docs/adr, glossary, and code before asking;
  ask one question at a time; sharpen terminology; update CONTEXT.md/ADRs as
  decisions crystallize. Trigger broadly when a plan/design/modification,
  opinion discussion, solution comparison, route/path comparison, architecture
  choice, product/design decision, tradeoff analysis, or multi-source/multi-layer
  data problem should be grounded in project docs, code, files, datasets, ADRs,
  context maps, or prior decisions. Also trigger when the user says plan review
  with docs, architecture boundary clarification, ADR/context updates, documented
  decision making, 结合文档拷打方案, 根据 ADR 审设计, 更新 CONTEXT, 确定架构边界,
  方案设计, 方案修改, 意见讨论, 路径比较, 多方信源, 多层数据. Use together with
  grill-me for broad design grilling plus evidence-backed project grounding.
---

<what-to-do>

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing.

If a question can be answered by exploring the codebase, explore the codebase instead.

</what-to-do>

<trigger-policy>

Trigger proactively for any request involving 方案设计, 方案修改, 意见讨论, 路径比较, 多方信源, 多层数据, architecture/product/design decisions, or route comparisons when the answer should be constrained by existing docs, code, ADRs, datasets, issue history, or other project artifacts.

The user does not need to explicitly say "grill-with-docs". If evidence exists in the workspace, inspect it first; only ask the user about decisions that cannot be resolved from project sources.

Pair with `grill-me` when the task needs both broad decision-tree questioning and docs/code/data-grounded validation.

</trigger-policy>

<supporting-info>

## Domain awareness

During codebase exploration, also look for existing documentation:

### File structure

Most repos have a single context:

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `CONTEXT-MAP.md` exists at the root, the repo has multiple contexts. The map points to where each one lives:

```
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                          ← system-wide decisions
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/                 ← context-specific decisions
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

Create files lazily — only when you have something to write. If no `CONTEXT.md` exists, create one when the first term is resolved. If no `docs/adr/` exists, create it when the first ADR is needed.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` right there. Don't batch these up — capture them as they happen. Use the format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

`CONTEXT.md` should be totally devoid of implementation details. Do not treat `CONTEXT.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).

</supporting-info>
