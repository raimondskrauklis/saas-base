# saas-base

A multi-tenant SaaS foundation — **FastAPI + React + PostgreSQL + Keycloak** — built to grow domain tools for RF, space, and sensor data.

**Status:** Active foundation; domain workflows (RFI detection, HPC processing) are exploratory and not yet in code.

Domain projects are forked from this repo. Whatever they need generically — ML pipeline plumbing, signal-processing steps, review loops — is added back here so the next project starts further ahead. The first domain target is radio-astronomy RFI work; radar and remote-sensing pipelines come later.

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

Two hypotheses are being explored on top of this foundation.

### Hypothesis 1 — RFI detection for radio astronomy

Radio-astronomy observations are often contaminated by human-made RF interference. Can lightweight ML classifiers, trained on operator-labelled spectrograms, flag suspect regions and hand them to a human for the final keep / quarantine decision? The goal is not to replace the astronomer; it is to make the review loop faster and reproducible.

This is exploration, not a shipped product.

### Hypothesis 2 — Scalable processing with Dask on HPC

Correlation and post-processing for large radio-astronomy datasets are traditionally MPI-based. Can Dask handle the same workloads? Port one representative step, benchmark against OpenMPI, document where each approach makes sense.

This is research, not a finished pipeline.

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

## Contact

- Open a GitHub issue or discussion.
- Email: raimonds.krauklis [at] gmail.com

If you have messy RF, radar, or sensor data and want to describe your problem, or collaborate on a small prototype, reach out.

## License

[MIT](LICENSE)
