# Roles — human, master, reviewer

**Index:** [prompts/README.md](./README.md)

```text
Human    → judgment, pause, ship calls
Master   → only agent you talk to; gates before run; compile briefs; synthesize back
Reviewer → Bugbot subagent; one task per spawn; no human I/O
```

| Role | Talks to human | Owns |
|------|----------------|------|
| **Human** | — | Product calls, skip, when to push |
| **Master** | yes | Memory, triage, implement, **block push until gates green**, brief reviewer |
| **Reviewer** | no | One verb on one diff — reason, don't rubber-stamp |
| **Greptile** (optional) | no | Post-push contract FIND — only when flow enabled |

**Master's main job:** don't let work **run** (push/ship) until tests, lint, Bugbot pass.

**Reviewer verbs**

| Verb | When | Key line in brief |
|------|------|-------------------|
| **FIND** | Phase gate | SCOPE + execution § phase |
| **VALIDATE** | Babysit pass 1 | `VALIDATE: <fn → failure path>` |
| **CLOSE** | Pass 2+ | Prior finding titles |

**Output format:** Accept XML, one line, or prose. Master reads **thinking export** when answer is thin ([OUTPUT_FORMAT](./OUTPUT_FORMAT.md)).

**Babysit pass 1 must be VALIDATE, not FIND.**

### Two Bugbot runtimes

| Channel | When | Tune via |
|---------|------|----------|
| **Hosted GitHub Bugbot** | Post-push on PR | `.cursor/BUGBOT.md` on `main` (append-only) |
| **Local Task subagent** | Pre-push gate | VERB + failure path + contract § in brief |

Subagent brief: ~6 lines. No chat history. See [PROMPTS.md](../PROMPTS.md).
