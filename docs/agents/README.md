# How we work with agents

**One page.** Process for program work in Cursor. Contract docs live under the program folder; this folder is **orchestration only**.

---

## Four layers (don't mix them)

| Layer | What | Where | Agent reads when |
|-------|------|-------|------------------|
| **1. Contract** | Locked decisions, phase scope, **ship gate** | The current `*_Pn_EXECUTION.md` | Implementing a phase |
| **2. Process** | How to start a LOOP | `.cursor/skills/phase-execution` | User attaches a plan folder |
| **3. Wiring** | Reviewers see the contract | `manifest.review_context.ssot`, `.cursor/BUGBOT.md` | First LOOP iteration; program switch |
| **4. Evidence** | What we learned on a real PR | `docs/agents/dogfood/` (optional) | After push; before next phase |

---

## Default iteration

```text
Read ONLY this phase's execution file
        ↓
FOR each subphase: implement → Deliverable green → next heading immediately
        ↓
Lint + phase gate + Bugbot CLOSE → commit
        ↓
Push kind: local → next phase
           first-push → push/PR if hosting allows → next phase
           batch → fetch review bot first when GitHub+Revy → one push
        ↓
next phase immediately (no “Continue?”)
```

**Flow flags:** `.agent/manifest.json` → `flows.*.enabled`

---

## Files in this folder

| File | Role |
|------|------|
| [ORCHESTRATION.md](./ORCHESTRATION.md) | LOOP detail, gates, anti-patterns |
| [PROMPTS.md](./PROMPTS.md) | Copy-paste Bugbot shells |
| [prompts/ROLES.md](./prompts/ROLES.md) | Human / master / reviewer |
| [prompts/OUTPUT_FORMAT.md](./prompts/OUTPUT_FORMAT.md) | VERB pass blocks |

**Skills:** `phase-execution` · `ship-changes` · `babysit-revy-pr` (only if installed)

---

## What we deliberately don't do

- Duplicate contract into `agents/` — point at program docs
- Bloat root `AGENTS.md` — one workflow section; detail here
- Push without local Bugbot
- Ask “Continue?” or end the turn mid-LOOP (except migration pause)
- Assume GitHub / Revy / pipenv when the manifest says otherwise
