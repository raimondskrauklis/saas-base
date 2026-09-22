# docs/virac/VIRAC_COLLABORATION_FINDINGS.md

# VIRAC collaboration — findings

**Status:** draft, pre-meeting. Baseline for a general plan once the discovery meeting resolves the open decisions below.
**Scope:** two ideas VIRAC raised — (1) ML-based RFI removal / filtering from radio-astronomy observation data, (2) a Dask study parallelising observation processing on HPC against standard / OpenMPI solutions — and what saas-base can offer as the foundation for either.
**Grounding:** VIRAC facts are cited by key into [`corpus/irbene/facts.md`](../../corpus/irbene/facts.md) / [`sources.md`](../../corpus/irbene/sources.md). Platform facts are cited by path into this repo. Anything not so marked is an assumption.

## Build principles

- **Real data only.** No synthetic RFI, no simulated visibilities as a substitute for a VIRAC sample. Synthetic data may augment, never replace, the test set.
- **Never mislead.** Every model result is reported next to AOFlagger and VIRAC's SSA on the same sample, with the label provenance stated. If a metric cannot be computed, it is N/A, not estimated.
- **Science-safe first.** A false positive on a maser line is worse than a missed RFI sample. Source-aware evaluation is a first-class metric, not an afterthought.
- **Lineage.** Every flag, override and model version is traceable to who / what / when. This is what the platform is for.
- **No corner-cutting in shared infra.** Whatever the domain layer needs generically (job runner, artifact store, review loop) is built in saas-base, not forked.
- **They own correctness.** VIRAC scientists are the reviewers of physics; we are the reviewers of engineering.

## Terminology

Domain terms: [`corpus/irbene/glossary.md`](../../corpus/irbene/glossary.md). Terms introduced here:

| Term | Meaning |
|:---|:---|
| Sample | One representative observation VIRAC hands over, in its native format, with any existing flags |
| Baseline | AOFlagger (SumThreshold) and VIRAC's SSA run on the sample; the reference every model is compared to |
| Weak labels | Flags produced by a baseline algorithm |
| Strong labels | Flags confirmed or overridden by a VIRAC scientist in the review UI |
| Issue | The platform object representing one flagged region (time × frequency × baseline/polarisation) awaiting a human decision |
| Track A / Track B | The RFI review loop / VIRAC's pipeline end-to-end on HPC (Dask vs MPI answered per step), respectively |

## What exists vs genuinely new

### At VIRAC (verified, public)

| Exists | Source | Consequence for us |
|:---|:---|:---|
| SFXC (DiFX 2.8.1) MPI correlator; AIPS + CASA + ParselTongue reduction pipeline | G25 | Correlation is not ours. A flagger plugs in post-correlation, or on single-dish dynamic spectra. |
| A Dask-based pipeline is *being built* covering calibration, RFI mitigation, spectral-line extraction, time-series | G25 | Track B is not "introduce Dask". It is "make the pipeline they already chose run end-to-end on HPC, and measure Dask vs MPI per step while doing it". |
| SSA named as the RFI decomposition method | G25 | SSA is a baseline, not a competitor. Our ML result must sit next to it. |
| GPU correlator under RADIOBLOCKS (to Feb 2027), AARTFAAC-derived | G25, RB | Off-limits scope. Do not propose correlator work. |
| Modernisation phase 4: HPC + GPU nodes intended for ML, data streaming | M4 | Training compute may exist on their side; timing unknown. |
| Real-time RFI detection tool for LOFAR LV614 (bachelor thesis) | LRFI | Precedent and appetite; different instrument, different data. |
| FlexBuff 288 + 64 TB, 2 PB tape; VDIF baseband | G25 | Data is large. A sample must be scoped by session, band, and product level. |
| IVARS: 154 processed interferometric sessions 2024–2025; single-dish maser archive 2017–2022, 42 sources | G25, AB23 | A real archive with known sources exists. Candidate ground truth for the maser-safety set. |

