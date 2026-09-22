# docs/virac/RFI_LUMI_FINDINGS.md

# RFI mitigation and Dask-on-HPC with VIRAC data on LUMI — findings

**Status:** draft, research pass 1 of 2. Baseline for `RFI_LUMI_GENERAL_PLAN.md`. Items marked *verify* are re-fetched in pass 2 (see §13 Research backlog).
**Scope:** the problem itself, not the collaboration shape — what the data is, how heavy it is, what breaks, what compute and network we have, and how to move VIRAC data to LUMI and use LUMI-G / LUMI-C well within a 4 500 GPU-hour grant.
**Companion:** [`VIRAC_COLLABORATION_FINDINGS.md`](VIRAC_COLLABORATION_FINDINGS.md) (tracks, decisions Q1–Q9, platform reuse). This doc does not repeat it.
**Grounding:** VIRAC facts by key into [`corpus/irbene/facts.md`](../../corpus/irbene/facts.md) / [`sources.md`](../../corpus/irbene/sources.md). LUMI and network facts by key into `sources.md` §"Compute and network infrastructure". Numbers without a key are estimates and say so.

## 1. Build principles (additions to the companion doc)

- **Burn compute on purpose.** LUMI cuts unused allocations. A plan that "saves" GPU-hours for later loses them. Large, honest experiments early — sweeps, cross-telescope generalisation, ablations — are the correct use, not waste.
- **Stage, don't stream.** Compute nodes have no local disk and (verify) no general outbound internet. Everything a job needs is on `/scratch` or `/flash` before `sbatch`.
- **Few big files.** Lustre punishes many small files; quotas are in file counts as well as TB. VIRAC's per-scan ASCII files are packed into HDF5 / Zarr before they leave Latvia.
- **Object storage is the border.** LUMI-O (S3) is the hand-off point between VIRAC, us, and LUMI compute. It survives LUMI downtimes, is reachable without an SSH account, and is the cheapest tier.
- **Same node, same data, or no benchmark.** Dask vs MPI numbers are only reported when both ran on identical LUMI-C nodes on identical inputs with numerical equivalence checked first.
- **AMD first, CUDA as control.** Everything targets ROCm on MI250X. RTU's A100 / L40S nodes are the CUDA control and the fallback for CUDA-only code (the VIRAC correlator).

## 2. The problem, precisely

Two instruments, two data shapes, one question: *which time–frequency cells are interference, without ever flagging the maser line.*

| Data product | Shape | Where RFI shows | ML-ready today? |
|:---|:---|:---|:---|
| Single-dish maser spectra (USRP X300 → MDPS) | Per scan: four ~15 s stages (`r0 r1 s0 s1`), each frequency × 2 pol; 4 096 points; many scans per observation → one HDF5 | As narrow spikes or broadband lifts; native time resolution ~15 s per stage, tens of stages per observation | **Weakly** — a coarse dynamic spectrum (~15 s × 4 096 ch) exists in the archived ASCII; finer dumps need backend changes (*verify*, Q-A1) |
| ISBI post-correlation visibilities (SFXC) | Per baseline: time (2 s) × frequency (4 096 ch maser subband; 128 ch continuum) × 4 pol products, complex | As time–frequency structures on the one baseline; cross-correlation already suppresses uncorrelated RFI | **Yes** — this is the standard segmentation input |
| ISBI / EVN baseband (VDIF on FlexBuff) | 2-bit samples, 512 Mbit/s per station in the IVARS mode | Only after channelisation | Out of scope (companion doc) |
| LOFAR LV614 | Station beamformed / dynamic spectra | Classic low-frequency RFI | Different instrument; deferred |

**Consequence.** The first ML dataset is ISBI post-correlation dynamic spectra, one baseline, C band, 2 s × 4 096 channels. Single-dish spectra join only if VIRAC keeps time-resolved spectrometer output (Q-A1).

### 2.1 Why this is hard here specifically

