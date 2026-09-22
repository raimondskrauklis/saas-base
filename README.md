# saas-base

A multi-tenant SaaS foundation — **FastAPI + React + PostgreSQL + Keycloak** — built to grow domain tools for RF, space, and sensor data.

**Status:** Working generic foundation. We are exploring where it can add value for RF and radio-astronomy data problems; no domain code exists yet, and nothing is promised.

The idea: domain projects are forked from this repo, and whatever they need generically — pipeline plumbing, signal-processing steps, review loops — is added back here so the next project starts further ahead. The first domain we are looking at is radio-astronomy RFI work. Whether that leads anywhere depends on real data and real partners.

It is not an ML platform yet. It is the chassis.

## What works today

| Area | What is wired |
|------|---------------|
| **Tenancy** | Workspaces, members, invitations, roles, workspace lifecycle (export / delete) |
| **Identity** | Keycloak 26, JWT + JWKS cache, user provisioning, service-account helper |
| **Admin** | In-app user directory (list, inspect, suspend / reactivate), platform admin, impersonation |
| **Audit** | Audit log on workspace and platform actions |
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2.0 async, Pydantic v2, Celery tasks, hand-written Alembic migrations, cursor pagination, structured errors |
| **Frontend** | React 19, TypeScript strict, Vite, Tailwind 4; settings, dashboard, admin tools; EN + LV i18n; light / dark theme |
| **Tests** | pytest + Vitest; unit and HTTP smoke tests |
| **Ops** | Runbooks for Keycloak, Mailgun, object storage, Certbot, database connections; Docker deploy conventions |

Domain code for RFI flagging, observation quality gates, or radar tracks is not here yet. It arrives as real projects are built on top.

Revy reviews pull requests in this repository: [github.com/raimondskrauklis/revy](https://github.com/raimondskrauklis/revy).

## Research directions

The intent is a layer where messy signal data becomes inspectable objects, humans review and override, and every decision leaves an audit trail:

```
raw signal / dump / log
        │
        ▼
  parse + validate
        │
        ▼
  cleaned objects  ──►  model / rule flags an issue
        │                       │
        ▼                       ▼
  human review ────────►  action (keep, drop, reprocess, assign)
        │
        ▼
   audit trail + downstream output
```

Two directions are being explored on top of this foundation. Both are open questions, not plans.

### Direction 1 — RFI review for radio astronomy

Radio-astronomy observations are contaminated by human-made interference, and telling interference from a real spectral line is hard. Can a reproducible baseline plus a small model, with an astronomer reviewing the flags, make that step faster and traceable? The astronomer stays in charge of the decision.

Exploration only. No model, no data, no result yet.

### Direction 2 — Radio-astronomy pipelines on HPC

Post-correlation processing for radio astronomy is traditionally MPI-based; newer pipelines are being written in Dask. Can an existing reduction chain run end-to-end on an HPC system from containers, with each step measured in both frameworks, so the trade-offs are documented rather than assumed?

Research only. Nothing runs yet.

## Why the foundation comes first

Many science data projects fail in one of two places: one-off scripts that cannot be reviewed, rerun, or handed to a colleague; or heavy platforms that force the science into a pre-baked shape. This repo takes the middle path. Authentication, workspaces, audit logging, and deployment runbooks are boring but essential; getting them right early means the ML and signal-processing work sits on solid ground.

## Who this is for

- Radio astronomers and RF engineers dealing with RFI, spectrograms, and observation quality.
- Radar / remote-sensing teams with messy sensor data that needs human-in-the-loop decisions.
- Science software engineers who want a small, auditable platform instead of a pile of scripts.
- Anyone curious about data-to-action loops for physical-sensor data.

If your data looks like "files arrive, someone eyeballs them, someone decides, downstream analysis happens", this is the starting point.

## Quick start

```bash
# Backend
cd backend
pipenv install
pipenv run uvicorn app.main:app --reload

# Frontend
cd ../frontend
npm install
npm run dev
```

Full setup: [docs/starter-pack/DEV_BOOTSTRAP.md](docs/starter-pack/DEV_BOOTSTRAP.md). Operator runbooks: [docs/utils/](docs/utils/README.md).

## Corpus and planning

Sourced facts about the first domain we are studying — the Irbene radio telescopes and the LUMI supercomputer — live in [corpus/](corpus/irbene/README.md). Findings and plans for that work are in [docs/virac/](docs/virac/README.md). They describe what exists and what we are considering; they are not commitments.

## Contact

- Open a GitHub issue or discussion.
- Email: raimonds.krauklis [at] gmail.com

If you have messy RF, radar, or sensor data and want to describe your problem, or collaborate on a small prototype, reach out.

## License

[MIT](LICENSE)
