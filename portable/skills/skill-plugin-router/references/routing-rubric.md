# Routing Rubric

Use this rubric when choosing skills or plugins for a request.

## Score Signals

Add signal weight only when it is concrete in the latest request or relevant thread context.

- `+5`: explicit skill, plugin, app, connector, or MCP mention.
- `+4`: file type or artifact exactly matches a skill, such as PDF, DOCX, PPTX, spreadsheet, GitHub PR, Linear issue, Figma URL, or Excalidraw diagram.
- `+4`: user action exactly matches the skill description, such as install skill, create skill, fix CI, address PR comments, create slides, process PDF, or diagnose bug.
- `+3`: external service dependency requires a plugin/app connector.
- `+3`: user asks for current OpenAI/API/product behavior and a docs-first skill is available.
- `+2`: prior thread context shows this is a continuation of the same workspace or workflow.
- `+2`: user language contains strong Chinese trigger phrases for a known workflow, such as 拷打方案, 拆 issue, 诊断, 截图, 实验报告, or 插件匹配.
- `-4`: the newest message explicitly narrows away from an older context.
- `-3`: only a product name is present and no installed skill/plugin is an exact match.
- `-5`: user explicitly says not to use a capability.

## Confidence Bands

- `High`: score 8 or more, or explicit mention plus matching task.
- `Medium`: score 5 to 7, useful but not essential; include as optional or conditional.
- `Low`: score below 5; omit unless explaining why it is not a match.

## Tie Breakers

1. Newest user message beats prior thread context.
2. Explicit user request beats inferred convenience.
3. Plugin-backed skills beat generic skills for connected-service work.
4. Existing local capability beats install suggestion.
5. A narrow skill beats a broad skill when both apply.
6. If the task asks for execution, choose capabilities that enable action, not just explanation.

## Common Routes

- Create or update a skill: `skill-creator`; add `plugin-creator` only when packaging as a plugin or writing plugin marketplace metadata.
- Create or scaffold a plugin: `plugin-creator`.
- Install skills: `skill-installer`.
- Current OpenAI API/Product guidance: `openai-docs`, with official docs verification.
- Debug or repair failures: `diagnose`; add `tdd` only when the user asks for test-first work.
- GitHub PR/issue/CI: use the relevant `github:*` skill and GitHub tools.
- Google Docs/Sheets/Slides/Drive: use the relevant `google-drive:*` skill.
- Local PDF/DOCX/PPTX/XLSX artifacts: use `pdf`, `documents:documents`, `presentations:Presentations`, or `spreadsheets:Spreadsheets`.
- Visual design from Figma/Paper: use `figma` or `paper-design`.
- Break plans into tickets: `to-issues`; use `linear:linear` or GitHub tools only when the target tracker is explicit.

## Boundary Language

Use a short boundary note when needed:

- "This can route submitted or pasted draft text, but cannot inspect text before you send it."
- "This recommends a plugin/connector, but it is not currently callable in this session."
- "This is a near match, not an exact installed skill name."
