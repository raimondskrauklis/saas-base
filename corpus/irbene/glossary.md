# corpus/irbene/glossary.md

# Irbene / VIRAC — glossary

Terms that appear in VIRAC material and in our planning docs. Short, engineer-facing.

## Instruments and signal chain

| Term | Meaning |
|:---|:---|
| RT-32 / RT-16 | The 32 m and 16 m dishes at Irbene |
| ISBI | Irbene Single-Baseline Interferometer — RT-32 + RT-16 as a two-element interferometer |
| Baseline | The vector between two antennas; one baseline here, 800 m |
| Band (L, S, C, X, Ka) | Frequency ranges: L ≈ 1–2 GHz, S ≈ 2–4, C ≈ 4–8, X ≈ 8–12, Ka ≈ 26.5–40 GHz |
| SEFD | System equivalent flux density, Jy — lower is more sensitive |
| Aperture efficiency | Fraction of the dish's geometric area that collects usefully; surface errors lower it |
| IF | Intermediate frequency — the down-converted band that gets digitised |
| DBBC2 | Digital baseband converter — digitises IF into channels for VLBI |
| USRP X300 | Ettus software-defined radio used as a spectral-line backend |
| FlexBuff | Commodity server for recording VLBI baseband at high rate |
| VDIF | VLBI Data Interchange Format — raw baseband recording format |
| Mark 5 | Older VLBI recorder family, retired at Irbene |
| Hydrogen maser | Atomic frequency standard providing the station clock |
| White Rabbit | Sub-nanosecond time transfer over Ethernet/fibre |
| Phase-cal | Injected comb of tones used to track instrumental phase |
| Noise diode | Injected known noise for amplitude calibration |

## Correlation and reduction

| Term | Meaning |
|:---|:---|
| Correlator | Multiplies signals from antenna pairs to form visibilities |
| FX correlator | Fourier-transform first, then cross-multiply — SFXC and DiFX are FX |
| SFXC / DiFX | Software correlators, MPI-based, used by JIVE and EVN |
| Visibility | Complex correlated output per baseline, channel, time |
| Fringe fitting | Solving residual delay, rate and phase so visibilities add coherently |
| Bandpass | Frequency-dependent gain correction |
| Integration time | Time over which visibilities are averaged (2 s at Irbene) |
| FFT points / channels | Spectral resolution of the correlator pass |
| AIPS / CASA | Standard reduction packages; ParselTongue scripts AIPS from Python |
| FITS-IDI / Measurement Set (MS) | Visibility file formats produced by correlators |
| Dynamic spectrum / waterfall | 2-D array of intensity in time × frequency |
| Flag / mask | Boolean array marking samples as unusable |

## RFI

| Term | Meaning |
|:---|:---|
| RFI | Radio-frequency interference — human-made emission in the band |
| Narrowband / broadband / transient RFI | Persistent lines (GNSS, satellites), wide bursts (lightning, switching), intermittent (aircraft, vehicles) |
| AOFlagger / SumThreshold | De-facto standard rule-based flagger and its core algorithm |
| SSA | Singular Spectrum Analysis — decomposition that separates trend / periodic / noise components; VIRAC's chosen RFI method |
| Flag vs subtract | Flagging drops samples; subtraction (SSA-style) tries to remove the interferer and keep the signal |
| Weak labels / strong labels | Machine-generated flags (AOFlagger) vs expert hand-labelled masks |
| U-Net / Swin-UNETR | Image-segmentation network families used for RFI masks on spectrograms |
| Maser trap | Narrow spectral lines (masers) look like narrowband RFI to a naive flagger |

## Science

| Term | Meaning |
|:---|:---|
| Methanol maser (6.7 GHz) | Narrow-line emission tracing high-mass star formation; VIRAC's main monitoring target |
| OH maser (1.6 GHz) | Hydroxyl maser line at L band |
| Continuum | Broadband emission, as opposed to a spectral line |
| QPP | Quasi-periodic pulsations in flare emission (solar and stellar) |
| Accretion burst | Sudden infall event in a protostar; produces maser flares and continuum changes |
| GNSS as illuminator | Using navigation-satellite signals as the transmitter for ionosphere probing or forward-scatter radar |
| FSR | Forward-scatter radar — detecting objects via signals scattered toward the receiver |
| SLR | Satellite laser ranging |

## Compute

| Term | Meaning |
|:---|:---|
| HPC | High-performance computing cluster, typically scheduled by SLURM or PBS |
| MPI / OpenMPI | Explicit message passing between processes; standard for tightly coupled kernels |
| Dask | Python framework building task graphs over chunked arrays, scheduled across cores or nodes |
| dask-jobqueue / dask-mpi | Ways to launch Dask workers on SLURM / PBS / MPI clusters |
| Task granularity | Size of each Dask task; too small and scheduling dominates, too large and parallelism is lost |
| Strong scaling | Fixed problem size, more workers |
| Weak scaling | Problem size grows with worker count |
| GPU correlator | Correlation on GPUs (tensor cores); the RADIOBLOCKS deliverable for ISBI |
| AARTFAAC | Amsterdam-ASTRON transient facility whose correlator design VIRAC is following |

## Organisations and programmes

| Term | Meaning |
|:---|:---|
| VIRAC | Ventspils International Radio Astronomy Centre |
| VUAS | Ventspils University of Applied Sciences — operator of VIRAC |
| EVN / EVN-Lite | European VLBI Network and its smaller-array mode |
| JIVE | Joint Institute for VLBI ERIC — runs SFXC and EVN correlation |
| LOFAR / LV614 | Low-Frequency Array; Irbene's international station |
| RADIOBLOCKS | Horizon Europe project (2023–2027) on the radio-astronomy data chain |
| IVARS | VIRAC project on interferometric maser + continuum variability |
| STEF | VIRAC project on QPPs in solar and stellar flares |
