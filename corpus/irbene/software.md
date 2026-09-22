# corpus/irbene/software.md

# Irbene / VIRAC — public software inventory

Public code from VIRAC, with what each repository does and what it tells us about the data chain. Source keys in [`sources.md`](sources.md). Repository metadata as observed 2026-09-22 via the GitHub API (VSORG).

## GitHub organisation `VIRAC-SPACE`

| Repository | Language | Last push | What it is | Relevance |
|:---|:---|:---|:---|:---|
| `ISBI-AARTFAAC` | C++ (CUDA / OpenCL) | 2026-09-18 | GPU correlator for the two-element interferometer, derived from ASTRON's AARTFAAC correlator; uses the Tensor-Core Correlator. Reads VDIF from files (offline) or UDP (real-time, `-R true`, one frame per datagram, per-station ports). Active: real-time testing, VDIF stream split into socket/file readers, integer-delay fixes (May–Sept 2026). ~2 100 lines in `ISBI/`. | Their RADIOBLOCKS deliverable. CUDA-only; out of our scope but defines the future upstream of the pipeline |
| `ISBI_pipeline` | Python (ParselTongue on AIPS) | 2024-06-20 | Single script `irib.py`. The full IVARS reduction: sampling-loss correction → a-priori gain (Tsys, gain curve from noise diode) → bandpass from continuum calibrators → manual phase-cal (RCP/LCP, inter-channel delay) → group-delay fringe fit on continuum at ~20 min intervals → per-channel fringe fit and flux-scale tuning → copy solutions to line data → fringe fit on maser peak channel at 20 s intervals for atmospheric phase/rate → copy back to continuum for long integration → final inspection fringe fit → spectra, visibility plots, continuum fluxes. Phase-rate solutions discarded in early stages. Author: R. A. Burns; funded by lzp-2022/1-0083 (IVARS). | **The exact step list for Track B.** Every stage above is a candidate pipeline step with an equivalence test |
| `ISBI_monitoring` | Python | 2026-01-27 | Monitoring for the interferometer (contents not inspected) | Likely source of per-session health metadata |
| `Visualization-tool-for-interferometric-data` | Python | 2026-01-28 | Plotting for interferometric products (small) | Reference for what scientists look at |
| `Maser-Data-Processing-Suite` | Python | — | Single-dish spectral-line reduction and monitoring; see below | Single-dish data chain (MDPS) |
| `kana` | C | 2023-03-02 | In-house software correlator (alpha) used for GNSS / space-debris interferometry | Historical; not the science correlator |
| `virac_pulsar_scripts` | Python | 2024-11-17 | Pulsar observing / reduction scripts | Out of scope |
| `Automatic_Correlation_information_system` | — | — | Not inspected | — |
| `dspsr` | — | — | Fork of the DSPSR pulsar package | Out of scope |

## Maser Data Processing Suite (MDPS) — single-dish chain in detail

From the MDPS preprint (MDPS) and BL20.

| Fact | Source |
|:---|:---|
| Backend: Ettus USRP X300 with TwinRX daughterboard; dual-polarisation spectroscopy; optimum attenuation found via noise-diode on/off calibration | MDPS, BL20 |
| Observing mode: frequency switching after Winkel et al. 2012 — **four stages per scan, typically 15 s integration each**: `ref off`, `sig off`, `ref on`, `sig on` (LO shifted up/down; noise diode off/on) | MDPS |
| One ASCII file per stage per scan: three columns — frequency, left-pol amplitude, right-pol amplitude; no header. Naming `source_frequency_station_iteration_NNNsX.dat`, e.g. `001r0` = scan 001, ref, diode off | MDPS |
| Typical spectrum length 4 096 points | MDPS |
| Scans within an observation are aligned on the peak velocity channel and averaged; residual baseline removed with an order-3 polynomial | MDPS |
| Calibration: backend units → K via Tsys from diode on/off; K → Jy via DPFU and an elevation-dependent gain polynomial from separate continuum-calibrator sessions; central half of the band (1/4–3/4 of samples) kept | MDPS |
| Outputs: HDF5 with tables `amplitude`, `amplitude_corrected`, `amplitude_corrected_not_smooht`, `specie`, `system_temperature`; JSON for monitoring metadata | MDPS |
| Monitoring: component amplitude vs time; Lomb–Scargle periodograms (Astropy); velocity–time contour maps | MDPS |
| Instrument-stability set — stable velocity components used to detect instrumental errors: G32.744-0.076 (30.49, 39.18 km/s), G49.490-0.388/W51 (59.29), G59.783+0.065 (19.2), G69.540-0.976/ON1 (14.64), G188.95+0.89/S252 (10.84), G111.542+0.777/NGC7538 (-58.04), G133.947+1.064/W3(OH) (-44.6) | MDPS |
| Why in-house: no existing package (CASA, GILDAS, GBTIDL, Effelsberg pipeline) reads the USRP output or implements frequency-switching calibration with a monitoring module | MDPS |

**Reading for the RFI work.** A single-dish scan is four ~15 s integrations, so the finest native time resolution in the archived ASCII is ~15 s per stage — not per-scan only, as assumed earlier. Whether the backend can dump shorter integrations is still the open question (Q-A1 in `docs/virac/RFI_LUMI_FINDINGS.md`). The instrument-stability component list is a ready-made "must never flag" set beyond W3OH and G111.

## Reduction stages as pipeline steps

Consolidated from `ISBI_pipeline` (ISBIP) and G25 for Track B step selection:

1. Load line and continuum datasets (SFXC output, two passes).
2. Digital sampling-loss correction (continuum).
3. A-priori gain calibration from Tsys and gain curve (noise-diode measurements).
4. Bandpass from continuum calibrators.
5. Manual phase-cal: RCP/LCP phase, inter-baseband-channel delay; integrate channels and polarisations.
6. Group-delay fringe fit on continuum sources, ~20 min solution interval; apply to all targets.
7. Per-baseband-channel fringe fit; absolute flux-scale tuning against maser and continuum calibrators.
8. Copy matching-channel solutions to line data.
9. Fringe fit on maser peak channel, 20 s intervals → atmospheric phase and rate; copy back to continuum.
10. Long integration of continuum on maser targets; final inspection fringe fit.
11. Output spectra, visibility plots, integrated continuum flux densities.

Steps 2–5 and 8, 11 are array-shaped and embarrassingly parallel across sources/scans (Dask's home ground). Steps 6, 7, 9 are solver steps whose cost is per solution interval; their parallelism is across sources and intervals, not within. None is communication-bound in the SFXC sense.
