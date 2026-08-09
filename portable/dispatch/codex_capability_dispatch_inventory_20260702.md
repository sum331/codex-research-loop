# Codex 能力调度清单 2026-07-02

状态: 草案 v0.3。范围: 统一整理本机与本项目可用的 skill、插件、MCP/app connector 与 hooks 调度链，先确定功能与状态，不调整迁移进程，不删除或停用任何组件。

## 1. 总览

| 组件层 | 当前状态 | 结论 |
|---|---|---|
| 本地 skills | 能力扫描识别 250 个 skill；`C:\Users\ASUS\.codex\skills` 下有 39 个用户级顶层目录（不含 `.system` 与 `_shared`）；磁盘实测总计 249 个 `SKILL.md`（含插件缓存） | OK。实际使用时仍需按触发规则读取对应 `SKILL.md` |
| 插件 | 能力扫描识别 38 个插件 manifest；`config.toml` 当前启用 11 个插件 | OK。以后以 `config.toml` 中启用项为准，不把缓存副本等同于已启用插件 |
| classic MCP servers | `codex doctor` 报告 `MCP servers 0` | 注意。当前没有传统 `[mcp_servers]` 配置，但 Codex app connector 工具可通过 `tool_search` 按需暴露 |
| Codex app connector MCP tools | GitHub、Google Drive、Figma、Linear、Hugging Face、Codex app automation/list_projects 已可发现 | 按需可用。调用前先用 `tool_search` 暴露工具，并遵守对应 skill 前置要求 |
| 用户级 hooks | `UserPromptSubmit`、`SessionStart`、`PostToolUse`、`Stop` 已配置 | OK。`UserPromptSubmit` 已升级为调度表驱动的 pre-run dispatcher；local-task-hooks 生命周期记录通过基础烟测 |
| 项目级 Codex hook | `.codex/hooks.json` 配置 `Stop` hook 到 `scripts\codex_stop_quijote_change_hook.py` | OK。包装器会把日志写入 `.hook/`，stdout 仅输出合法 hook JSON |
| Git hooks | `core.hooksPath=.githooks`，`.githooks\pre-commit` 调用 `scripts\record_quijote_change.py` | OK。`sh -n` 语法检查通过，记录脚本 dry-run 通过 |

状态定义:

- `OK`: 已找到入口，配置可解析，并完成基本语法或 smoke 验证。
- `按需可用`: 当前会话可通过插件/app 工具发现，但需要任务触发、skill 前置或用户登录态。
- `注意`: 不是失败，但容易在后续调度中误判。
- `待治理`: 需要专门修复、收敛或补文档，本轮不直接改。

## 2. Skills 分区

能力扫描命令:

```powershell
python C:\Users\ASUS\.codex\skills\skill-plugin-router\scripts\scan_codex_capabilities.py --format markdown
```

扫描结论:

- Codex home: `C:\Users\ASUS\.codex`
- Skills: 250
- Plugin manifests: 38
- Marketplace entries: 0

本地顶层 skill 目录:

| 分区 | 代表目录 | 用途 | 状态 |
|---|---|---|---|
| 调度与治理 | `skill-plugin-router`, `local-task-hooks`, `handoff`, `skill-creator`, `plugin-creator` | prompt 路由、能力盘点、hook 包装、交接文档、skill/plugin 创建 | OK |
| 诊断与开发 | `diagnose`, `tdd`, `prototype`, `electron-dev`, `triage`, `to-issues` | bug 诊断、测试驱动、原型、桌面应用、任务拆分 | OK |
| 学术与论文 | `academic-research-suite`, `nature-*`, `word`, `pdf`, `z2-harness-loop` | 文献、Nature 风格写作、Word/PDF、z2quijote 项目工作流 | OK |
| 图像与设计 | `figma`, `paper-design`, `excalidraw-diagram`, `cleanshot` | 设计稿、白板图、截图/OCR、设计系统 | 按需可用 |
| 外部服务 | `readwise-mcp`, `mobile-codex-inbox`, `wispr-analytics` | 阅读库、移动任务入口、语音历史分析 | 按需可用 |
| 浏览器与系统自动化 | plugin-cache 内的 `browser`, `chrome` skills；`raycast-alfred` 为 macOS 向能力 | 本地/Chrome 浏览器验证、截图、页面交互；macOS 启动器能力 | 注意。Windows 下优先使用 browser/chrome，`raycast-alfred` 不作为本机主路径 |

调度原则:

1. 用户显式点名 skill 时优先使用该 skill。
2. 任务语义明显匹配 skill 时，也要先读取对应 `SKILL.md`。
3. 多个 skill 同时适用时，选最小集合，先读规则，再动文件或调用外部工具。
4. `skill-plugin-router` 只提供 advisory routing context；最新用户请求始终优先。

## 3. 插件分区

当前 `C:\Users\ASUS\.codex\config.toml` 启用插件:

| 插件 ID | 主要功能 | 状态 |
|---|---|---|
| `github@openai-curated` | GitHub 仓库、issue、PR、评论、CI 状态 | OK |
| `google-drive@openai-curated` | Google Drive、Docs、Sheets、Slides | OK |
| `linear@openai-curated` | Linear issue、project、status update | OK |
| `documents@openai-primary-runtime` | DOCX/文档处理 | OK |
| `spreadsheets@openai-primary-runtime` | Excel/CSV/表格处理 | OK |
| `presentations@openai-primary-runtime` | PPT/Slides 处理 | OK |
| `figma@openai-curated` | Figma 读取、设计生成、变量、截图 | 按需可用 |
| `browser@openai-bundled` | Codex 内置浏览器自动化 | 按需可用 |
| `pdf@openai-primary-runtime` | PDF 读取、渲染、检查、生成 | OK |
| `template-creator@openai-primary-runtime` | artifact template skill 创建 | OK |
| `chrome@openai-bundled` | 用户 Chrome 自动化，需要用户登录态时使用 | 按需可用 |

