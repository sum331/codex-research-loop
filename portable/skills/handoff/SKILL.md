---
name: handoff
description: >
  Compact the current conversation/work into a handoff document for another agent
  or future session, including status, decisions, artifacts, commands, open
  questions, and suggested skills. Trigger when the user asks for a handoff,
  transfer note, session summary, continuation brief, context compaction, next
  agent brief, or says 交接文档, 接力, 总结当前上下文, 下个会话继续.
argument-hint: "What will the next session be used for?"
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save to the temporary directory of the user's OS - not the current workspace.

Include a "suggested skills" section in the document, which suggests skills that the agent should invoke.

Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
