# Agent orchestration

**Index:** [README.md](./README.md) · **Prompts:** [PROMPTS.md](./PROMPTS.md)

**Roles:** [prompts/ROLES.md](./prompts/ROLES.md) — human talks to master only; master compiles briefs for Bugbot.

---

## Golden rule: local Bugbot before **every** ship

Master **blocks run** until the gate is green.

```text
implement → tests → lint → phase gate → LOCAL BUGBOT → commit
  → local: next phase
  → first-push: push/PR if hosting allows
  → batch: fetch review bot first when GitHub+Revy, then one push
```

**Cadence:** P0 local; P1 first-push; mid phases local; last batch. Bugbot every phase.

**Closeout:** final phase = gap pass (`post-finish-gap-pass`) + doc sync — not optional.

---

## Review context wiring (first LOOP iteration)

Read `.agent/manifest.json` before wiring. SSOT = `review_context.ssot`.

On program switch: replace `programs[]` with a single new entry; update `BUGBOT.md`.

---

## Parent agent discipline

| Do | Don't |
|----|-------|
| Read **only** current phase execution file | Re-read entire findings every subphase |
| Deliverable green, then next heading immediately | Implement several subphases then test once |
| Poll Bugbot (and Revy if applicable) until clean | Ask “Continue?” mid-LOOP |
| `feat/<topic>` from default branch | Implement on `main` / `master` |
| Pause only after a migration subphase | Stop between ordinary subphases |

**Sequential:** code complete → Bugbot → fix → re-Bugbot if blockers → push (when the ship gate says so).