- **A 6.7 GHz methanol maser is narrow, bright and variable** — exactly what a SumThreshold-class detector or a U-Net trained on LOFAR calls "narrow-band RFI". The literature's headline gains (MES22, CMP24, SWIN24, WF25) are on continuum-dominated or pulsar data, not on spectral-line data where the science *is* the spike. A "must-never-flag" set (W3OH, G111.542+0.776 — G25) is the primary metric, not an afterthought.
- **No strong labels exist for Irbene.** Every published result that beat AOFlagger did so on expert-labelled test sets from the same instrument. Nobody has labelled Irbene C-band. This is why the review loop in the companion doc exists.
- **One baseline.** Interferometric flaggers exploit baseline diversity. ISBI has one. Techniques that need many baselines (SIR across baselines, per-baseline statistics) reduce to single-dish-like behaviour.
- **SSA is already their method** (G25). SSA / KLT eigenspace projection is a *subtraction* method (CH22) — it reconstructs the signal without RFI components rather than masking cells. Comparing a mask model against a subtraction model needs two metrics: flag quality on cells and post-mitigation SNR on the line. Report both.
- **Site RFI** is DVB-T, GSM and sporadic C-band pulses from maritime radar and wind-turbine scatter (prior pass; source key pending, *verify* Q-A6). Pulsed, broadband, short — the case where time resolution of 2 s already averages most of it away, and where single-dish time-resolved data would matter most.

## 3. How heavy the data is

All rows are estimates from published observing modes (G25) unless keyed. VIRAC confirms in the meeting (Q-A2).

| Product | Rate / size | Basis |
|:---|:---|:---|
| IVARS baseband, one station | 512 Mbit/s = 230 GB/h | 8 sub-bands × 8 MHz × 2 pol × 2 bit × Nyquist (G25) |
| IVARS baseband, both stations, one session | ~3 TB | ~6–8 h per session: 30 targets × 2 × 5–8 min + calibrators (G25) |
| Whole IVARS raw archive (154 sessions) | ~450 TB | consistent with FlexBuff 288 + 64 TB and a 2 PB tape tier (G25, TOG25) |
| Spectral-line pass, one baseline, correlated | ~0.25 GB/h (one sub-band) to ~2 GB/h (all 8 sub-bands); 2–17 GB/session | 4 096 ch × 4 pol × complex64 every 2 s (G25); sub-band coverage of the line pass unknown (Q-A2) |
| Continuum pass | ~0.12 GB/h | 16 × 128 ch × 4 pol × complex64 every 2 s (G25) |
| Whole IVARS correlated archive | ~0.5–3 TB | 154 sessions × 3–17 GB, plus 20–50 % FITS-IDI/MS overhead |
| Single-dish maser spectrum | ~0.25 MB per pol-pair spectrum; a few MB per scan in ASCII | 32k-point FFT max, 14-bit, up to 50 MHz per channel (BL20); four files per scan (MDPS) |
| Single-dish archive 2017–2022 | tens of GB | 42 sources, 5–7 day cadence (G25, AB23) |
| Public LOFAR RFI set (MES22) | ~10 GB | 7 500 × 512×512 train, 109 expert test |
| Cross-telescope RFI set 2026 (HERA, LOFAR, NSRT) | ~103 GiB HDF5 | prior pass; *verify* key |

**Reading.** The ML problem is small: the entire correlated IVARS archive plus public sets is a few TB at most, fits in `/scratch` default quota (50 TB) many times over and in `/flash` default (2 TB) once. The heavy data is baseband, which we do not move. The Dask/MPI benchmark can use as much or as little baseband-derived data as the chosen step needs.

## 4. Compute we have

### 4.1 LUMI-G (LUMI-G, BILL)

- 2 978 nodes; per node one 64-core EPYC 7A53 (56 cores usable), 512 GB RAM, 4 × MI250X. Each MI250X is two GCDs; Slurm and HIP expose **8 GCDs per node**, each as a separate GPU device with 64 GB HBM. Billing counts MI250X modules (4 per node), not GCDs — see BILL. No local disk.
- Billing: 1 GPU-hour = one MI250X module for one hour. `standard-g` (whole nodes): 4 GPU-h per node-hour. `small-g` / `dev-g`: 0.5 GPU-h per GCD-hour, with a surcharge if more than 8 cores or 64 GB RAM per GCD is requested.
- **Our 4 500 GPU-h = 9 000 GCD-hours = 1 125 full-node-hours.**
- Limits (PART): `small-g` up to 4 nodes, 3 days; `standard-g` up to 1 024 nodes, 2 days; `dev-g` 30 min – 2 h for debugging only.
- Software (PYT): PyTorch ROCm containers as EasyBuild modules (e.g. `PyTorch/2.7.0-rocm-6.2.4-python-3.12-singularity-20250527`), `cotainr` to build custom ROCm containers, venvs squashed into SquashFS to protect Lustre. Required env: `MIOPEN_USER_DB_PATH` on `/tmp`, `NCCL_SOCKET_IFNAME=hsn0,hsn1,hsn2,hsn3`, and the `hsn` interfaces for anything distributed.

