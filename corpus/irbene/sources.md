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
