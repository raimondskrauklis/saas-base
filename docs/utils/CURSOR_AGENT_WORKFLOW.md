# Cursor agent workflow — quick ref

Short map. Detail: [agents/README.md](../agents/README.md).

| Who | File |
|-----|------|
| Any new chat | [AGENTS.md](../../AGENTS.md) |
| Flow flags | [.agent/manifest.json](../../.agent/manifest.json) |
| Master — LOOP | [agents/README.md](../agents/README.md) |
| Bugbot (pre-push) | [.cursor/BUGBOT.md](../../.cursor/BUGBOT.md) |
| Roles + verbs | [agents/prompts/ROLES.md](../agents/prompts/ROLES.md) |

```text
Human    → judgment, pause, when to push
Master   → only agent you talk to; implement; block ship until gates green
Reviewer → Bugbot subagent; one task per spawn
```

```text
implement → tests → lint → LOCAL BUGBOT → commit → push only if hosting + ship gate
```

**Do not push** with open Bugbot blockers. Skills: `phase-execution` · `ship-changes` · `babysit-revy-pr` (if installed).

Pack SSOT: sibling `../agent-workflow` (`pack_source` in the manifest).