### In saas-base (verified, this repo)

| Exists | Path | Reuse note |
|:---|:---|:---|
| Multi-tenant workspaces, members, invitations, roles | `backend/app/models/workspaces.py`, `workspace_memberships.py`, `invitations.py` | A VIRAC workspace is a row, not a deployment. |
| Keycloak JWT auth, JWKS cache, provisioning | `backend/app/core/auth.py`, `services/keycloak_provisioning.py` | Ready. |
| Audit log | `backend/app/models/audit_log.py` (`AuditLogORM`), `services/audit_service.py` | Records who/what/when; flag decisions should write here. |
| Celery + Redis workers | `backend/app/core/config.py:95-201`, `backend/app/workers/` | Job runner for ingest and baseline runs. Not an HPC scheduler — see Track B. |
| Example tenant model with cursor pagination and filter builder | `backend/app/models/items.py` (`ItemORM`), `backend/app/services/filter_query_builder.py` | Template for `Observation`, `Scan`, `Issue` ORMs. |
| Data export job pattern | `backend/app/models/data_export_job.py` | Template for long-running artifact-producing jobs. |
| Object storage runbook | `docs/utils/SPACES_STORAGE.md` | Where samples and flag artifacts would live. |
| Deploy: nginx, Keycloak, env examples | `deploy/` | Dedicated-droplet pattern already exercised (Irbene Gate runbook, internal). |

### Genuinely new (nothing in the repo today)

- Any radio-astronomy data reader (FITS-IDI, Measurement Set, HDF5 dynamic spectra, VDIF).
- Any ML pipeline plumbing: dataset versioning, training job, model registry, evaluation report.
- Any Dask integration, `dask-jobqueue`, or SLURM awareness.
- Domain objects: Observation / Scan / Issue and the review UI.
- A baseline harness that runs AOFlagger and SSA and stores masks.

**Trap:** `ItemORM` is an example model, not a base class to subclass for domain objects. Copy the pattern (workspace FK, soft delete, partial index) — do not couple to it.

## Catalog — tracks

### Track A — RFI review loop with an ML baseline

**Rationale.** Literature 2022–2026 shows segmentation models (U-Net, Swin-UNETR, WF-SwinUnet) beat SumThreshold on expert-labelled test sets from the same instrument, but gains are modest and data-specific (MES22, CMP24, SWIN24, WF25). The consistent lesson is that *labels from the target instrument* decide the result. The scarce resource is therefore scientist time spent confirming or overriding flags — which is precisely what a review loop with audit trail captures as a by-product of normal use.

**Method.**

1. Ingest one VIRAC sample into a workspace; expose Observation → Scan → Issue with their column names.
2. Baseline harness: AOFlagger and SSA on the sample; masks stored as Issue objects with algorithm and version.
3. Review UI: scientist accepts / overrides / annotates. Every action → audit log. Overrides accumulate as strong labels.
4. First model: U-Net-class segmentation trained on weak labels (AOFlagger), evaluated on strong labels, reported next to both baselines.
5. Maser-safety metric: false-positive rate on a "must never flag" source set VIRAC names (candidates: W3OH, G111.542+0.776 — G25).

**Verification gate.** A VIRAC scientist has reviewed ≥ 1 real session end-to-end in the UI; baseline masks and ≥ 1 model result are on the same page with label provenance shown; maser-safety FPR is reported.

### Track B — VIRAC's pipeline end-to-end on HPC (Dask vs MPI answered by building it)

**Rationale.** VIRAC's own framing is "Dask vs standard / OpenMPI". Read behind it: they have already chosen Dask for the new pipeline (G25) while everything they trust — SFXC — is MPI. What they need is evidence that the choice holds on their own cluster and on an HPC before RADIOBLOCKS deliverables and theses are built on it. A benchmark table does not give them that; their pipeline running end-to-end on LUMI and on their 30 nodes with a known cost model does. The Dask-vs-MPI comparison falls out of building it properly: per step, same inputs, equivalence checked, both variants kept in the harness (AFR25a, AFR25b, SFXC).