**Sizing.** A U-Net-class model on ~10k 512×512 spectrograms trains in roughly 1–2 GPU-h per run on one GCD (estimate; calibrate in P1). One hundred such runs is ~200 GPU-h. The grant is therefore *not* the constraint — labels and data are. The grant *is* large enough for what usually gets skipped: full sweeps, seeds, cross-telescope generalisation, self-supervised pre-training, and SSA / SVD on GPU at scale.

### 4.2 LUMI-C (LUMI-C, BILL)

- 2 048 nodes, 2 × EPYC 7763 = 128 cores, 256 GB (128 nodes at 512 GB, 32 at 1 TB), one 200 Gbit/s Slingshot NIC. `standard` bills 128 core-h per node-hour; `small` / `debug` bill `max(cores, ceil(mem/2 GB))` core-hours.
- `cray-python` ships NumPy/SciPy (Cray LibSci), **mpi4py on Cray MPICH, Pandas and Dask** — the fair A/B for Track B is one module, one node type.
- Our LUMI-C grant size is unclear from the note ("350") — *verify* (Q-A3): 350 node-hours, 350 k core-hours, or something else.

### 4.3 LUMI-D, RTU, VIRAC

- LUMI-D `largemem` (4 TB nodes, 1 day) for pre-processing that does not fit 256 GB; billed in core-hours. Its NVIDIA A40s are visualisation-only — not a CUDA escape hatch (PART).
- RTU Rudens (RTU): 1 node 4 × A100 40 GB, 2 nodes 4 × L40S, 4 nodes 2 × L40S, V100s; PBS; 100 Gbit/s to GÉANT. CUDA control runs and the only place the VIRAC GPU correlator (CUDA) runs as-is.
- VIRAC HPC (IT18, 2018): 30 nodes, 2 × Xeon E5-2630 v3, 128 GB each, 10 Gbit/s to GÉANT; GPU nodes announced in modernisation phase 4 (M4), status *verify* (Q-A4). Reproduction target for Track B.

### 4.4 GPU vendor: why AMD is acceptable here (Q-A10)

| Workload | Vendor exposure | Where it runs |
|:---|:---|:---|
| RFI segmentation (U-Net, Swin-UNETR) in PyTorch | None — standard conv/attention ops, DDP over RCCL; official ROCm PyTorch containers on LUMI (PYT) | LUMI-G |
| SSA / SVD baselines | `torch.linalg.svd` → rocSOLVER; only performance at 4 096-ch Hankel sizes is unknown (Q-B3); CPU fallback trivial | LUMI-G, CPU fallback |
| Dask vs MPI benchmark | CPU only | LUMI-C |
| ISBI-AARTFAAC correlator (TCC: CUDA/WMMA, NVRTC) | Total — no HIP backend (TCC); Pawsey abandoned an xGPU port to MI250X (BLINK) | Never on LUMI-G; RTU or VIRAC NVIDIA if ever in scope; parked |

- Reachable NVIDIA alternatives are thin: RTU Rudens is one 4 × A100 node plus a few L40S nodes, shared, PBS — enough for control runs, not sweeps (RTU). VIRAC GPU nodes: status unknown (Q-A4). Other EuroHPC NVIDIA systems need a new application with months of lead time. Meanwhile the LUMI grant is granted, sufficient, and subject to the cut-off (CUT).
- Genuine ROCm risks — custom CUDA kernels, bleeding-edge libraries, MIOpen cache quirks — either do not apply to U-Net-class models or are handled by LUMI's containers.
- Portability across ROCm and CUDA, proven by one control run per model on RTU (kept in P3), is itself a deliverable: a large share of EuroHPC GPU capacity is AMD.
- Flips to NVIDIA-first if: the correlator port enters scope; hand-written kernels (Numba-CUDA, Triton beyond ROCm support) become necessary; LUMI-AI turns out NVIDIA-based (pass-2 check — PyTorch work carries over regardless).

