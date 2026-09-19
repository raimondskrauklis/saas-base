# Distilled prompts

**Parent:** [README.md](../README.md) · **LOOP:** [ORCHESTRATION.md](../ORCHESTRATION.md)

Contract docs + phase scope + VERB — not long Custom Instructions.

**Wiring:** `.cursor/BUGBOT.md` → program docs + [CURSOR_AGENT_WORKFLOW.md](../../utils/CURSOR_AGENT_WORKFLOW.md).

---

## Two tracks

| Track | When | Bugbot verb |
|-------|------|-------------|
| **Phase LOOP** | Phase slice done | FIND → CLOSE |
| **Babysit** | Greptile thread (if enabled) | VALIDATE → CLOSE |

Master must set **VERB** — agent won't infer the track.

---

## Files

| File | Use when |
|------|----------|
| [ROLES.md](./ROLES.md) | Who talks to whom |
| [OUTPUT_FORMAT.md](./OUTPUT_FORMAT.md) | Pass blocks for Custom Instructions |

Per-phase distill blocks: add `PHASES.md` in target repo when running long programs (optional).