**Method.**

1. Obtain the current pipeline stages (ParselTongue / CASA / early Dask) and the SFXC output for a set of IVARS sessions.
2. Make each stage a containerised, chunk-aware step with a reference implementation and an equivalence test; MPI variant where the step is communication-bound, Dask variant everywhere it is array-shaped.
3. Run the whole chain on LUMI-C at scale and on VIRAC's cluster from the same containers; measure wall time, memory, strong and weak scaling per step.
4. Written recommendation: where Dask fits, where MPI stays, the crossover on both machines — plus the cost model per session on LUMI.

**Verification gate.** The chain runs on VIRAC's cluster by a VIRAC engineer from the committed harness on one session; scaling curves reproduced by them; recommendation reviewed.

**Product.** A pipeline they run on Monday, with a benchmark memo as its by-product. Platform contribution to saas-base: HPC job-submission pattern and step/artifact lineage, only where proven generic. Complementary work enabled by having the archive next to LUMI compute is in [`COMPLEMENTARY_PROBLEMS_FINDINGS.md`](COMPLEMENTARY_PROBLEMS_FINDINGS.md).

### Sequencing

Track A first unless VIRAC says the Dask pipeline is the urgent fire. A yields something used within weeks and generates the labels the ML hypothesis needs; B yields the pipeline the archive re-processing in the complementary findings depends on. Both can run with two named contacts.

## Advice / options

| Option | Recommendation | Why |
|:---|:---|:---|
| Track A as described | **Adopt** | Uses what saas-base has; produces owned labels; honest ML answer |
| Track B as described | **Adopt, second** | Answers their stated question by shipping the pipeline, not a PDF; the benchmark is a by-product |
| ML model bake-off without the review loop | **Reject** | No strong labels → results not trustworthy on their data |
| Correlator or pre-correlation (baseband) flagging | **Reject** | RADIOBLOCKS scope; communication-bound; not ours |
| Real-time flagging in the acquisition chain | **Defer** | Only after batch results are proven; PAT26 shows it is feasible later |
| Start from the LOFAR LV614 tool | **Defer** | Different instrument and data; revisit if VIRAC wants LOFAR in scope |

## External research / patterns

| Pattern | Source | Adopt / defer / reject |
|:---|:---|:---|
| Train on AOFlagger weak labels, test on expert strong labels | MES22, CMP24 | **Adopt** — matches the review-loop design |
| Dice loss for class imbalance; AOFlagger-pretrain then fine-tune | CMP24 | **Adopt** for the first model |
| Hierarchical vision transformer (Swin-UNETR) | SWIN24, WF25 | **Defer** — second model, after U-Net baseline |
| 1-D low-latency model for pulsar search | PAT26 | **Defer** — not their science driver |
| Dask-MS / QuartiCal task-granularity findings | AFR25a, AFR25b | **Adopt** as the design reference for Track B chunking |
| SSA as subtraction rather than flagging | G25 | **Respect** — different goal; report both flag-quality and post-subtraction SNR |

## Data scope & exclusions

- **In scope (first sample):** one band, one receiver, one product level, chosen by VIRAC. Preference: C-band (4.5–8.8 GHz) because it is the interferometer's main band and where IVARS/STEF data live (G25). Assumption until they confirm.
- **Product level:** post-correlation visibilities or single-dish dynamic spectra. Not baseband. Ask which hurts more.
- **Excluded:** VDIF baseband; LOFAR LV614 data; GNSS / FSR campaigns; anything under embargo.
- **Compute-time vs filter-late:** baseline masks are computed once at ingest and stored; model masks are versioned artifacts; review decisions filter late in the UI.
- **Exit:** data may be deleted on request; workspace export / delete already exists (`services/data_export.py`, `services/workspaces.py`).

