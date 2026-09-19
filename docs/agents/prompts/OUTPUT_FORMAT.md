# Bugbot output — context over format

**Index:** [prompts/README.md](./README.md)

**Principle:** Reasoning and trace quality matter more than response shape. Accept platform XML or one-line answers.

| Who | Owns what |
|-----|-----------|
| **Reviewer subagent** | Trace code; challenge mechanism; any output format |
| **Master** | Read thinking export; synthesize gate decision for human |

---

## Custom Instructions (paste to subagent)

**Keep brief:** `VERB` + `SCOPE` + failure path + contract §.

### FIND (phase gate)

```text
PASS: 1 (find)
Report actionable bugs introduced by the diff.
Trace code; cite file:line and mechanism.
Cite locked findings/execution IDs when applicable.
Out of scope: pre-existing issues unless this diff worsens them.
Any output format is fine.
```

### VALIDATE (babysit pass 1 — Greptile only)

```text
PASS: 1 (validate)
VALIDATE: <fn → failure path>
Prove or break the claim — trace the path; do not rubber-stamp.
External review thread: <verbatim or summary>
Any output format is fine.
```

### CLOSE (pass 2+)

```text
PASS: 2 (closure)
Prior findings: <list from master handoff>
Mark each CLOSED or STILL OPEN with evidence in your reasoning.
New actionable bugs only.
Any output format is fine.
```

---

## Master synthesis (after subagent returns)

| Section | Purpose |
|---------|---------|
| **Findings / closure** | What to fix or CLOSED items |
| **Deferred** | Traced but not filed — often only in thinking |
| **Scope note** | Phase § or external thread + path traced |

Gate stays green only when reasoning supports it.

---

## PR body (optional, helps reviewers)

```markdown
## Scope
<phase id> — <one line>

## Mechanism
<failure path or locked decision>

## Contract
<execution doc> § <phase>

## Test plan
- [ ] …

## Out of scope
…
```
