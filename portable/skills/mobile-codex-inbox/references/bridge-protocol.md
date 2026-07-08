# Bridge Protocol

## Task States

- `pending`: Mobile message was accepted and is waiting for Codex.
- `running`: Codex claimed the task.
- `waiting_user`: Codex needs clarification from the mobile user.
- `done`: Task completed.
- `failed`: Task could not be completed.
- `cancelled`: Task was cancelled.

## Task Schema

Tasks are stored under `data/tasks/<task_id>.json` in the bridge project.

```json
{
  "id": "task_20260520213000_abcdef",
  "status": "pending",
  "source": "feishu",
  "sourceMessageId": "om_xxx",
  "sourceChatId": "oc_xxx",
  "sourceSenderId": "ou_xxx",
  "sourceChatType": "p2p",
  "text": "fix the login page validation and add tests",
  "routingMode": "project-thread",
  "project": "default",
  "projectPath": "C:\\work\\crm",
  "targetFiles": ["src\\login.ts"],
  "thread": {
    "mode": "new",
    "sessionId": null,
    "forkFrom": null,
    "allowFork": false
  },
  "attempts": 0,
  "createdAt": "2026-05-20T13:30:00.000Z",
  "updatedAt": "2026-05-20T13:30:00.000Z",
  "claimedAt": null,
  "completedAt": null,
  "resultText": null,
  "errorText": null,
  "runnerLogPath": null
}
```

## Desktop Sync

Mobile tasks are mirrored for desktop recovery:

- Journal: `data/desktop-sync/DESKTOP_SYNC.md`
- Task mirrors: `data/desktop-sync/tasks/<task_id>.md`
- Commands: `npm run sync -- status`, `npm run sync -- show <task_id>`, `npm run sync -- rebuild`

## Dispatch Modes

- `/codex`: creates tasks with `routingMode=project-thread` and binds them to the resolved default project thread when `defaultSessionId` exists.
- `/codex0`: creates tasks with `routingMode=dispatcher` and forces the older dispatcher conversation, bypassing default project-thread binding.
- `CODEX_DISPATCH_MODE=dispatcher`: dispatcher remains the fallback and `/codex0` destination. `project`, `projectPath`, and `targetFiles` are hints; `projectPath` is not required. The dispatcher can answer temporary questions directly or ask the user for a missing project/action.
- Direct project thread route: when a task has `thread.mode=resume` and `thread.sessionId`, or the resolved project has `defaultSessionId`, the watcher bypasses the dispatcher. With `CODEX_THREAD_RUNNER=interactive`, it starts a visible `codex resume <session_id>` run; otherwise it runs `codex exec resume <session_id>`.
- `CODEX_DISPATCH_MODE=project`: the watcher resolves the project before launching Codex. `projectPath`, a registered `project`, or a default project is required.

## CLI Contract

All commands run from the bridge project.

```powershell
npm run tasks -- list [--status pending]
npm run tasks -- next
npm run tasks -- claim [task_id]
npm run tasks -- show <task_id>
npm run tasks -- complete <task_id> --message "<text>" [--no-send]
npm run tasks -- fail <task_id> --message "<text>" [--no-send]
npm run tasks -- ask <task_id> --message "<text>" [--no-send]
npm run tasks -- cancel <task_id> [--message "<text>"] [--no-send]
```

`complete`, `fail`, `ask`, and `cancel` send a Feishu message unless `--no-send` is passed.