## Edge cases

- **Maser lines flagged as RFI.** Named as a first-class metric above. Also the reason a pure F1-on-RFI report is insufficient.
- **Flags already exist.** If CASA flag tables or AOFlagger masks are in the archive, they are weak labels for free — and the first test of our ingest.
- **Sample too large to leave the building.** Fall back to running the harness on their side; the platform then ingests masks, not raw data.
- **Two implementations of the "same" step disagree.** Track B must fix numerical equivalence before timing anything.
- **Model generalisation.** A C-band RT-32 model is not an L-band or RT-16 model. State the scope on every report.
- **Scientist time.** If no one can review weekly, Track A stalls at step 2. Ask before promising.

## Decisions registry

| Q# | Question | Status | Resolution |
|:---|:---|:---|:---|
| Q1 | Which track first? | open | Proposed A; they may override |
| Q2 | Which band / receiver / product level for the first sample? | open | Proposed C-band post-correlation |
| Q3 | Where does a flagger plug in — Dask task, CASA flag table, file? | open | Ask |
| Q4 | Who at VIRAC reviews weekly? | open | Need one name |
| Q5 | Can code be public? Can data? | open | Ask |
| Q6 | Baseline set agreed before any model trains? | open | Propose AOFlagger + SSA |
| Q7 | Compute for training: their phase-4 GPUs, ours, or cloud? | open | Ask timeline |
| Q8 | Funding shape: student project, grant WP, paid pilot? | open | Ask |
| Q9 | Where do these docs live — saas-base (public), a new domain repo, or internal? | resolved | Corpus public in `corpus/irbene/`; findings and plans public in `docs/virac/`; meeting notes in `internal-docs/virac/` (gitignored) |

## Parking lot

- **Phase-0 prerequisites (shared infra):** artifact store abstraction for large binary masks; a generic long-running-job model beyond `DataExportJobORM`; a reader-plugin interface for scientific file formats.
- Whether Irbene Gate (internal) becomes the deployment target or a fresh workspace on an existing instance.
- A public-facing write-up of the maser-safety metric, if the results are worth it.

## Devil's advocate

- **They do not need us.** They have Dask, SSA, a correlator programme, and a thesis-level RFI tool. What we add is engineering throughput and a product loop, not physics. If they want a research student, we are the wrong shape.
- **ML may not beat SSA on their data.** The literature gains are small and instrument-specific. The review loop must be valuable even if the model result is "no better" — that is why labels and audit are the deliverable, not the model.
- **We will misread the physics.** Mitigation is a named reviewer, not confidence.
- **A benchmark can be rigged either way.** Track B is only worth doing if they own the step selection and rerun the harness themselves.

## Experiment / verification

| Output | Pass | Fail |
|:---|:---|:---|
| Ingest | One VIRAC session visible as Observation → Scan → Issue with native column names | Any field imputed or renamed without their say |
| Baseline harness | AOFlagger and SSA masks stored with algorithm + version; reproducible from CLI | Masks differ between runs on identical input |
| Review loop | ≥ 1 scientist session; every decision in audit log | Decisions lost or unattributed |
| First model | Precision / recall / F1 / AUPRC on strong labels, next to both baselines; maser FPR reported | Reported only on weak labels, or without baselines |
| Track B harness | Chain runs on VIRAC's cluster from the committed harness; scaling curves reproduced there | Results only from our machine; a report without a runnable pipeline |

## References

- Corpus: [`corpus/irbene/facts.md`](../../corpus/irbene/facts.md), [`sources.md`](../../corpus/irbene/sources.md), [`glossary.md`](../../corpus/irbene/glossary.md)
- Platform: `backend/app/models/`, `backend/app/services/`, `backend/app/workers/`, `docs/utils/SPACES_STORAGE.md`
- Meeting agenda and discovery questions: `internal-docs/virac/MEETING_PREP.md` (contributors with access)
