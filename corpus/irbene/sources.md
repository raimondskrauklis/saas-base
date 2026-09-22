# corpus/irbene/sources.md

# Irbene / VIRAC — sources

Source keys used in `facts.md`. Public material only.

| Key | Source | What it gives |
|:---|:---|:---|
| G25 | Shmeld, I.; Bezrukovs, V.; Šteinbergs, J.; Šķirmante, K.; Aberfelds, A.; Belov, S.A.; Burns, R.A.; Kolotkov, D.Y.; Nakariakov, V.M.; Bezrukovs, D.; Purviņš, M.; Kalniņa, A.; Orbidans, A.; Bleiders, M.; Konuhova, M. "Applications of the Irbene Single-Baseline Radio Interferometer." *Galaxies* 2025, 13(6), 126. [doi:10.3390/galaxies13060126](https://doi.org/10.3390/galaxies13060126). CC BY 4.0. | Instruments, receivers, data acquisition, storage, correlator, software stack, science programmes, Dask / SSA / GPU-correlator plans, RADIOBLOCKS, STEF, IVARS |
| M4 | VUAS, "VUAS Launches Fourth Modernization Phase of the Irbene Radio Telescope Complex", [en.virac.eu](https://en.virac.eu/vuas-launches-fourth-modernization-phase-of-the-irbene-radio-telescope-complex) | Current RT-32 efficiency, phase-4 investments: surface calibration, L/S cryo receiver, HPC + GPU expansion for ML, data streaming |
| V1 | VIRAC — History, [en.virac.eu](https://en.virac.eu/astronomija-interesentiem/vesture) | 1994 handover, reconstruction dates |
| V2 | VIRAC — About, [en.virac.eu](https://en.virac.eu/about) | Operator, instruments, LOFAR-LATVIA |
| EVN | "First successful VLBI observations in the EVN with RT-32", PoS, [doi:10.22323/1.178.0078](https://doi.org/10.22323/1.178.0078) | RT-32 receiver bands at EVN entry, 2012 fringe test |
| LRFI | JanFPV, `lofar-RFI-detection`, [github.com/JanFPV/lofar-RFI-detection](https://github.com/JanFPV/lofar-RFI-detection) | VUAS bachelor thesis: real-time RFI detection tool for Irbene LOFAR station LV614 |
| AB23 | Aberfelds, A.; Šteinbergs, J.; Shmeld, I.; Burns, R.A. "Five years of 6.7-GHz methanol maser monitoring with Irbene radio telescopes." *MNRAS* 526, 5699 (2023). | Single-dish maser monitoring programme |
| SK22 | Skirmante, K. et al. "Observations of Weak Galactic OH Masers in 1.6 GHz Frequency Band Using Irbene RT-32." *Latv. J. Phys. Tech. Sci.* 59, 14 (2022). | L-band OH maser work |
| BL20 | Bleiders, M. "Spectral Line Registration Backend Based on USRP X300 Software Defined Radio." *J. Astron. Instrum.* 9, 2050009 (2020). | Spectral-line backend design |
| KO12 | Kotlere, D. et al. "Algorithmic Development of Software Correlator for Space Debris Data Processing in VIRAC." *VIRAC Space Res. Rev.* 1, 57 (2012). | KANA in-house correlator |
| SFXC | Keimpema, A. et al. "The SFXC Software Correlator for VLBI." *Exp. Astron.* 39, 259 (2015). | SFXC design — MPI-based FX correlator |
| RB | RADIOBLOCKS project, [radioblocks.eu](https://radioblocks.eu/) | Horizon Europe grant 101093934, 2023-03-01 → 2027-02-28, 8.9 M€ |
| TOG25 | Irbene station report to the EVN TOG, 4 Sept 2025, [jive.eu/jivewiki](https://jive.eu/jivewiki/lib/exe/fetch.php?media=tog%3A20250904_irbene_station_report_to_the_tog_2025.pdf) | FlexBuff 32 TB + 288 TB (36 × 8 TB), jive5ab 3.1.0, disk upgrade to 16 TB planned 2026; RT-16 X/Ka receiver Q1–Q2 2026 ends its EVN use; overflow to LOFAR data server (39 TB HDD, 2 PB tape) |
| IT18 | "First interferometric observations in Irbene – Torun baseline conducted by VIRAC", PoS 344, 131 (2018). [doi:10.22323/1.344.0131](https://doi.org/10.22323/1.344.0131) | VIRAC HPC in 2018: 30 nodes, 2 × Xeon E5-2630 v3, 128 GB each, 10 Gbit/s to GÉANT; FlexBuff 320 TB; pySCHED / Field System / jive5ab pipeline; KANA + SFXC |
| MDPS | VIRAC-SPACE, Maser Data Processing Suite, [github.com/VIRAC-SPACE/Maser-Data-Processing-Suite](https://github.com/VIRAC-SPACE/Maser-Data-Processing-Suite); Šteinbergs et al., preprint [doi:10.20944/preprints202108.0156.v1](https://doi.org/10.20944/preprints202108.0156.v1) | Single-dish spectral-line chain: four ASCII files `r0 r1 s0 s1` per scan → HDF5 tables (amplitude, corrected, smoothed, species, Tsys) + JSON monitoring |
| ISBI | VIRAC-SPACE, ISBI-AARTFAAC, [github.com/VIRAC-SPACE/ISBI-AARTFAAC](https://github.com/VIRAC-SPACE/ISBI-AARTFAAC) | GPU correlator for the ISBI; C++ / CUDA / NVRTC; "for usage with Nvidia GPUs"; uses the Tensor-Core Correlator |
| EVNC | EVN capabilities, [evlbi.org/capabilities](https://www.evlbi.org/capabilities) | Disk recording at 2 Gbit/s standard, 4 Gbit/s best-effort; e-VLBI real-time ~1–2 Gbit/s per station; SFXC modes |

## External method references (not VIRAC-specific)

Used in `docs/virac/` findings, listed here so the corpus is one place for citations.

| Key | Source | What it gives |
|:---|:---|:---|
| AOF | Offringa, A. et al. "Post-correlation radio frequency interference classification methods." *MNRAS* 405, 155 (2010). | AOFlagger / SumThreshold baseline |
| MES22 | Mesarcik, M. et al. "Learning to detect RFI in radio astronomy without seeing it." *MNRAS* 516, 5367 (2022). [arXiv:2207.00351](https://arxiv.org/abs/2207.00351) | LOFAR public RFI dataset: 7,500 AOFlagger-labelled train, 109 expert-labelled test; NLN vs U-Net vs AOFlagger |
| CMP24 | "A comparison framework for deep learning RFI detection algorithms." *MNRAS* (2024). [doi:10.1093/mnras/stae892](https://doi.org/10.1093/mnras/stae892) | Weak-label train / strong-label test methodology, Dice loss, AOFlagger pretraining |
| SWIN24 | Ouyang, X. et al. "Hierarchical vision transformers for RFI mitigation in radio astronomy." RFI 2024. [PDF](https://vannieuwpoort.com/wp-content/uploads/RFI_2024.pdf) | Swin-UNETR on LOFAR: AUROC 0.97, F1 0.64 vs AOFlagger F1 0.57 |
| WF25 | "WF-SwinUnet: A Window Fusion-based RFI Segmentation Model and Its Application in FAST." *AJ* (2025). [doi:10.3847/1538-3881/aded03](https://doi.org/10.3847/1538-3881/aded03) | Segmentation vs SumThreshold on hand-labelled FAST spectrograms |
| PAT26 | "PaTRNet: Low-latency SED RFI Mitigation for FAST Pulsar Searches." *AJ* (2026). [doi:10.3847/1538-3881/ae3d0a](https://doi.org/10.3847/1538-3881/ae3d0a) | 1-D low-latency RFI model, F1 0.888, 3 ms per slice |
| AFR25a | Perkins, S. et al. "Africanus I. Dask-MS and Codex Africanus." *Astron. Comput.* 52, 100958 (2025). [arXiv:2412.12052](https://arxiv.org/abs/2412.12052) | Dask for radio data processing; scaling to ~80 workers, task granularity ceiling |
| AFR25b | Kenyon, J. et al. "Africanus II. QuartiCal." *Astron. Comput.* (2025). [doi:10.1016/j.ascom.2025.100962](https://doi.org/10.1016/j.ascom.2025.100962) | Dask + Numba calibration at scale; single-node and distributed benchmarks |
| AOFPY | AOFlagger documentation, Python interface, [aoflagger.readthedocs.io](https://aoflagger.readthedocs.io/en/latest/python_interface.html) | `make_image_set` / `load_strategy_file` / `batch_run` on NumPy arrays without a Measurement Set; Lua strategies with `TelescopeId` |
| APE23 | Apertif AOFlagger strategy notes, [ASTRON Apertif docs](https://www.astron.nl/telescopes/wsrt-apertif/apertif-drift-scan-notes/) | Spectral-line-aware strategy tuning, protected channel ranges (used as pattern, not as Irbene strategy) |
| CH22 | Chen, X. et al. "RFI mitigation with SSA/KLT eigenspace projection." (2022) — *verify exact citation in pass 2* | Singular Spectrum Analysis / KLT as a subtraction method; Hankel embedding, eigen-decomposition |
| FRI01 | Fridman, P. A. "RFI excision using a higher order statistics analysis of the power spectrum." *A&A* 368, 369 (2001). [doi:10.1051/0004-6361:20000497](https://doi.org/10.1051/0004-6361:20000497) | 13–20 dB RFI suppression on WSRT spectral-line data using pre-integration statistics |
| SFXC | Keimpema, A. et al. "The SFXC software correlator for VLBI." *Exp. Astron.* 39, 259 (2015). [doi:10.1007/s10686-015-9446-1](https://doi.org/10.1007/s10686-015-9446-1) | MPI-based FX correlator used at JIVE and by VIRAC; communication-bound design |
| TCC | Romein, J. W. "The Tensor-Core Correlator." *A&A* 656, A32 (2021). [github.com/nlesc-recruit/tensor-core-correlator](https://github.com/nlesc-recruit/tensor-core-correlator) | CUDA / WMMA tensor-core correlator library; no AMD backend |
| BLINK | Pawsey / Curtin BLINK pipeline papers (2023–2024) on MI250X correlation — *verify exact citation in pass 2* | xGPU port to Setonix MI250X abandoned; simpler HIP correlator written from scratch |

## Compute and network infrastructure

| Key | Source | What it gives |
|:---|:---|:---|
| LUMI-G | LUMI docs, [GPU nodes — LUMI-G](https://docs.lumi-supercomputer.eu/hardware/lumig/) | 2 978 nodes; 64-core EPYC 7A53, 512 GB, 4 × MI250X (8 GCDs / node, 64 GB HBM each); no local disk |
| LUMI-C | LUMI docs, [CPU nodes — LUMI-C](https://docs.lumi-supercomputer.eu/hardware/lumic/) | 2 048 nodes; 2 × EPYC 7763, 256 GB (128 × 512 GB, 32 × 1 TB); 200 Gbit/s Slingshot |
| PART | LUMI docs, [Slurm partitions](https://docs.lumi-supercomputer.eu/runjobs/scheduled-jobs/partitions/) | Partition limits: `small-g` 4 nodes / 3 d, `standard-g` 1 024 nodes / 2 d, `dev-g`, `small`, `standard`, `largemem`, `lumid` |
| BILL | LUMI docs, [Billing policy](https://docs.lumi-supercomputer.eu/runjobs/lumi_env/billing/) | GPU-hour = one MI250X module-hour; 0.5 GPU-h per GCD-hour; core-hours on LUMI-C; TB-hours 1× P, 3× F, 0.25× O |
| STOR | LUMI docs, [Storage overview / quotas](https://docs.lumi-supercomputer.eu/storage/) | Default quotas: home 20 GB, project 50 GB, scratch 50 TB, flash 2 TB, LUMI-O 150 TB; file-count limits; no backups; data readable 90 d after project end |
| LUS | LUMI docs, [Parallel filesystems / Lustre](https://docs.lumi-supercomputer.eu/storage/parallel-filesystems/lustre/) | LUMI-P 80 PB / 960 GB/s; LUMI-F ~8 PB / ~2 TB/s; progressive default layout; `lfs setstripe`; avoid many small files |
| LUO | LUMI docs, [LUMI-O object storage](https://docs.lumi-supercomputer.eu/storage/lumio/) | S3 endpoint `lumidata.eu`; keys via `auth.lumidata.eu` (≤ 1 year); `lumio-conf`, `rclone`, `s3cmd`; external access supported |
| ACC | LUMI training, "Accessing LUMI and transferring data" (LUMI intro course 2025, [lumi-supercomputer.github.io](https://lumi-supercomputer.github.io/LUMI-training-materials/)) | `scp`/`sftp` discouraged for large data; LUMI-O recommended; stale multipart uploads consume quota; LUMI-O ↔ Lustre bandwidth lower than Lustre ↔ compute |
| PYT | LUMI docs, [PyTorch on LUMI](https://docs.lumi-supercomputer.eu/software/packages/pytorch/) | ROCm PyTorch Singularity modules; `cotainr`; `MIOPEN_USER_DB_PATH` on `/tmp`; `NCCL_SOCKET_IFNAME=hsn0,hsn1,hsn2,hsn3` |
| PYJ | LUMI docs, [Python on LUMI](https://docs.lumi-supercomputer.eu/software/installing/python/) | `cray-python` bundle: NumPy/SciPy on LibSci, mpi4py on Cray MPICH, Pandas, Dask; SquashFS venvs to protect Lustre |
| DJQ | dask-jobqueue docs, [SLURMCluster](https://jobqueue.dask.org/en/latest/generated/dask_jobqueue.SLURMCluster.html) | `interface` for high-speed NIC; `scheduler_options`; `job_extra_directives` |
| CUT | LUMI docs, [Resource cut-off policy](https://docs.lumi-supercomputer.eu/runjobs/lumi_env/cutoff/) | Projects from 1 Oct 2025: at 6 months, < 40 % used → allocation reduced to 60 %; warning at 3 months if < 20 % |
| LAI | LUMI / EuroHPC announcements on LUMI-AI (2025) — *verify exact URL in pass 2* | LUMI-AI (Eviden/Bull) scheduled 2H 2027; LUMI service life to 2027 |
| DEV | EuroHPC JU, [Access calls](https://eurohpc-ju.europa.eu/access-our-supercomputers/eurohpc-access-calls_en) | Development access 2026: 10 000 node-h LUMI-G (40 000 GPU-h), 15 000 node-h LUMI-C; 105 498 TiB-h storage |
| KAJ | CSC / LUMI, network connectivity statements — *verify exact URL in pass 2* | 4 × 100 Gbit/s Kajaani ↔ Funet/NORDUnet ↔ GÉANT; scalable to multi-terabit |
| TBT | NORDUnet / GÉANT news, May 2025 — *verify exact URL in pass 2* | 1.2 Tbit/s demonstration Amsterdam ↔ Kajaani |
| SIG | SigmaNet (LU MII) news, March 2021 — *verify exact URL in pass 2* | Latvian NREN uplink to GÉANT at 100 Gbit/s |
| RTU | RTU HPC centre, [hpc.rtu.lv](https://hpc.rtu.lv/) | Rudens cluster: 4 × A100 node, L40S nodes (2 × 4, 4 × 2), V100s, K40s; PBS; 100 Gbit/s to GÉANT; EuroCC Latvia |
