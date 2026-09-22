# docs/virac/RFI_LUMI_GENERAL_PLAN.md

# RFI mitigation and Dask-on-HPC on LUMI — general plan

**Status:** draft; phases fixed, numbers calibrate in P1.
**Baseline:** [`RFI_LUMI_FINDINGS.md`](RFI_LUMI_FINDINGS.md) (problem, data, compute, transfer) and [`VIRAC_COLLABORATION_FINDINGS.md`](VIRAC_COLLABORATION_FINDINGS.md) (tracks, platform reuse, Q1–Q9).
**Locked from findings:** ISBI post-correlation C-band visibilities are the first ML product; AOFlagger + SSA are the baselines; maser-safety FPR is the first metric; LUMI-O is the ingress/egress border; everything runs in containers; the Dask/MPI benchmark uses one `cray-python` module on identical LUMI-C nodes; the correlator is out of scope.
**Open (calibration only):** grant details (Q-A3), single-dish time-resolved availability (Q-A1), session sizes (Q-A2).

## Cross-cutting — shipped in every phase

- **Lineage.** Every mask, model, metric and benchmark row carries data version, code commit, container digest, LUMI job ID. Nothing without a provenance record is reported.
- **Coverage and exclusion surfacing.** Each report states which sessions, bands, sources were in and which were excluded, and why.
- **Visualisation.** Time–frequency plots with baseline vs model masks and the protected line marked; scaling curves for Track B. Committed as artifacts, not screenshots.
- **Reproducibility across sites.** Harness runs on LUMI, RTU Rudens, and VIRAC's cluster from the same container and config; LUMI-specific settings live in one Slurm profile.
- **Compute burn tracking.** `lumi-allocations` snapshot in every phase gate; cumulative GPU-h against the month-6 target (≥ 40 %).
- **Tests.** Unit tests for readers, packers, metrics and the harness; a smoke test that runs end-to-end on a 1-session fixture.
- **i18n.** Any UI touched in saas-base (review loop) ships EN + LV.

## P0 — LUMI foundations and data border

**Goal.** A working, repeatable path from a Latvian host to a LUMI-G job with zero manual steps in between.
**Scope.** In: LUMI project setup (`lumi-allocations`, quotas, LUMI-O keys, buckets), `rclone` push from Latvia and pull on LUMI, container build (`cotainr` on PyTorch ROCm + AOFlagger CPU container), squashed venv, Slurm job templates for `small-g`, `small`, `standard`, `largemem`, MIOpen/NCCL/`hsn` settings, Lustre layout for shards, Latvian backup location. Out: any science, any model.
**Deliverables.** `lumi/` directory with containers, job templates, `rclone` profiles, a `make smoke` that moves a fixture LUMI-O → scratch → GPU job → LUMI-O and back; a measured throughput table (Latvia → LUMI-O, LUMI-O → scratch, scratch → flash); grant facts filled in (Q-A3, Q-A5, Q-A8 resolved).
**Depends on.** Nothing.

## P1 — First real sample and packer

**Goal.** One IVARS session on LUMI in an ML-ready layout, with any existing flags preserved.
**Scope.** In: SFXC output reader (format per Q-A2), per-session HDF5/Zarr packer (time × chan × pol, 256 MB+ chunks) built and run in Latvia, checksum manifest, W3OH / G111.542+0.776 scans tagged as the safety set, public LOFAR (MES22) and cross-telescope sets staged alongside, read-throughput calibration on `/flash` vs `/scratch`. Out: single-dish data (until Q-A1), baseband.
**Deliverables.** `virac-io` package (reader, packer, manifest); one session and the public sets on LUMI-O and scratch; data card with sizes replacing §3 estimates; chunk-size and stripe recommendation.
**Depends on.** P0.

## P2 — Baselines on LUMI

