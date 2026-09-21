# saas-base

Open-source foundation for **small SaaS tools built around data pipelines, science workflows, and ML operations**.

`saas-base` is a real, runnable starting point: FastAPI + React + PostgreSQL + Keycloak, with multi-tenant workspaces, user management, billing hooks, and audit logging already wired. I use it to spin up focused products — starting with observatory data quality and pipeline workflows, then expanding to other science and ML verticals.

If you are a researcher or scientist with a **data-pipeline problem** — messy files that need to become inspectable objects, human-in-the-loop decisions, or reproducible processing steps — this is the shape of the toolset I am building for. [Get in touch](#contact).

---

## What is here now

| Layer | Tech | What it gives you |
|-------|------|-------------------|
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2.0 async, Pydantic v2 | Multi-env database routing, hand-written Alembic migrations, Keycloak JWT auth, cursor pagination, structured errors, Celery tasks |
| **Frontend** | React 19, TypeScript strict, Vite, Tailwind 4 | Workspace-scoped UI, admin user directory, settings, impersonation UI, EN + LV i18n |
| **Auth** | Keycloak 26 | JWT + JWKS caching, service-account helper, lifecycle actions (suspend, reactivate, delete) |
| **Billing** | Stripe (optional) | Checkout, Customer Portal, webhook scaffolding; disable with `STRIPE_ENABLED=false` |
| **Tests** | pytest + Vitest | Unit + HTTP smoke tests, mocked external services |

Not included: a specific domain. That is intentional — this repo is the chassis. Domain code (RFI flagging, observation quality gates, pipeline run desks, etc.) lives in product repos that consume this template.

---

## Why I am building this

Most science teams I talk to do not need a generic dashboard. They need a **decision loop**: raw data → validated objects → human review → action → audit trail. The pattern shows up in radio astronomy, radar, environmental monitoring, and any lab where a human still has to sign off on a file before downstream analysis.

`saas-base` captures the repeatable half of that loop so I can focus on the domain half:

- identity, workspaces, and permissions,
- audit logging and lifecycle,
- UI patterns for listing, inspecting, and acting on objects,
- deployment runbooks (Keycloak, Postgres, TLS, CI/CD),
- a clean starting point for science/ML product work.

---

## Quick start

You need Python 3.12, Node 24, a local PostgreSQL, and a Keycloak instance. Then:

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

See [docs/starter-pack/DEV_BOOTSTRAP.md](docs/starter-pack/DEV_BOOTSTRAP.md) and [docs/utils/KEYCLOAK_SETUP.md](docs/utils/KEYCLOAK_SETUP.md) for the full setup.

---

## Project status

This repository is the public home of the template. It is already used as the base for [`irbene-gate`](https://github.com/raimondskrauklis/irbene-gate), an observatory data-quality product built for the VIRAC team at Irbene. Future science/ML projects will fork from here.

Engineering history is preserved in `docs/platform-base/`, `docs/mini-saas/`, and `docs/saas-base/` as a transparent build log. These docs describe the evolution of the template, not a shipped product feature set.

---

## Contact

If you have a data-pipeline or ML problem that needs a small, opinionated SaaS tool — especially in science, engineering, or operations — I would like to hear about it.

- GitHub issues and discussions are open.
- Email: raimonds [at] gmail.com

---

## License

[MIT](LICENSE)