### 4.5 Policies that shape the plan

- **Resource cut-off (CUT):** for projects starting on/after 1 Oct 2025, usage is checked at 6 months; if under 40 % of the allocation is used, the allocation is cut to 60 %. Warning at 3 months if under 20 %. Applies to non-industrial regular and extreme-scale projects — whether our project type is covered: *verify* (Q-A5). Plan as if it applies: **≥ 1 800 GPU-h consumed by month 6.**
- **Project lifetime = data lifetime (STOR):** no backups anywhere on LUMI; data readable 90 days after project end, then deleted. LUMI-O is the on-LUMI backup tier; the real backup is in Latvia.
- **LUMI horizon (LAI):** competitive service life ends 2027; LUMI-AI (Bull) is scheduled 2H 2027. Anything we build must not depend on LUMI beyond 2027 — hence containers and object storage, not bespoke module chains.

## 5. Storage on LUMI (STOR, BILL, LUS)

| Area | Path | Default quota | Files | Rate | Use |
|:---|:---|:---|:---|:---|:---|
| Home | `/users/<u>` | 20 GB | 100k | — | configs only |
| Project | `/project/project_<id>` | 50 GB (→ 500 GB) | 100k | 1× | code, containers, squashed venvs |
| Scratch | `/scratch/project_<id>` | 50 TB (→ 500 TB) | 2 000k | 1× | staged inputs, checkpoints, outputs |
| Flash | `/flash/project_<id>` | 2 TB (→ 100 TB) | 1 000k | 3× | hot training set during a run only |
| Object | LUMI-O, S3 `https://lumidata.eu` | 150 TB (→ 2.1 PB) | 500k / bucket | 0.25× | ingress, egress, cold copies, sharing |

- Billing is TB-hours. 1 TB on scratch for 180 days = 4 320 TB-h; the same on flash = 12 960; on LUMI-O = 1 080. The TB-hour grant size: *verify* (Q-A3).
- Lustre default layout since May 2026 is progressive (1 stripe ≤ 256 MB; 4 OSTs to 16 GB; 8 above on LUMI-P; 8/16 on LUMI-F). Our training shards should be 256 MB – few GB HDF5 / Zarr chunks — no per-spectrogram files.
- `/tmp` on compute nodes is RAM and counts against job memory. MIOpen cache goes there.
- Automatic scratch/flash cleaning is not active but may be enabled with three months' notice.

## 6. Moving data: Irbene → LUMI

### 6.1 Path and bottleneck

| Hop | Capacity | Key |
|:---|:---|:---|
| VIRAC HPC / FlexBuff → GÉANT | 10 Gbit/s (2018); "10 Gbit optical fibre" for VLBI gear | IT18, V2 |
| Latvia (SigmaNet) → GÉANT | 100 Gbit/s since March 2021 | SIG |
| RTU → GÉANT | 100 Gbit/s | RTU |
| GÉANT → NORDUnet → Funet → Kajaani | 4 × 100 Gbit/s in place, scalable; 1.2 Tbit/s Amsterdam–Kajaani demonstrated May 2025 | KAJ, TBT |
| Ventspils University ↔ SigmaNet link | unknown | *verify* Q-A7 |

**The bottleneck is VIRAC's own 10 Gbit/s edge.** Theoretical 4.5 TB/h; realistic single-host long-distance 1–2 TB/h with parallel streams. A 1 TB sample moves in about an hour; the whole correlated archive in an afternoon; 100 TB of baseband in days — feasible but a decision, not a default.

### 6.2 Mechanism

- **Do not `scp`/`sftp` anything large.** Single-stream SSH over a high-latency path is bandwidth-limited by latency; LUMI's own training material says so and recommends LUMI-O (ACC).
- **LUMI-O from Latvia:** create keys at `auth.lumidata.eu` (up to one year), download the generated `rclone` config, run `rclone copy` from the VIRAC (or RTU) host with multipart uploads and several transfers in parallel. No LUMI SSH account is needed on the sending host — VIRAC staff can push without becoming LUMI users (LUO, ACC).
- **On LUMI:** `module load lumio` → `rclone copy lumi-o:bucket /scratch/...` from a login node or inside a job with a token whose lifetime covers the wall time. LUMI-O ↔ Lustre bandwidth is lower than Lustre ↔ compute; stage once, reuse many times (ACC).
- **Stale multipart parts eat quota** on LUMI-O; set a bucket policy or clean up after failed uploads (ACC).
- **No Globus** on LUMI (prior pass). No data-transfer node beyond login nodes documented — *verify* Q-A8.
- **Packing before transfer:** VIRAC exports are converted to HDF5 (visibilities: time × chan × pol per scan) or Zarr with 256 MB+ chunks *in Latvia*, so LUMI never sees the ASCII or thousands of small files.