**Goal.** AOFlagger and SSA masks for every staged session, reproducible from one command, with the maser channels protected.
**Scope.** In: AOFlagger Python API on NumPy planes with a spectral-line-safe Lua strategy (protected channel range, Apertif-style sensitivities); SSA/KLT implementation on CPU and on MI250X (`torch.linalg.svd`), timing both; higher-order-statistics baseline only if time-resolved single-dish data exists; metric library (precision / recall / F1 / AUPRC on cells, maser FPR, post-subtraction line SNR); mask storage next to data with algorithm + version. Out: any learned model.
**Deliverables.** `rfi-baselines` package; masks for all sessions; a baseline report with the maser-safety numbers; first GPU-hours spent (SSA sweep over window sizes).
**Depends on.** P1.

## P3 — Weak-label model and honest evaluation

**Goal.** A U-Net-class segmentation model trained on AOFlagger weak labels, evaluated on whatever strong labels exist, reported next to both baselines.
**Scope.** In: PyTorch ROCm training on `small-g` (1–8 GCDs), Dice loss, AOFlagger pre-train then fine-tune, seeds and sweeps as job arrays, cross-telescope transfer test (train LOFAR/HERA/NSRT → test Irbene), model cards with lineage, masks exported to LUMI-O. Strong labels come from the saas-base review loop (companion Track A); until they exist, evaluation is on public expert sets plus the maser-safety set only, stated as such. Out: transformer models; anything real-time.
**Deliverables.** `rfi-models` package; trained checkpoints; evaluation report with baseline columns; GPU burn ≥ 40 % of grant by end of this phase.
**Depends on.** P2; strong labels from companion Track A improve but do not block it.

## P4 — Dask vs MPI benchmark on LUMI-C

**Goal.** Per-step, same-node, equivalence-checked comparison of Dask and mpi4py on VIRAC-chosen post-correlation steps, with a written recommendation.
**Scope.** In: step selection with VIRAC (bandpass/gain application, spectral-line extraction + time-series binning, one communication-heavy step); reference implementation and equivalence test; MPI variant on Cray MPICH; Dask variant via `dask-jobqueue` / `dask-mpi` on `hsn0`; strong and weak scaling 1–16 nodes on `standard`; same harness re-run on VIRAC's cluster and RTU. Out: correlator; GPU variants of the steps unless trivially available.
**Deliverables.** `hpc-bench` harness; scaling curves and memory profiles; recommendation memo (where Dask fits, where MPI stays, crossover on LUMI-C and on VIRAC hardware).
**Depends on.** P1 (data), P0 (templates). Independent of P2–P3; can run in parallel once P1 lands.

## P5 — Second model wave and surplus-compute experiments

**Goal.** Spend the remaining grant on the experiments that are usually skipped, and lock the final model comparison.
**Scope.** In: Swin-UNETR / WF-SwinUnet on the same splits; self-supervised pre-training on the full correlated archive if staged; ablations (with/without protected channels, with/without SSA pre-subtraction); single-dish time-resolved data if Q-A1 was "yes"; final evaluation on strong labels from the review loop. Out: new data sources.
**Deliverables.** Final model report; recommended production configuration (baseline + model + thresholds) for VIRAC's Dask pipeline; archived checkpoints and masks on LUMI-O and in Latvia.
**Depends on.** P3; strong labels from companion Track A.

## P6 — Hand-over and platform feedback

**Goal.** Everything reproducible without LUMI and without us; generic pieces fed back to saas-base.
**Scope.** In: run the full harness on RTU and VIRAC's cluster from the same containers; final data and artifact copy to Latvia before project end; write-ups (methods, benchmark, data card); saas-base contributions — HPC job-submission pattern, artifact-store abstraction for masks, reader-plugin interface — only where P0–P5 proved them generic. Out: new science.
**Deliverables.** Reproduction log from two non-LUMI sites; archived project; saas-base PRs; post-finish gap pass.
**Depends on.** P4, P5.

## Sequencing

P0 → P1 → {P2 → P3 → P5} ∥ {P4} → P6. P4 starts as soon as P1 lands and runs on LUMI-C while P2–P3 use LUMI-G; this is also what keeps both grants burning early.

## Remaining open item

Grant specifics (Q-A3: LUMI-C amount, TB-hours, project type, dates) — read from `lumi-allocations` in P0; they only change sizing, not phases.

**Next step:** `create-execution-plan` for P0 once Q-A3 is read and the VIRAC meeting answers Q-A1, Q-A2, Q-A9.
