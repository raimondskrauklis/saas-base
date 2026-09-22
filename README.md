# saas-base

A small, opinionated **foundation for SaaS tools around RF, space, and sensor data**.

Right now this is a working generic shell: **FastAPI + React + PostgreSQL + Keycloak**, with multi-tenant workspaces, user management, and audit logging already wired. It is not an ML platform yet. It is the chassis we will grow into real products — starting with radio-astronomy RFI work and later with radar / remote-sensing pipelines.

If you are a researcher or engineer with messy RF, radar, or sensor data and want to shape a lightweight tool around it, [get in touch](#contact).

---

## What this is today

| Layer | Tech | Purpose |
|-------|------|---------|
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2.0 async, Pydantic v2 | Multi-env database routing, hand-written Alembic migrations, Keycloak JWT auth, cursor pagination, structured errors, Celery tasks |
| **Frontend** | React 19, TypeScript strict, Vite, Tailwind 4 | Workspace UI, user directory, settings, admin tools, EN + LV i18n |
| **Auth** | Keycloak 26 | JWT + JWKS cache, service-account helper, user lifecycle |
| **Tests** | pytest + Vitest | Unit + HTTP smoke tests |

That is the starting point. Domain code for RFI flagging, observation quality gates, or radar tracks will be added as we build real projects on top.

The engineering approach here is influenced by [Revy](https://github.com/raimondskrauklis/revy) — our AI-assisted code-review tool — which we use as a reviewer on this repo. Both repositories share the same discipline: small, transparent, iterated in the open.

---

## Where we are heading

We want to turn this shell into a **thin, domain-native layer** where messy signal data becomes inspectable objects, humans can review and override, and every decision leaves an audit trail. The loop looks like this:

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

Two concrete directions we want to explore:

### 1. RFI detection for radio astronomy

Radio-astronomy observations are often contaminated by human-made RF interference. We want to learn whether lightweight ML classifiers, trained on operator-labelled spectrograms, can flag suspect regions and hand them to a human for the final keep/quarantine decision. The goal is not to replace the astronomer — it is to make the review loop faster and reproducible.

This is **exploration**, not a shipped product.

### 2. Scalable processing with Dask on HPC

Correlation and post-processing for large radio astronomy datasets are traditionally MPI-based. We want to experiment with Dask for the same workloads: port a representative step, benchmark against OpenMPI, and document where each approach makes sense.

Again, this is research, not a finished pipeline.

---

## Why build the foundation first

Most science data projects we see fail in one of two places:

1. **One-off scripts** that cannot be reviewed, rerun, or handed to a colleague.
2. **Heavy platforms** that force the science into a pre-baked shape.

We are trying a middle path: a small, auditable foundation that grows with the domain. Authentication, workspaces, audit logging, and deployment runbooks are boring but essential; getting them right early means the interesting ML and signal-processing work sits on solid ground.

The design follows the same closed-loop idea: data becomes objects, objects become decisions, and every decision is auditable — but built as open, lightweight components that stay close to the science.

---

## Who this is for

- **Radio astronomers and RF engineers** dealing with RFI, spectrograms, and observation quality.
- **Radar / remote-sensing teams** with messy sensor data that needs human-in-the-loop decisions.
- **Science software engineers** who want a small, auditable platform instead of a pile of scripts.
- **Anyone curious about data-to-action loops** for physical-sensor data.

If your data looks like “files arrive, someone eyeballs them, someone decides, downstream analysis happens,” we should talk.

---

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

Full setup: [docs/starter-pack/DEV_BOOTSTRAP.md](docs/starter-pack/DEV_BOOTSTRAP.md) and [docs/utils/KEYCLOAK_SETUP.md](docs/utils/KEYCLOAK_SETUP.md).

---

## Project status

Private engineering lab. The first RFI prototype is still being shaped. Engineering history is preserved in `docs/platform-base/`, `docs/mini-saas/`, and `docs/saas-base/` as a transparent build log.

We also dogfood this repo with [Revy](https://github.com/raimondskrauklis/revy), our AI-assisted code reviewer. If you are interested in how we review code, take a look there too.

---

## Contact

- Open a GitHub issue or discussion.
- Email: raimonds [at] createit.digital

If you have messy RF, radar, or sensor data and want to describe your problem — or even collaborate on a small prototype — reach out. We are building this in the open with real partners.

---

## License

[MIT](LICENSE)