## 7. Dask vs MPI on LUMI — what the fair experiment looks like

- Both sides from one `cray-python` module: `mpi4py` on Cray MPICH over Slingshot vs `dask.distributed` via `dask-jobqueue.SLURMCluster(interface="hsn0", ...)` or `dask-mpi` under the same `srun`. Same node type, same inputs, same output checked bit-for-bit or within a stated tolerance first (DJQ, PYJ).
- Candidate steps, ordered by how well they suit each side: bandpass / a-priori gain application (embarrassingly parallel — Dask should tie or win), spectral-line extraction and time-series binning across sessions (chunkable — Dask's home ground, AFR25a/b), fringe fitting or anything with all-to-all data movement (MPI's home ground). Report the crossover.
- Known Dask ceilings: task granularity and scheduler overhead at ~80+ workers (AFR25a); Python import storms on Lustre with many MPI ranks — mitigate with containers (PYJ).
- **Not the correlator.** SFXC is MPI because FX correlation is communication-bound (SFXC); the VIRAC GPU correlator is CUDA (ISBI): TCC is CUDA/WMMA-only with no AMD port (TCC), and Pawsey abandoned porting xGPU to MI250X and wrote a simpler HIP correlator from scratch (BLINK). A HIP/rocWMMA port is a real, separate project — parked (§11).

## 8. RFI methods: baseline stack for Irbene data

| Method | Role | Notes |
|:---|:---|:---|
| AOFlagger SumThreshold (AOF, AOFPY) | Weak-label generator and baseline | Python API `make_image_set` / `batch_run` takes NumPy arrays directly — no Measurement Set needed; Lua strategies can protect a channel range; Apertif strategy shows spectral-line-aware tuning (APE23). CPU only. |
| SSA / KLT eigenspace projection (CH22, G25) | VIRAC's method; second baseline | Hankel embedding + eigen-decomposition; report post-subtraction SNR. Runs on GPU via `torch.linalg.svd` / rocSOLVER — verify performance on MI250X (Q-B3). |
| Higher-order statistics of the power spectrum (FRI01) | Cheap third baseline | 13–20 dB suppression on WSRT spectral-line data; needs pre-integration statistics — only if time-resolved dumps exist. |
| U-Net on weak labels, Dice loss, AOFlagger pre-train (MES22, CMP24) | First model | Weak-label train / strong-label test. |
| Swin-UNETR / WF-SwinUnet (SWIN24, WF25) | Second model | After U-Net; single-dish FAST result is the closest published analogue. |
| Cross-telescope generalisation (prior pass, *verify* key) | Transfer test | Train on LOFAR/HERA/NSRT, test on Irbene: the honest "does anything transfer" experiment; NSRT is a single dish. |

## 9. Pipeline shape (what gets built)

1. **Latvia side (VIRAC + us):** exporter that reads SFXC output for one session and writes one HDF5 per session with visibilities, flags-if-any, and metadata; `rclone` push to a LUMI-O bucket.
2. **LUMI ingress job:** pull bucket → `/scratch`; validate checksums; build training shards (Zarr) → `/flash` for the active run only.
3. **Baseline job (LUMI-C `small`):** AOFlagger and SSA masks per session, stored next to the data with algorithm + version.
4. **Training job (LUMI-G `small-g`, 1–8 GCDs):** PyTorch ROCm container; weak labels in, model + masks out; sweeps as job arrays.
5. **Evaluation:** strong labels from the saas-base review loop (companion doc) flow back to LUMI-O; metrics per model next to both baselines; maser-safety FPR first.
6. **Egress:** masks and model cards → LUMI-O → saas-base ingest as Issue objects. Raw data never leaves LUMI except to Latvia.
7. **Benchmark job (LUMI-C `standard`, 1–16 nodes):** Track B harness; MPI and Dask variants; scaling curves committed with the harness.

