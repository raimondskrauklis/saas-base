# saas-base

Engineering lab for **RF, space, and sensor data pipelines**.

This repo is both a **reusable SaaS shell** (FastAPI + React + PostgreSQL + Keycloak) and the starting point for real products built around messy signal data. The first concrete problem we are attacking is **RFI detection and filtering in radio-astronomy observations using machine learning**, with a parallel track on **scaling astronomical data processing with Dask on HPC** and comparing it to OpenMPI-style workflows.

If you work with noisy radar, RF, or sensor data and need a small, opinionated system to turn raw files into inspectable objects, decisions, and actions — [get in touch](#contact).

---

## Why this exists

Science teams often get stuck between two bad options:

1. **One-off notebooks and scripts** that nobody trusts in production.
2. **Heavy platforms** that force the science into their shape.

We are trying a third path: a **thin, domain-native layer** where data becomes objects a human can inspect, override, and act on, with an audit trail back to the source file. The focus is on the loop, not the dashboard:

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

For radio astronomy this means: an observation or scan is an object; suspected RFI is a claim attached to it; the operator accepts, quarantines, or escalates; every decision is logged. ML improves the claims; operators keep the final say.

This thinking is heavily inspired by how Palantir builds closed-loop data-to-action systems, but implemented here as lightweight, open-source components that stay close to the domain.

---

## What is here now

| Layer | Tech | Purpose |
|-------|------|---------|
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2.0 async, Pydantic v2, Celery | Multi-tenant API, hand-written Alembic migrations, Keycloak JWT auth, audit logging, billing hooks |
| **Frontend** | React 19, TypeScript strict, Vite, Tailwind 4 | Workspace UI, user directory, settings, admin tools, EN + LV i18n |
| **Auth** | Keycloak 26 | JWT + JWKS cache, service-account helper, user lifecycle |
| **Billing** | Stripe (optional) | Checkout / Portal scaffolding; disable with `STRIPE_ENABLED=false` |
| **Tests** | pytest + Vitest | Unit + HTTP smoke tests |

This is the chassis. Domain code for RFI, radar tracks, or sensor pipelines will live in product repos that consume this template.

---

## Active research directions

### 1. RFI detection and filtering for radio astronomy

**Problem:** Radio-astronomy observations are contaminated by human-made radio frequency interference. Separating real celestial signal from RFI is still often manual or based on brittle heuristics.

**Approach we are exploring:**
- Represent observations and scans as objects with lineage back to raw files.
- Train lightweight ML classifiers (and later segmentation models) to flag suspected RFI in time-frequency space.
- Surface claims in an operator UI with enough context to accept, quarantine, or override.
- Use every override as training signal.

**First consumer:** observatory data-quality workflows at Irbene / VIRAC.

### 2. Dask for HPC-scale astronomical data processing

**Problem:** Correlation and post-processing pipelines for large radio astronomy datasets are traditionally written with MPI. Dask offers a higher-level, Python-native alternative, but its fit for this workload is not proven.

**Approach we are exploring:**
- Port a representative processing step to Dask and benchmark it against an OpenMPI baseline on the same hardware.
- Measure scheduling overhead, I/O patterns, and memory usage for real-ish data shapes.
- Document when Dask wins, when MPI wins, and where a hybrid model makes sense.

---

## Who this is for

- **Radio astronomers and RF engineers** dealing with RFI, spectrograms, and observation quality gates.
- **Radar / remote-sensing teams** with messy sensor data that needs human-in-the-loop decisions.
- **Science software engineers** who want a small, auditable platform instead of a pile of scripts.
- **Anyone building Palantir-style data-to-action loops** without the platform lock-in.

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

Private engineering lab. The repo is intentionally not public yet while the first RFI prototype is being shaped. Engineering history is preserved in `docs/platform-base/`, `docs/mini-saas/`, and `docs/saas-base/` as a transparent build log.

---

## Contact

- Open a GitHub issue or discussion.
- Email: raimonds [at] createit.digital

If you are a scientist with messy RF, radar, or sensor data and want to collaborate or just describe your problem, reach out. We are building this in the open with real partners.

---

## License

[MIT](LICENSE)