插件缓存根目录:

- `C:\Users\ASUS\.codex\plugins\cache\chatgpt-global`
- `C:\Users\ASUS\.codex\plugins\cache\openai-bundled`
- `C:\Users\ASUS\.codex\plugins\cache\openai-curated`
- `C:\Users\ASUS\.codex\plugins\cache\openai-curated-remote`
- `C:\Users\ASUS\.codex\plugins\cache\openai-primary-runtime`

本机个人插件:

- `C:\Users\ASUS\.codex\plugins\prompt-submit-skill-router`

治理原则:

- 调度时优先相信 `config.toml` 的启用项。
- 缓存里存在多个版本时，不直接把所有缓存版本视为可用入口。
- 需要安装或调用新插件时，先通过 `tool_search` 或插件安装工具确认是否有可调用能力。

## 4. MCP 与 app connector

`codex doctor` 结果显示 classic MCP servers 为 0。因此本机当前没有传统 MCP server 配置需要维护。

但 Codex app connector 工具可通过 `tool_search` 按需发现。本轮已发现的工具族:

| 工具族 | 代表能力 | 状态 | 调度注意 |
|---|---|---|---|
| GitHub | PR/issue/comment/status/branch/file 操作 | 按需可用 | 通过 GitHub skill 或具体任务触发，避免把本地 git 操作和远端 PR 操作混淆 |
| Google Drive | Drive 文件、Docs、Sheets、Slides、评论 | 按需可用 | 需要 Drive skill 前置时先读 skill；表格/幻灯片/文档按文件类型分流 |
| Figma | `use_figma`, 设计生成、变量、截图、新建文件 | 按需可用 | Figma 工具调用前必须加载对应 Figma skill，例如 `figma-use`、`figma-create-new-file` |
| Linear | issue、project、milestone、status update、search/fetch | 按需可用 | 外部 issue 状态变更应显式说明目标对象 |
| Hugging Face | model/dataset/space/paper/doc/job | 按需可用 | 技术资料优先官方/Hub 元数据，涉及远程 job 需单独确认成本与硬件 |
| Codex app | automation/list_projects 等 | 按需可用 | 自动化任务要先查找 automation 工具，不手写 raw directive |

调度原则:

1. classic MCP 配置为空不代表 app connector 不可用。
2. app connector 需要时先 `tool_search`，让本轮工具显式暴露后再调用。
3. 对 Figma、Google Drive、GitHub 等连接器，遵循对应 skill 的前置读取规则。

## 5. Hooks 调度链

### 5.1 用户级 hooks

文件: `C:\Users\ASUS\.codex\hooks.json`

| 事件 | 命令 | 功能 | 状态 |
|---|---|---|---|
| `UserPromptSubmit` | `python "C:\Users\ASUS\.codex\plugins\prompt-submit-skill-router\scripts\user_prompt_submit_router.py"` | 读取当前 prompt、可用上文 payload、近期 router 日志与项目调度表，注入 skill/plugin/MCP/hook 调用建议 | OK |
| `SessionStart` | `python "C:\Users\ASUS\.codex\hooks\local-task-hooks\codex_lifecycle_hook.py" SessionStart` | 捕获本地 hook 快照 | OK |
| `PostToolUse` | `python "C:\Users\ASUS\.codex\hooks\local-task-hooks\codex_lifecycle_hook.py" PostToolUse` | 收集 hook 失败日志 | OK |
| `Stop` | `python "C:\Users\ASUS\.codex\hooks\local-task-hooks\codex_lifecycle_hook.py" Stop` | 写入本地 hook 汇总 | OK |

已做验证:

```powershell
python -m py_compile C:\Users\ASUS\.codex\plugins\prompt-submit-skill-router\scripts\user_prompt_submit_router.py C:\Users\ASUS\.codex\hooks\local-task-hooks\codex_lifecycle_hook.py
'{"prompt":"统一整理 skill plugin mcp hooks 调度 状态 功能"}' | python C:\Users\ASUS\.codex\plugins\prompt-submit-skill-router\scripts\user_prompt_submit_router.py
```

router smoke 输出可按场景推荐 `skill-plugin-router`、`local-task-hooks`、`browser`、`figma`、`nature-reader`、`nature-citation`、`github`、`linear` 等注册能力，说明 `UserPromptSubmit` 入口可运行，并已从静态表升级为调度表驱动。

### 5.2 项目级 Codex Stop hook

文件: `.codex\hooks.json`