## 10. Challenges and obstacles

| # | Obstacle | Severity | Mitigation |
|:---|:---|:---|:---|
| C1 | No strong labels for Irbene; maser lines look like RFI | High | Review loop first; maser-safety FPR as gate; protected-channel strategy for AOFlagger |
| C2 | Single-dish product is time-integrated — no dynamic spectra | High if Q-A1 is "no" | Start on ISBI visibilities; ask VIRAC to enable time-resolved dumps for one campaign |
| C3 | Lustre small-file limits vs VIRAC's per-scan ASCII | Medium | Pack to HDF5/Zarr in Latvia; never unpack on LUMI |
| C4 | Compute nodes without outbound internet / no local disk | Medium | Stage everything; containers; token lifetimes ≥ wall time |
| C5 | Resource cut-off at month 6 | Medium | Front-load GPU experiments; ≥ 1 800 GPU-h by month 6 |
| C6 | Data lifetime = project lifetime; LUMI ends 2027 | Medium | LUMI-O + Latvian copy; containers and S3, no LUMI-specific stack |
| C7 | ROCm gaps (MIOpen cache, some ops, AOFlagger CPU-only) | Medium | Official PyTorch containers; RTU CUDA control; keep flaggers on CPU |
| C8 | VIRAC edge is 10 Gbit/s | Low for ML, high for baseband | Move correlated data only; baseband stays unless Track B needs it |
| C9 | Dask benchmark rigged by choice of step | Medium | VIRAC picks the step; equivalence before timing; both on `cray-python` |
| C10 | VIRAC GPU correlator is CUDA-only | Out of scope | Park a HIP port; run as-is on RTU if ever needed |
| C11 | Reproduction on VIRAC's 2015-era cluster | Medium | Harness must run on 30 × Xeon v3 nodes without GPUs |
| C12 | Scientist review time | High | One named reviewer, weekly; otherwise Track A stalls at baselines |

## 11. Parking lot

- HIP / rocWMMA port of the Tensor-Core Correlator for ISBI-AARTFAAC — real project, wrong time.
- Real-time flagging in the USRP backend.
- LOFAR LV614 as a second instrument.
- Self-supervised pre-training on the full correlated archive (~0.5 TB) if the supervised route stalls — good use of surplus GPU-hours.
- Public release of an Irbene C-band expert-labelled test set, if VIRAC agrees (Q5 in companion).

## 12. Decisions registry (this doc; companion has Q1–Q9)

| Q# | Question | Status | Resolution |
|:---|:---|:---|:---|
| Q-A1 | Finest single-dish time resolution: archived ASCII gives ~15 s per stage (MDPS); can the backend dump shorter integrations, and is the raw ASCII archive retained? | open | Ask; decides how far single-dish RFI work can go |
| Q-A2 | Actual per-session sizes for IVARS baseband and correlated output; SFXC output format (FITS-IDI? MS? native) | open | Ask; replaces §3 estimates |
| Q-A3 | Exact grant: LUMI-C amount ("350" = ?), TB-hours, project type, start and end dates | open | Read `lumi-allocations`; decides cut-off exposure |
| Q-A4 | VIRAC HPC today: node count, GPUs from phase 4, Slurm? | open | Ask; reproduction target |
| Q-A5 | Is our LUMI project subject to the resource cut-off? | open | Ask LUMI support; plan as if yes |
| Q-A6 | Source key for the Irbene RFI environment claims (DVB-T, GSM, radar, turbines) | open | Pass-2 fetch |
| Q-A7 | Ventspils University ↔ SigmaNet link capacity | open | Ask VIRAC IT |
| Q-A8 | LUMI compute-node outbound policy and any dedicated transfer node | open | Pass-2 fetch, LUMI docs / support |
| Q-A9 | First data product for ML: ISBI correlated (proposed) vs single-dish | proposed | ISBI correlated, C band, IVARS sessions with W3OH/G111 as the safety set |
| Q-B3 | `torch.linalg.svd` / rocSOLVER performance on MI250X at 4 096-channel Hankel sizes — is GPU SSA worth it, or does the CPU baseline suffice? | open | Measure in P2 (SSA sweep); pass-2 literature check for KLT/SSA-on-GPU results |
| Q-A10 | AMD (LUMI-G) vs NVIDIA-only cluster | **resolved** | LUMI-G for training and sweeps; RTU Rudens as CUDA control and the only home for CUDA-only code (correlator); zero vendor-specific code in our repos. Rationale in §4.4. Revisit only if the correlator port enters scope or hand-written kernels become necessary |

