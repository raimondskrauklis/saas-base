# corpus/irbene/facts.md

# Irbene / VIRAC — facts

Every line carries a source key from [sources.md](sources.md). Dates are as published; where a source states a plan rather than a result, the line says so.

## Operator and site

| Fact | Source |
|:---|:---|
| VIRAC — Ventspils International Radio Astronomy Centre — is operated by Ventspils University of Applied Sciences (VUAS) | G25, V2 |
| Site: Irbene, Kurzeme, Latvia; former Soviet installation handed over in 1994 | V1 |
| Two fully steerable parabolic telescopes: RT-32 (32 m) and RT-16 (16 m), 800 m apart, forming the Irbene Single-Baseline Interferometer (ISBI) | G25 |
| A LOFAR international station (LOFAR-LATVIA, LV614) is also on site | V2, LRFI |
| Both dishes have taken part in EVN and EVN-Lite VLBI sessions since October 2015 and contributed to the RadioAstron space-VLBI mission | G25 |

## Receivers and sensitivity

| Fact | Source |
|:---|:---|
| Both telescopes: broadband cryogenic 4.5–8.8 GHz receivers (TTI, Spain), dual circular polarisation, front-end at 14 K, IF 0.3–1.5 GHz | G25 |
| System temperature ≈ 30 K (RT-32) and 35 K (RT-16); SEFD 300–400 Jy, comparable to other EVN stations | G25 |
| RT-32 also has an uncooled L-band (1.45–1.72 GHz) receiver, three-mirror optics, SEFD ≈ 750 Jy at 1650 MHz | G25 |
| Calibration: phase-cal tone injection (1 MHz spacing) and broadband noise diode | G25 |
| RT-32 aperture efficiency at C band is estimated at 30 % because of surface-panel misalignment since the 2015 refurbishment and an off-axis C-band feed position | G25 |
| RT-16 modernisation: in-house cryogenic dual-band X (8–12 GHz) + Ka (26.5–40 GHz) receiver scheduled for Q1 2026; interferometry stays X-band until RT-32 gets Ka | G25 |
| Fourth modernisation phase (announced 2025): RT-32 surface calibration targeting higher efficiency, new cryogenic L/S receiver, HPC cluster expansion with GPU nodes intended for machine learning, data streaming | M4 |

## Data acquisition, storage, timing

| Fact | Source |
|:---|:---|
| Digitisation: DBBC2 digital baseband converters (2-bit sampling, multiband) plus a programmable spectral-line backend on the Ettus USRP X300 SDR | G25, BL20 |
| Recording: FlexBuff servers, 288 TB and 64 TB; long-term archive on a 2 PB tape system originally built for LOFAR | G25 |
| Baseband format: VDIF (FlexBuff); Mark 5 at RT-16 has been retired in favour of FlexBuff | G25 |
| Timing: T4 Science Hydrogen Maser 3000 at RT-16, distributed to RT-32 over fibre with White Rabbit; Allan variance better than 1e-15 over a day | G25 |
| Observation control: custom scripting system executing predefined source / frequency / calibration sequences autonomously | G25 |

## Correlation and post-processing software

| Fact | Source |
|:---|:---|
| Correlator: SFXC (DiFX-2.8.1 build) from JIVE — an MPI-based software FX correlator | G25, SFXC |
| Typical correlation resolution 0.01 MHz → 0.088 km/s at 6.7 GHz; IVARS runs two passes: continuum (128 FFT points) and spectral line (4096 FFT points), 2 s integrations | G25 |
| Post-processing: AIPS (31DEC25) and CASA 6.7; calibration in a dedicated ParselTongue pipeline (a-priori gain, bandpass, manual phase-cal, apply) | G25 |
| The same SFXC + AIPS + ParselTongue pipeline built for masers (IVARS) is reused unchanged for stellar-flare continuum (STEF) | G25 |
| In-house "KANA" software correlator (alpha) used for GNSS / space-debris interferometry outputs | G25, KO12 |
| Residual delay/phase solving in the reduction pipeline is an acknowledged open optimisation item (Burns et al., in prep) | G25 |

## Stated plans for processing frameworks (as of Nov 2025)

| Fact | Source |
|:---|:---|
| VIRAC is building a modular Dask-based processing pipeline covering calibration, RFI mitigation, spectral-line extraction and time-series analysis | G25 |
| The named RFI approach in that pipeline is Singular Spectrum Analysis (SSA) decomposition, aimed at dynamic spectral environments | G25 |
| Within RADIOBLOCKS, VIRAC is developing a GPU-accelerated correlator for the ISBI, modelled on the AARTFAAC correlator, with near-real-time fringe fitting and beamforming modes planned | G25, RB |
| Cross-correlation between the two antennas is cited as reducing RFI relative to single-dish data | G25 |
| A VUAS bachelor project produced a real-time RFI detection tool for the LOFAR station LV614 (Python, Docker, Flask UI) | LRFI |

## Science programmes

| Fact | Source |
|:---|:---|
| 6.7 GHz Class II methanol maser monitoring: 42 sources, March 2017 – October 2022, cadence 5–7 days, ~95 % on RT-16; >55 % of sources variable | G25, AB23 |
| IVARS (Latvian Science Council, from 2022): 30 high-mass protostars monitored interferometrically; 236 sessions Feb 2024 – Apr 2025, 154 successful; reference masers W3OH and G111.542+0.776, continuum calibrators J2202+4216 and J2230+6946 | G25 |
| STEF (Latvian Science Council, 2023–2025, 300 k€): QPPs in stellar flares; targets EV Lac, AD Leo; 1 s time resolution; nine campaigns since Nov 2023; no clear flare yet, sensitivity to tens of mJy modelled | G25 |
| Ionosphere probing with GNSS as coherent sources, including SURA heating experiments (from 2012) | G25 |
| GNSS satellite orbit determination: VLBI + SLR campaigns NKA41/42 (Sept 2017), >25 GPS/GLONASS satellites, 8 MHz bandwidth, LCP | G25 |
| Forward-scatter radar detection of space debris using GNSS satellites as illuminators; fragment 16182 detected 18 March 2021 | G25 |
| OH maser (1.6 GHz) observations on RT-32 L-band | SK22 |

## Projects and funding

| Fact | Source |
|:---|:---|
| RADIOBLOCKS — Horizon Europe 101093934, 1 March 2023 – 28 February 2027, 8.9 M€ | G25, RB |
| STEF — lzp-2022/1-0017, 1 January 2023 – 31 December 2025, 300 k€ | G25 |
| IVARS — Latvian Science Council, launched 2022 | G25 |

## People named in public material

Authors of G25 (VIRAC unless noted): Ivar Shmeld, Vladislavs Bezrukovs (corresponding), Jānis Šteinbergs, Karina Šķirmante, Artis Aberfelds, Ross A. Burns, Dmitrijs Bezrukovs, Māris Purviņš, Anna Kalniņa, Arturs Orbidans, Marcis Bleiders, Marina Konuhova; with Sergey A. Belov, Dmitrii Y. Kolotkov, Valery M. Nakariakov (solar / stellar QPP collaborators). Software credited to I.S., V.B., J.Š., K.Š., A.A., R.A.B., M.P., M.B. | G25
