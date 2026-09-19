---
name: chunk-execution
description: >-
  Execute one plan subphase at a time (P0.1, P0.2, …) with Cursor TODOs, then
  stop. Use only when the user explicitly invokes chunk-execution or asks for a
  single subphase — not for full plan LOOP.
---

# Chunk execution (one subphase)

**When:** user explicitly asks for **one** subphase / chunk (e.g. “do P0.1 only”, `@chunk-execution`).

**Not:** full plan delivery — use **`phase-execution`** for that.

---

## Steps

1. Read the product `.cursorrules` / `AGENTS.md` for stack anti-patterns (migrations, etc.).
2. Open execution file; identify **single** subphase (e.g. P0.1).
3. Create **2–5** TODOs for that subphase only — target files, deliverable, verify command.
4. Implement → run deliverable tests → mark TODOs done.
5. If subphase is **P0.0 / PR review context**: wire SSOT + `.cursor/BUGBOT.md` per `phase-execution` P0.0 and `manifest.review_context`.
6. **Stop here.** Report what shipped and what subphase is next. **`ship-changes`** if the user wants commit/push.

Do **not** pre-create TODOs for later subphases. Do **not** continue to the next subphase unless the user asks in a **new** message.