## 13. Research backlog (pass 2)

Ordered by how much a wrong assumption would cost.

**LUMI**

- Official statement on compute-node outbound network access; existence of data-transfer nodes (Q-A8).
- Measured LUMI-O ↔ Lustre and Latvia → LUMI-O throughput; recommended `rclone` concurrency on LUMI.
- Whether Development / Benchmark / national projects are exempt from the cut-off (Q-A5).
- LUMI-AI (2027) GPU vendor and software stack — decides whether ROCm-specific tuning has a future on LUMI or only portability matters.
- `torch.linalg.svd` / rocSOLVER performance on MI250X for SSA at 4 096-channel Hankel sizes (Q-B3).
- `cotainr` recipe that includes `aoflagger` (conda-forge) alongside PyTorch ROCm; or keep AOFlagger in a separate CPU container.
- `dask-mpi` availability in `cray-python`; Dask dashboard access through Open OnDemand.
- Zarr vs HDF5 read throughput on LUMI-F with PFL defaults; optimal chunk sizes for 2 s × 4 096 ch planes.
- Exact TB-hour and file-count quotas granted to our project.

**VIRAC**

- IVARS correlated data format and whether AIPS/CASA flag tables already exist (free weak labels).
- Whether the Dask pipeline code (G25) is public; which steps exist today.
- Any published RFI survey or spectrum-occupancy measurement at Irbene (Q-A6).
- USRP backend dump mode and retention (Q-A1).
- Network: Irbene site → Ventspils → SigmaNet path and capacity (Q-A7).

**Methods**

- Spectral-line-safe AOFlagger strategies (Apertif, GBT, Effelsberg single-dish practice); `TelescopeId` closest to a 32 m dish.
- ITU protection status of 6 650–6 675.2 MHz and what interferers are legal there.
- Single-dish RFI ML on FAST/NSRT/Effelsberg beyond WF25 and PAT26; NSRT subset of the cross-telescope set as the nearest public analogue.
- KLT/SSA on GPU implementations in radio astronomy; complexity for 2 s × 4 096 planes.
- Dask vs MPI benchmark templates on Slingshot systems (Setonix, LUMI) to copy the methodology.

**Access and people**

- RTU Rudens allocation process for A100 / L40S control runs.
- Who at VIRAC owns SFXC output export; who owns the FlexBuff/JIVE transfer tooling (`jive5ab`, `m5copy`) that could be reused for pushes to LUMI-O.

## 14. Devil's advocate

- **The ML might not be needed.** With one baseline and 2 s integration, AOFlagger with a protected maser channel range plus SSA may already be "good enough". The project must be valuable if the model result is "no better": labels, lineage, a reproducible harness, and the Dask/MPI report are the deliverables that survive that outcome.
- **4 500 GPU-hours is a small grant** (EuroHPC Development access alone is 40 000 GPU-h — DEV). It is large for *this* problem only because the problem is small. Do not design experiments to look big.
- **We can move data faster than they can label it.** Weeks of transfer capacity vs one scientist's hours a week. The schedule is set by C12, not by GÉANT.
- **LUMI is a moving target** through 2027. Containers, S3 and a harness that also runs on RTU and VIRAC's cluster are the hedge — and they are also just good engineering.

## 15. References

Keys resolve in [`corpus/irbene/sources.md`](../../corpus/irbene/sources.md). VIRAC: G25, TOG25, IT18, MDPS, BL20, AB23, M4, V2, ISBI. Methods: AOF, AOFPY, APE23, CH22, FRI01, MES22, CMP24, SWIN24, WF25, PAT26, AFR25a, AFR25b, SFXC, TCC, BLINK. Infrastructure: LUMI-G, LUMI-C, BILL, PART, STOR, LUS, LUO, ACC, PYT, PYJ, DJQ, CUT, LAI, DEV, KAJ, TBT, SIG, RTU.
