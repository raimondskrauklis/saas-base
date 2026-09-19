---
name: bootstrap-workflow
description: >-
  Install or upgrade agent-workflow in a target repo: detect stack and hosting,
  audit skills, adapt manifest, materialize .agent/, .cursor/, docs/agents/.
  Use when the user asks to bootstrap agent workflow, install the pack, audit
  skills, or port workflow to a target repo.
---

# Bootstrap workflow pack

**When:** user points at a target repo (or this pack as sibling) and asks to install, port, upgrade, or audit skills.

**Pack location (resolve in order):**

1. Path the user gave
2. Target `.agent/manifest.json` → `pack_source.path` (usually `../agent-workflow`)
3. Sibling `../agent-workflow` if it contains `skills.catalog.json`
4. `pack_source.url` — `git clone` / `git pull` if the user wants a remote (GitHub or other). **Not** Cursor Origin unless they ask.

**Rule:** Nothing runs from the pack directory. **Materialize** into the target repo.

**Catalog:** `skills.catalog.json`. **Audit:** `patterns/skills-audit.md`. **Adapt:** `patterns/ADAPT.md`.

The agent in the target repo must **reason**. Different stack, no GitHub, different test runner — fill the manifest from what exists. Do not copy another product's `.cursorrules`.

---

## 0. Sync the pack

If the pack path is a git repo and has a remote:

```bash
git -C <pack_path> pull --ff-only
```

If there is no remote, use the folder as-is. Never force-push or rewrite pack history.

---

## 1. Discover target repo

1. Confirm target repo root (not the pack root, unless the user is editing the pack itself).
2. Scan: `AGENTS.md`, `.cursor/skills/`, `.cursor/mcp.json`, `.agent/`, `.revy/`, `docs/`, git remotes, lockfiles (`Pipfile`, `package.json`, `go.mod`, `pyproject.toml`).
3. Read pack `skills.catalog.json`, `project.manifest.template.json`, `patterns/ADAPT.md`, `patterns/review-context.schema.json`.

Print a short discovery note: layout, hosting, test runner.

---

## 2. Write `.agent/manifest.json`

Adapt the template. Fill `hosting`, `test_commands`, `backend_dir` / `frontend_dir`, `default_scope` from [ADAPT.md](../../patterns/ADAPT.md).

Set `pack_source.path` to the pack used this run.

Do not add unused integrations. `integrations.revy` only for the Revy product or when the user says Revy runs on this repo's PRs.

Write `.agent/flows/*.json` from pack templates for **installed** flows only. Enable `revy-babysit` only when Revy applies.

---

## 3. Skill audit (required)

Follow `patterns/skills-audit.md`.

1. Load pack catalog.
2. For each skill: **install** | **upgrade** | **keep** | **skip** | **remove**.
3. Print compact table **before** copying files.

**Default install:** `bootstrap-workflow`, `phase-execution`, `ship-changes`, `chunk-execution`.

**Planning** — when `docs/` has program artifacts or the user does phased work.

**Optional:** Revy babysit, Sentry, docs export — per audit rules.

4. Copy selected skills from `templates/.cursor/skills/<id>/` → target `.cursor/skills/<id>/`.
   - `copy_scripts: true` — copy the full folder.
   - **Upgrade** core/meta/planning from pack templates (pack is authoritative).
   - **Keep** skills not in the catalog (product-local).
5. Copy catalog → `.agent/skills.catalog.json`; set `skills.installed`.

---

## 4. Review context SSOT

Per `patterns/ADAPT.md` § Review context SSOT.

Idle default: `active_program: null`. Do not invent a fake program.

Set `programs[].scope` from execution docs or manifest `default_scope`.

---

## 5. `.cursor/BUGBOT.md`

From `patterns/BUGBOT.md.template` — paths relative to `.cursor/`. If no active program, a short idle stub is enough.

---

## 6. `docs/agents/`

Copy from `templates/docs/agents/` + `templates/docs/utils/CURSOR_AGENT_WORKFLOW.md` if missing. Do not overwrite consumer dogfood notes.

---

## 7. Merge `AGENTS.md`

- No `AGENTS.md` → copy `templates/AGENTS.md` then fill product name/stack.
- Existing → merge `templates/AGENTS.workflow.snippet.md`. List **installed** skills only.

---

## 8. Verify

```text
[ ] .agent/manifest.json + skills.catalog.json (pack_version matches pack)
[ ] pack_source.path is correct
[ ] hosting.kind matches remotes + user
[ ] test_commands are real for this repo
[ ] Skill audit table; skills.installed matches .cursor/skills/ (plus product-local)
[ ] Review context SSOT per hosting
[ ] AGENTS.md skills table matches installed set
```

Report: audit table, files created, hosting, gaps.

---

## Upgrade / re-audit only

User says "audit skills" or "upgrade workflow pack":

1. Sync pack (step 0).
2. Skill audit only — compare installed vs catalog + repo signals.
3. Upgrade outdated core skills; add missing optionals; do not delete product-local skills.
4. Stamp `pack_version` from the pack catalog.

---

## Not in scope

- Product SaaS scaffold
- CI/CD unless the user asks
- Copying another product's domain rules
- Cursor Origin unless the user explicitly asks
