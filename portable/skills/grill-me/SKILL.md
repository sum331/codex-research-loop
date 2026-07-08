---
name: grill-me
description: >
  Grill the user on a plan/design before execution: ask one sharp question at a
  time, resolve scope, assumptions, tradeoffs, edge cases, dependencies, and
  decision-tree branches, while recommending an answer for each question. Trigger
  broadly for plan/design creation, plan modification, solution comparison,
  route/path comparison, architecture/product/design discussion, opinion review,
  tradeoff analysis, multi-source or multi-layer data reasoning, ambiguous scope,
  or any high-uncertainty decision that should be clarified before execution.
  Also trigger when the user says grill me, stress-test this plan, challenge this
  design, clarify scope/boundaries, ask me questions first, 拷打我, 拷打方案,
  方案设计, 方案修改, 意见讨论, 路径比较, 多方信源, 多层数据, 确定边界,
  先问清楚, 帮我追问, 方案评审. Use together with grill-with-docs when project
  docs, code, ADRs, files, datasets, or prior decisions should constrain the
  discussion.
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time.

If a question can be answered by exploring the codebase, explore the codebase instead.

## Trigger policy

Trigger proactively for any request involving 方案设计, 方案修改, 意见讨论, 路径比较, 多方信源, 多层数据, architecture choices, implementation routes, product/design alternatives, or tradeoff-heavy decisions. The user does not need to literally say "grill me".

When multiple sources or existing project artifacts matter, pair this with `grill-with-docs` so the questions are grounded in docs, code, data, and prior decisions.