当前命令:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-Location -LiteralPath 'D:\work\pr_due_upload_files_20260317_220257'; python scripts\codex_stop_quijote_change_hook.py"
```

功能:

- Codex `Stop` 时调用 `scripts\codex_stop_quijote_change_hook.py`。
- 包装器再调用 `scripts\record_quijote_change.py --auto --scope quijote-codex-auto --source codex-stop --include-working-tree --no-codex --diff-char-limit 60000`。
- 人类可读日志写入 `.hook\quijote-change-stop-hook.log`。
- stdout 仅输出 `{}`，避免破坏 Codex hook JSON 协议。

状态: OK。`scripts\codex_stop_quijote_change_hook.py` 与 `scripts\record_quijote_change.py` 已通过 `py_compile`。`--dry-run` 会输出 `{}`，符合 hook wrapper 行为。

### 5.3 Git pre-commit hook

当前 Git 配置:

```powershell
git config --get core.hooksPath
# .githooks
```

文件: `.githooks\pre-commit`

功能:

- pre-commit 时调用 `scripts/record_quijote_change.py`。
- 支持环境变量:
  - `QUIJOTE_CHANGE_LOG_SCOPE`
  - `QUIJOTE_CHANGE_LOG_SOURCE`
  - `QUIJOTE_CHANGE_LOG_NO_CODEX`
  - `QUIJOTE_CHANGE_LOG_CODEX_TIMEOUT`
  - `QUIJOTE_CHANGE_LOG_DIFF_CHAR_LIMIT`

已做验证:

```powershell
& "C:\Program Files\Git\bin\sh.exe" -n .githooks\pre-commit
python scripts\record_quijote_change.py --auto --scope hook-inventory-smoke --source codex-inventory --include-working-tree --no-codex --diff-char-limit 2000 --dry-run
```

结果: `sh -n` 通过；dry-run 生成了变更审计条目，未要求停止或修改当前迁移进程。

## 6. 调度决策树

后续统一调度时按这个顺序判断:

1. 用户是否显式点名 skill、插件、app 或 hook。
2. 当前任务是否已有项目内固定入口，例如 z2quijote、Quijote hook、path governance、migration registry。
3. 是否需要外部连接器。需要时先 `tool_search` 暴露工具，再按 skill 规则调用。
4. 是否涉及文件写入、迁移、删除或 Git 操作。涉及时先确认范围，优先 dry-run 或 smoke。
5. 是否会影响正在运行的数据迁移。若会影响，单独排队，不混入本轮工程治理。

推荐默认路由:

| 任务类型 | 首选能力 | 备注 |
|---|---|---|
| 能力盘点、skill/plugin 路由 | `skill-plugin-router` | 使用扫描脚本确认本机真实状态 |
| hook 包装、生命周期日志 | `local-task-hooks` | 只治理 hook，不替代项目业务逻辑 |
| z2quijote 项目工作流 | `z2-harness-loop` + 项目脚本 | 先读项目文件，再运行 smoke |
| 论文/审稿/发布包 | `academic-research-suite` 或 `nature-*` | 发布包必须做绝对路径卫生检查 |
| Word/PDF/表格/PPT | 对应 runtime skill 或 plugin | 需要渲染检查时走文件类型专用工具 |
| GitHub/Drive/Linear/Figma/HF | 对应 app connector + skill | 先通过 `tool_search` 暴露工具 |
| 浏览器验证 | `browser` 或 `chrome` | 本地页面优先 browser；需要用户登录态用 chrome |

## 6.1 每轮运行前调度 hook

入口: `C:\Users\ASUS\.codex\plugins\prompt-submit-skill-router\scripts\user_prompt_submit_router.py`

触发: 用户提交 prompt 后、模型正式处理本轮请求前，由用户级 `UserPromptSubmit` hook 自动执行。

输入来源:

- 当前 hook payload 中的 `prompt` / `userPrompt` / `input` / `message`。
- hook payload 中可能存在的 `messages` / `conversation` / `transcript` / `thread` / `context`，作为上文上下文信号。
- `C:\Users\ASUS\.codex\plugins\prompt-submit-skill-router\router.log` 的近期匹配记录；仅当当前 prompt 含“继续”“接着”“下一步”“上文”等延续语义时作为弱信号。
- 本项目 `docs\codex_capability_dispatch_inventory_20260702.md` 的调度注册表。

输出:

- stdout 输出 Codex hook JSON。
- `hookSpecificOutput.additionalContext` 包含推荐调用顺序、Registry ID、置信度、功能说明、调用方式和边界说明。
- `router.log` 追加本次 prompt 字符数、使用的 registry、匹配到的 registry IDs 与分数。

边界:

- 该 hook 不能直接强制加载 skill，也不能直接调用 MCP/app connector 工具。
- 对 skill/system-skill，hook 会要求本轮 agent 在实质工作前读取对应 `SKILL.md`。
- 对插件/app connector，hook 会要求本轮 agent 先用 `tool_search` 暴露工具，再调用。
- 对 hooks，hook 只提示其用途和验证路径，不在业务请求中手动执行。

## 7. 风险与待治理项

| 项 | 状态 | 处理建议 |
|---|---|---|
| 插件缓存存在多个来源与版本 | 注意 | 文档和调度只引用 `config.toml` 启用项；缓存清理另开任务 |
| classic MCP server 为 0 | 注意 | 当前不需要修；只要在文档中区分 classic MCP 和 app connector MCP |
| `codex doctor` 报告混合认证信号 | 注意 | ChatGPT 登录与 `OPENAI_API_KEY` 同时存在；连接器出错时优先检查认证路径 |
| rollouts 占用约 2.33 GB | 待治理 | 可单独做 Codex 历史/缓存清理，不混入本轮项目文件治理 |
| PowerShell here-string 容易误写 | 注意 | 中文/JSON smoke 优先用单行 JSON 管道或严格 here-string 格式 |
| 工作树体量大导致 `git status --short` 超时 | 注意 | 后续状态检查优先用限定范围命令，避免每轮全量扫工作树 |
| 迁移进程仍独立运行 | 注意 | 本文不管理迁移生命周期，迁移文件治理另设专题 |

## 8. 后续规范草案

1. 新增 skill 或插件前，必须写清楚触发语义、入口路径、是否需要外部登录态、是否有副作用。
2. 新增 hook 前，必须提供 `py_compile` 或脚本解析检查，并说明 stdout 是否必须为 hook JSON。
3. 所有自动调度只给 advisory context；最终执行仍以用户当前请求和项目文件为准。
4. 所有 destructive 操作，例如删除、迁移、覆盖、远端 issue/PR 状态变更，默认先 dry-run 或明确列出目标。
5. app connector 与 classic MCP 分开记录，避免把 `codex doctor` 的 `MCP servers 0` 误解为所有 connector 不可用。
6. 项目级 hook 与用户级 hook 分开维护: 用户级 hooks 管 Codex 生命周期，项目级 hooks 管当前仓库审计。
7. 每次能力治理后追加一条验证记录，至少包含扫描命令、hook 语法检查、router smoke 和项目 hook dry-run。

## 9. 调度注册表与强制检查

配套检查功能:

```powershell
python scripts\maintenance\check_codex_capability_registry.py
python scripts\maintenance\check_codex_capability_registry.py --dump-current
```

用途:

- 扫描 `C:\Users\ASUS\.codex\skills` 中的本地 skills 与 `.system` system skills。
- 扫描 `C:\Users\ASUS\.codex\config.toml` 中启用的插件与 classic MCP server 配置。
- 扫描 `C:\Users\ASUS\.codex\plugins` 下的个人插件 manifest。
- 扫描用户级 `C:\Users\ASUS\.codex\hooks.json`、项目级 `.codex\hooks.json` 与 Git `core.hooksPath` 下的 hooks。
- 如果存在未登记的能力 ID，则返回非零退出码。

新增能力的准入流程:

1. 先在本节注册表新增 `Registry ID`、触发/调用方式、功能、状态。
2. 再新增或修改 skill、插件、MCP 或 hook 配置。
3. 运行 `python scripts\maintenance\check_codex_capability_registry.py`。
4. 对 skill 运行 `quick_validate.py`；对 hook 运行 JSON 解析、`py_compile`、shell/PowerShell 解析或 dry-run。
5. 涉及 destructive 操作时仍需单独 dry-run，不得用注册通过替代安全确认。

`.githooks\pre-commit` 已接入该检查器: 提交前先检查调度注册表，再执行原有 Quijote change-log hook。

### 9.1 本地 skills

| Registry ID | 调用方式 | 功能 | 状态 |
|---|---|---|---|
| `skill:academic-research-suite` | `$academic-research-suite` 或 ARS 别名 | 深度研究、文献综述、论文草稿、审稿与研究流程 | OK |
| `skill:research-loop` | `$research-loop`；research loop、loop、autopilot、goal runner、one-shot research、direct result、deep-loop、auto-loop、auto-loop-watchdog、problem-loop、experiment-runner、experiment-runner-plus、OPHIS、harness-registry、hypothesis-portfolio、code-builder、math-abstraction、一句话目标、直接给出结果、不反复确认、自动完成、实验运行器、机制观察、机制假设、机制干预、机制库、验证面、假设池、发散假设、代码构建、数学抽象、无人值守、专家委员会、对抗 gate、阀门、科研工作流请求 | 项目级科研 loop 控制面：状态、材料、证据、存储、一句话目标 autopilot、机制账本、harness 注册、假设组合、experiment-runner-plus、scratch-only 代码构建、数学抽象链、深循环、专家委员会、对抗 gate、仲裁与无人值守续跑 | OK |
| `skill:cleanshot` | `$cleanshot`；截图、OCR、录屏类请求 | CleanShot X 截图、OCR、标注 | 平台注意: macOS 工具，Windows 下仅登记不作为主路径 |
| `skill:diagnose` | `$diagnose`；debug/诊断/排查请求 | 复现、最小化、假设、插桩、修复、回归测试 | OK |
| `skill:electron-dev` | `$electron-dev`；Electron/桌面应用请求 | Electron、React、Vite、IPC、打包 | OK |
| `skill:explain-complex-concepts` | `$explain-complex-concepts`；解释/讲解/拆解复杂天文学、物理、统计、机器学习或论文概念请求 | 面向中文学习环境的复杂科学概念解释，包含直觉、公式、天文学与 ML 桥接、误解、自检和证据状态 | OK |
| `skill:excalidraw-diagram` | `$excalidraw-diagram`；架构图/流程图/白板图请求 | 生成 Excalidraw JSON 图 | OK |
| `skill:figma` | `$figma`；Figma URL、节点、设计稿实现请求 | Figma MCP 设计读取与代码实现 | 按需可用 |
| `skill:grill-me` | `$grill-me`；要求拷问/推敲方案 | 一问一答压实方案、边界与取舍 | OK |
| `skill:grill-with-docs` | `$grill-with-docs`；结合项目文档拷问方案 | 先读项目文档，再质询计划与术语 | OK |
| `skill:handoff` | `$handoff`；交接/续接/压缩上下文请求 | 生成工作交接文档 | OK |
| `skill:llm-wiki` | `$llm-wiki`；知识库/wiki/llm-wiki/知识图谱/消化素材/查询或维护个人知识库请求 | 构建和维护本地 Markdown wiki，支持素材消化、页面互链、知识图谱数据与离线 HTML 图谱生成 | OK |
| `skill:local-task-hooks` | `$local-task-hooks`；hook task/快照/日志请求 | PowerShell 任务包装与 Codex 生命周期 hook | OK |
| `skill:mobile-codex-inbox` | `$mobile-codex-inbox`；移动端任务桥接请求 | 处理移动渠道提交的 Codex 任务 | 按需可用 |
| `skill:nature-academic-search` | `$nature-academic-search` | 多源文献检索、引文校验、MeSH/引用文件 | OK |
| `skill:nature-citation` | `$nature-citation` | Nature/CNS 风格严格引文补充 | OK |
| `skill:nature-data` | `$nature-data` | Data Availability、FAIR、数据仓库计划 | OK |
| `skill:nature-figure` | `$nature-figure` | Nature/high-impact 图件生成、审计、润色 | OK |
| `skill:nature-paper-to-patent` | `$nature-paper-to-patent` | 论文/代码/图件转中文发明专利草案 | OK |
| `skill:nature-paper2ppt` | `$nature-paper2ppt` | 科研论文转中文 PPTX 汇报 | OK |
| `skill:nature-polishing` | `$nature-polishing` | Nature 风格英文润色、重构与翻译 | OK |
| `skill:nature-reader` | `$nature-reader` | 论文 PDF/DOI/arXiv 双语精读 Markdown | OK |
| `skill:nature-response` | `$nature-response` | 审稿意见逐点回复与 rebuttal 审计 | OK |
| `skill:nature-reviewer` | `$nature-reviewer` | 模拟 Nature 风格审稿报告 | OK |
| `skill:nature-writing` | `$nature-writing` | Nature 风格 manuscript section 写作 | OK |
| `skill:paper-design` | `$paper-design`；Paper Design 相关请求 | Paper Design MCP 原型、设计同步、React/Tailwind 转换 | 按需可用 |
| `skill:pdf` | `$pdf`；PDF 读取/生成/渲染检查请求 | PDF 抽取、渲染、生成、布局检查 | OK |
| `skill:prototype` | `$prototype`；原型/快速验证请求 | 终端或 UI 原型验证 | OK |
| `skill:raycast-alfred` | `$raycast-alfred`；Raycast/Alfred 请求 | macOS 启动器自动化 | 平台注意: Windows 下仅登记不作为主路径 |
| `skill:readwise-mcp` | `$readwise-mcp`；Readwise/Reader 请求 | Readwise/Reader 文档、高亮、阅读库 | 需外部连接器 |
| `skill:skill-plugin-router` | `$skill-plugin-router`；skill/plugin 路由请求 | 能力盘点、路由建议、插件/app 分流 | OK |
| `skill:tdd` | `$tdd`；测试先行/红绿重构请求 | 测试驱动开发循环 | OK |
| `skill:to-issues` | `$to-issues`；拆 issue/拆任务请求 | 将计划拆成可执行 issue/tickets | OK |
| `skill:triage` | `$triage`；分拣/标注/优先级请求 | issue triage 与状态标签 | OK |
| `skill:wispr-analytics` | `$wispr-analytics`；Wispr/口述历史请求 | Wispr Flow 历史分析与词典管理 | 按需可用 |
| `skill:word` | `$word`；Word/DOCX 请求 | Word 文档创建、编辑、转换、验证 | OK |
| `skill:z2-harness-loop` | `$z2-harness-loop`；z2/z2quijote/Quijote manuscript/project 请求 | z2quijote 长线工作、论文、harness loop、验证规划 | OK |

说明: `C:\Users\ASUS\.codex\skills\codex-primary-runtime` 是运行时目录，不含 `SKILL.md`，不按 skill 注册。

### 9.2 system skills

| Registry ID | 调用方式 | 功能 | 状态 |
|---|---|---|---|
| `system-skill:imagegen` | `$imagegen` 或图像生成/编辑请求 | 生成或编辑位图图像 | OK |
| `system-skill:openai-docs` | `$openai-docs`；OpenAI API/Codex 文档请求 | 查询官方 OpenAI 文档并引用 | OK |
| `system-skill:plugin-creator` | `$plugin-creator`；创建/更新 Codex 插件 | 脚手架与维护个人插件 | OK |
| `system-skill:skill-creator` | `$skill-creator`；创建/更新 skill | 设计、初始化、验证 skill | OK |
| `system-skill:skill-installer` | `$skill-installer`；安装 skill 请求 | 安装 curated 或 GitHub skill | OK |

### 9.3 插件与 app connector

| Registry ID | 调用方式 | 功能 | 状态 |
|---|---|---|---|
| `plugin:browser@openai-bundled` | `tool_search` 暴露 browser 工具；或 `$browser` skill | Codex 内置浏览器自动化 | 按需可用 |
| `plugin:chrome@openai-bundled` | `tool_search` 暴露 chrome 工具；或 `$chrome` skill | 用户 Chrome、登录态页面、已有标签页 | 按需可用 |
| `plugin:documents@openai-primary-runtime` | `$documents` 或文档类 runtime 工具 | DOCX/Docs 文档处理 | OK |
| `plugin:figma@openai-curated` | Figma 请求先加载对应 Figma skill，再 `tool_search` | Figma 文件、变量、截图、设计生成 | 按需可用 |
| `plugin:github@openai-curated` | GitHub 请求先用 GitHub skill 或 `tool_search` | GitHub repo、issue、PR、CI | 按需可用 |
| `plugin:google-drive@openai-curated` | Google Drive/Docs/Sheets/Slides 请求触发 | Drive 文件与 Google 办公套件 | 按需可用 |
| `plugin:linear@openai-curated` | Linear issue/project 请求触发 | Linear 项目、issue、状态更新 | 按需可用 |
| `plugin:pdf@openai-primary-runtime` | `$pdf` 或 PDF runtime 工具 | PDF 读取、渲染、生成、验证 | OK |
| `plugin:presentations@openai-primary-runtime` | `$presentations` 或 PPT/Slides 请求 | PPTX/Slides 创建、编辑、导出 | OK |
| `plugin:prompt-submit-skill-router` | 用户提交 prompt 时由 `UserPromptSubmit` 自动调用 | 基于当前输入、上文 payload、近期 router 日志和调度注册表注入 skill/plugin/MCP/hook 调用建议 | OK |
| `plugin:spreadsheets@openai-primary-runtime` | `$spreadsheets` 或表格请求 | XLSX/CSV/Sheets 分析与编辑 | OK |
| `plugin:template-creator@openai-primary-runtime` | `$template-creator` 或模板 skill 请求 | artifact template skill 创建与更新 | OK |

### 9.4 MCP 与 hooks

| Registry ID | 调用方式 | 功能 | 状态 |
|---|---|---|---|
| `mcp:classic:none` | 不调用；由 `codex doctor` 和注册检查器确认 | 当前没有 classic MCP server 配置 | OK |
| `hook:user:UserPromptSubmit:prompt-submit-skill-router` | 提交用户 prompt 时自动触发 | 运行调度表驱动 pre-run dispatcher，向本轮注入推荐调用顺序 | OK |
| `hook:user:SessionStart:local-task-hooks` | Codex session start 自动触发 | 记录本地 hook 快照 | OK |
| `hook:user:PostToolUse:local-task-hooks` | 工具调用后自动触发 | 收集 hook 失败上下文 | OK |
| `hook:user:PostToolUse:powershell-noprofile-executionpolicy-bypass-command-c-users-asus-cache-codex-runtimes-codex-primary-runtime-dependencies-python-python-exe-c-users-asus-plugins-codex-research-loop-scripts-codex-research-lifecycle-hook-py-posttooluse` | 工具调用后自动触发 | 记录 research-loop 工具事件 | OK |
| `hook:user:Stop:local-task-hooks` | Codex stop 自动触发 | 写入生命周期摘要 | OK |
| `hook:user:SessionStart:powershell-noprofile-executionpolicy-bypass-command-c-users-asus-cache-codex-runtimes-codex-primary-runtime-dependencies-python-python-exe-c-users-asus-plugins-codex-research-loop-scripts-codex-research-lifecycle-hook-py-sessionstart` | Codex session start 自动触发 | 启动 research-loop 快照 | OK |
| `hook:user:Stop:powershell-noprofile-executionpolicy-bypass-command-c-users-asus-cache-codex-runtimes-codex-primary-runtime-dependencies-python-python-exe-c-users-asus-plugins-codex-research-loop-scripts-codex-research-lifecycle-hook-py-stop` | Codex stop 自动触发 | 写入 research-loop checkpoint | OK |
| `hook:project:Stop:codex-stop-quijote-change` | 项目级 Codex Stop 自动触发 | 调用 Quijote change-log wrapper，stdout 输出合法 JSON | OK |
| `hook:project:Stop:powershell-noprofile-executionpolicy-bypass-command-set-location-literalpath-d-work-pr-due-upload-files-20260317-220257-d-work-tools-uv-python-cpython-3-10-windows-x86-64-none-python-exe-scripts-z2-codex-autocontinue-hook-py` | 项目级 Codex Stop 自动触发 | 调用 Z2 auto-continuation hook，按状态决定是否唤醒后续循环 | OK |
| `hook:git:pre-commit:quijote-change-log` | `git commit` 前自动触发 | 先检查调度注册表，再记录 Quijote change log | OK |

### 9.5 机器校验标记

以下 HTML 注释是注册检查器读取的机器标记。更新上方表格时必须同步更新此标记块。

<!-- capability-registry-id: hook:git:pre-commit:quijote-change-log -->
<!-- capability-registry-id: hook:project:Stop:codex-stop-quijote-change -->
<!-- capability-registry-id: hook:project:Stop:powershell-noprofile-executionpolicy-bypass-command-set-location-literalpath-d-work-pr-due-upload-files-20260317-220257-d-work-tools-uv-python-cpython-3-10-windows-x86-64-none-python-exe-scripts-z2-codex-autocontinue-hook-py -->
<!-- capability-registry-id: hook:user:PostToolUse:local-task-hooks -->
<!-- capability-registry-id: hook:user:PostToolUse:powershell-noprofile-executionpolicy-bypass-command-c-users-asus-cache-codex-runtimes-codex-primary-runtime-dependencies-python-python-exe-c-users-asus-plugins-codex-research-loop-scripts-codex-research-lifecycle-hook-py-posttooluse -->
<!-- capability-registry-id: hook:user:SessionStart:local-task-hooks -->
<!-- capability-registry-id: hook:user:SessionStart:powershell-noprofile-executionpolicy-bypass-command-c-users-asus-cache-codex-runtimes-codex-primary-runtime-dependencies-python-python-exe-c-users-asus-plugins-codex-research-loop-scripts-codex-research-lifecycle-hook-py-sessionstart -->
<!-- capability-registry-id: hook:user:Stop:local-task-hooks -->
<!-- capability-registry-id: hook:user:Stop:powershell-noprofile-executionpolicy-bypass-command-c-users-asus-cache-codex-runtimes-codex-primary-runtime-dependencies-python-python-exe-c-users-asus-plugins-codex-research-loop-scripts-codex-research-lifecycle-hook-py-stop -->
<!-- capability-registry-id: hook:user:UserPromptSubmit:prompt-submit-skill-router -->
<!-- capability-registry-id: mcp:classic:none -->
<!-- capability-registry-id: plugin:browser@openai-bundled -->
<!-- capability-registry-id: plugin:chrome@openai-bundled -->
<!-- capability-registry-id: plugin:documents@openai-primary-runtime -->
<!-- capability-registry-id: plugin:figma@openai-curated -->
<!-- capability-registry-id: plugin:github@openai-curated -->
<!-- capability-registry-id: plugin:google-drive@openai-curated -->
<!-- capability-registry-id: plugin:linear@openai-curated -->
<!-- capability-registry-id: plugin:pdf@openai-primary-runtime -->
<!-- capability-registry-id: plugin:presentations@openai-primary-runtime -->
<!-- capability-registry-id: plugin:prompt-submit-skill-router -->
<!-- capability-registry-id: plugin:spreadsheets@openai-primary-runtime -->
<!-- capability-registry-id: plugin:template-creator@openai-primary-runtime -->
<!-- capability-registry-id: skill:academic-research-suite -->
<!-- capability-registry-id: skill:research-loop -->
<!-- capability-registry-id: skill:cleanshot -->
<!-- capability-registry-id: skill:diagnose -->
<!-- capability-registry-id: skill:electron-dev -->
<!-- capability-registry-id: skill:explain-complex-concepts -->
<!-- capability-registry-id: skill:excalidraw-diagram -->
<!-- capability-registry-id: skill:figma -->
<!-- capability-registry-id: skill:grill-me -->
<!-- capability-registry-id: skill:grill-with-docs -->
<!-- capability-registry-id: skill:handoff -->
<!-- capability-registry-id: skill:llm-wiki -->
<!-- capability-registry-id: skill:local-task-hooks -->
<!-- capability-registry-id: skill:mobile-codex-inbox -->
<!-- capability-registry-id: skill:nature-academic-search -->
<!-- capability-registry-id: skill:nature-citation -->
<!-- capability-registry-id: skill:nature-data -->
<!-- capability-registry-id: skill:nature-figure -->
<!-- capability-registry-id: skill:nature-paper-to-patent -->
<!-- capability-registry-id: skill:nature-paper2ppt -->
<!-- capability-registry-id: skill:nature-polishing -->
<!-- capability-registry-id: skill:nature-reader -->
<!-- capability-registry-id: skill:nature-response -->
<!-- capability-registry-id: skill:nature-reviewer -->
<!-- capability-registry-id: skill:nature-writing -->
<!-- capability-registry-id: skill:paper-design -->
<!-- capability-registry-id: skill:pdf -->
<!-- capability-registry-id: skill:prototype -->
<!-- capability-registry-id: skill:raycast-alfred -->
<!-- capability-registry-id: skill:readwise-mcp -->
<!-- capability-registry-id: skill:skill-plugin-router -->
<!-- capability-registry-id: skill:tdd -->
<!-- capability-registry-id: skill:to-issues -->
<!-- capability-registry-id: skill:triage -->
<!-- capability-registry-id: skill:wispr-analytics -->
<!-- capability-registry-id: skill:word -->
<!-- capability-registry-id: skill:z2-harness-loop -->
<!-- capability-registry-id: system-skill:imagegen -->
<!-- capability-registry-id: system-skill:openai-docs -->
<!-- capability-registry-id: system-skill:plugin-creator -->
<!-- capability-registry-id: system-skill:skill-creator -->
<!-- capability-registry-id: system-skill:skill-installer -->

## 10. 本轮验证记录

2026-07-04 追加 `llm-wiki`:

- 已安装到 `C:\Users\ASUS\.codex\skills\llm-wiki`，并在本文件注册 `skill:llm-wiki` 与机器校验标记。
- 已补齐 `jq` 到 `D:\work\.tools\PortableGit\usr\bin\jq.exe`，并构建 `packages\graph-engine\dist\engine.iife.js`。
- 已按 `llm-wiki` 官方 `MANAGED_ITEMS` 收敛安装内容，清理直接整仓安装带入的 `node_modules`、`workbench`、`tests`、`assets`、`designs`；保留 graph HTML 所需的 `packages\graph-engine\dist`。
- `llm-wiki` 内部 `deps` 与 `platforms` 中的伴随入口，例如 `baoyu-url-to-markdown`、`youtube-transcript`、`llm-wiki-upgrade`，归属 `skill:llm-wiki`，不作为本表主调度入口单独登记。
- 已修复本机 `C:\Users\ASUS\.codex\skills\.system\skill-creator\scripts\quick_validate.py` 的 UTF-8 读取与 frontmatter 兼容字段校验。
- 已执行 `python scripts\maintenance\check_codex_capability_registry.py --codex-home C:\Users\ASUS\.codex`，结果为 `Capability registry OK: 49 entries registered.`
- 已执行 `python C:\Users\ASUS\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\ASUS\.codex\skills\llm-wiki`，结果为 `Skill is valid!`
- 已执行 `UserPromptSubmit` router smoke，`llm-wiki`/知识图谱请求被高置信度路由到 `skill:llm-wiki`。
- 已执行图谱链路 smoke: `build-graph-data.sh` 生成 `graph-data.json`，`build-graph-html.sh` 生成非空 `knowledge-graph.html`。

本轮修复:

- `C:\Users\ASUS\.codex\skills\.system\skill-creator\scripts\quick_validate.py` 改为显式 UTF-8 读取 `SKILL.md`，修复 Windows 默认 GBK 导致的 `UnicodeDecodeError`。
- `quick_validate.py` 增加对现有本机 skill frontmatter 兼容字段的识别，包括 `author`、`version`、`status`、`argument-hint`、`tools`、`tags` 等；这些字段已存在于可发现 skills 中，不再误判为失效。
- `.githooks\pre-commit` 接入 `scripts\maintenance\check_codex_capability_registry.py`，提交前先检查能力注册表，再执行原有 Quijote change-log hook。
- 新增 `.gitattributes`，固定 `.githooks/*` 与 `*.sh` 为 LF，避免 Windows 换行破坏 shell hook。
- `C:\Users\ASUS\.codex\plugins\prompt-submit-skill-router\scripts\user_prompt_submit_router.py` 已重写为调度表驱动的 pre-run dispatcher，读取当前输入、可用上文 payload、近期 router 日志和本项目注册表，并输出推荐调用顺序。
- `C:\Users\ASUS\.codex\plugins\prompt-submit-skill-router\.codex-plugin\plugin.json` 版本更新为 `0.2.0`，描述同步为 registry-driven routing。

已执行并通过:

```powershell
python C:\Users\ASUS\.codex\skills\skill-plugin-router\scripts\scan_codex_capabilities.py --format markdown
codex doctor
python -m py_compile C:\Users\ASUS\.codex\skills\.system\skill-creator\scripts\quick_validate.py
python C:\Users\ASUS\.codex\skills\.system\skill-creator\scripts\quick_validate.py <each local skill directory>
python -m py_compile C:\Users\ASUS\.codex\plugins\prompt-submit-skill-router\scripts\user_prompt_submit_router.py C:\Users\ASUS\.codex\hooks\local-task-hooks\codex_lifecycle_hook.py scripts\codex_stop_quijote_change_hook.py scripts\record_quijote_change.py
python -m py_compile scripts\maintenance\check_codex_capability_registry.py
python scripts\maintenance\check_codex_capability_registry.py
& "C:\Program Files\Git\bin\sh.exe" -n .githooks\pre-commit
'{"prompt":"统一整理 skill plugin mcp hooks 调度 状态 功能"}' | python C:\Users\ASUS\.codex\plugins\prompt-submit-skill-router\scripts\user_prompt_submit_router.py
'{"prompt":"\u6839\u636e Figma \u8bbe\u8ba1\u7a3f\u5b9e\u73b0\u9875\u9762\uff0c\u5e76\u7528\u6d4f\u89c8\u5668\u6253\u5f00\u672c\u5730 localhost \u9a8c\u8bc1","cwd":"D:\\work\\pr_due_upload_files_20260317_220257"}' | python C:\Users\ASUS\.codex\plugins\prompt-submit-skill-router\scripts\user_prompt_submit_router.py
'{"prompt":"\u6253\u5f00\u4e00\u4e2a PDF \u8bba\u6587\uff0c\u505a\u4e2d\u6587\u7cbe\u8bfb\u5e76\u6574\u7406\u5f15\u7528","cwd":"D:\\work\\pr_due_upload_files_20260317_220257"}' | python C:\Users\ASUS\.codex\plugins\prompt-submit-skill-router\scripts\user_prompt_submit_router.py
'{"prompt":"检查这个 GitHub PR 的 CI 并修复 review comments，然后同步 Linear issue","cwd":"D:\\work\\pr_due_upload_files_20260317_220257"}' | python C:\Users\ASUS\.codex\plugins\prompt-submit-skill-router\scripts\user_prompt_submit_router.py
python scripts\record_quijote_change.py --auto --scope hook-inventory-smoke --source codex-inventory --include-working-tree --no-codex --diff-char-limit 2000 --dry-run
git check-attr text eol -- .githooks\pre-commit
```

另外，`C:\Users\ASUS\.codex\hooks\local-task-hooks\*.ps1` 已完成 PowerShell parser 解析检查。

2026-07-08 追加 `explain-complex-concepts`:

- 已安装到 `C:\Users\ASUS\.codex\skills\explain-complex-concepts`，并在本文件注册 `skill:explain-complex-concepts` 与机器校验标记。
- 已同步补齐当前 `C:\Users\ASUS\.codex\hooks.json` 中已存在的 research-loop 用户级 `SessionStart`、`PostToolUse`、`Stop` hook 注册项；未修改 hook 配置本身。
- 已在 `C:\Users\ASUS\.codex\plugins\prompt-submit-skill-router\scripts\user_prompt_submit_router.py` 的 `SPECIAL_TRIGGERS` 中加入 `skill:explain-complex-concepts` 语义触发词，包括 residual-space learning、power spectrum、FITS/WCS、redshift、attention/注意力机制、复杂概念、天文学、物理、机器学习等。
- 已执行 `python D:\work\pr_due_upload_files_20260317_220257\scripts\maintenance\check_codex_capability_registry.py --registry D:\work\pr_due_upload_files_20260317_220257\docs\codex_capability_dispatch_inventory_20260702.md --codex-home C:\Users\ASUS\.codex --repo-root D:\work\pr_due_upload_files_20260317_220257`，结果为 `Capability registry OK: 53 entries registered.`
- 已执行 `python -m py_compile C:\Users\ASUS\.codex\plugins\prompt-submit-skill-router\scripts\user_prompt_submit_router.py`，结果通过。
- 已执行 `python C:\Users\ASUS\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\ASUS\.codex\skills\explain-complex-concepts`，结果为 `Skill is valid!`
- 已执行 `UserPromptSubmit` router smoke：residual-space learning、红移/距离、注意力机制、FITS/WCS 请求均路由到 `skill:explain-complex-concepts`；纯论文英文润色请求仍路由到 `skill:nature-polishing`，未被新 skill 误抢。
