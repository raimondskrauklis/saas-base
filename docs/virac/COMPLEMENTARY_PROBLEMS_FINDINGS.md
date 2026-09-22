# docs/virac/COMPLEMENTARY_PROBLEMS_FINDINGS.md

# Complementary problems — what becomes possible with the IVARS archive next to LUMI compute

**Status:** draft; proposals, not commitments. Nothing here is agreed with VIRAC.
**Position:** VIRAC's two ideas (RFI mitigation with ML; Dask vs MPI on HPC) are first-class and come first — see [`VIRAC_COLLABORATION_FINDINGS.md`](VIRAC_COLLABORATION_FINDINGS.md). This doc lists problems we can propose *because* we hold the two pieces that matter — users with a real problem, and the data — and because Track B puts the entire archive next to large compute for the first time.
**Grounding:** VIRAC facts by key into [`corpus/irbene/facts.md`](../../corpus/irbene/facts.md); infrastructure by key into [`corpus/irbene/sources.md`](../../corpus/irbene/sources.md).

## 1. The enabling fact

Once Track B lands, the whole IVARS correlated archive (154 sessions, ~0.5 TB) and — if wanted — the single-dish maser archive (2017–, tens of GB) are on LUMI scratch, with a pipeline that runs end-to-end there and on VIRAC's cluster. Re-processing eight years of data uniformly becomes an afternoon, repeatable. Every problem below is a consequence of that; none is possible on 30 Xeon v3 nodes at the cadence science needs (IT18, G25).

## 2. Catalog

### C1 — Uniform archive re-processing → homogeneous IVARS catalogue with quality flags

**Problem.** The archive was reduced over years with evolving software (AIPS versions, ParselTongue changes, manual phase-cal — G25). Variability studies compare epochs reduced differently. **Proposal.** Re-reduce every session with one pinned pipeline version on LUMI; attach per-point quality flags (RFI mask origin, calibration residuals, Tsys) and full lineage. **Output.** One catalogue, one version, one provenance record per point. **Why VIRAC cares.** Their science is variability — flares, periodicity (G25, AB23) — and the first question any referee asks is whether the light curve changes are astrophysical or reduction artefacts. **Cost.** Compute is trivial on LUMI-C; the work is pinning the pipeline (Track B) and agreeing what "quality flag" means with the scientists.

### C2 — Cross-epoch consistency as the label source for maser-safe RFI

**Problem.** Nobody has strong RFI labels for Irbene, and a 6.7 GHz maser line looks like narrow-band RFI to every published detector (MES22, CMP24). **Observation.** 42 masers observed every 5–7 days for years (G25, AB23). A maser feature is persistent in velocity across sessions and drifts slowly; RFI is not epoch-consistent in the source frame. **Proposal.** Self-supervised labels from the archive: features stable in LSR velocity across N epochs are "line", features stable in sky frequency but not in velocity are "RFI", the rest is noise. Use as weak labels, validate against the review-loop strong labels. **Why it is interesting.** RFI-ML literature labels single spectrograms; an epoch-consistency prior is new and specific to a long-baseline monitoring programme. **Risk.** Fast maser variability (days) blurs the prior; test on the "must-never-flag" set first.

### C3 — Three-class anomaly detection: maser flare vs RFI vs instrument glitch

**Problem.** A sudden brightening in one session is either science (flare), interference, or the instrument (Tsys jump, receiver, correlator). Today a human decides. **Proposal.** Once C1 exists, train on the archive's own history: per-source baseline behaviour, with monitoring metadata (MDPS JSON, Tsys) as side channels. Output is a triage label with confidence, surfaced in the review loop. **Why VIRAC cares.** Their alert-style science (flares) depends on trusting the alert. **Dependence.** C1 catalogue; monitoring metadata retention (ask).

### C4 — Residual delay / phase solving in the reduction pipeline

**Problem.** Named by VIRAC as an acknowledged open optimisation item (G25, Burns et al. in prep). **Proposal.** Bounded engineering task inside Track B: implement, test for equivalence against the current manual step, measure on LUMI. **Why it is good.** They named it; it is concrete; it lands inside the pipeline we are already building. **Ask first:** what exactly is unsolved — algorithm, automation, or runtime.

### C5 — Empirical Irbene RFI occupancy map

**Problem.** Site RFI is described qualitatively (DVB-T, GSM, radar pulses, wind-turbine scatter — Q-A6 in the RFI/LUMI findings). **Proposal.** From the archive: time × frequency × years occupancy statistics per band, from baseline flags (P2) with no ML needed. **Output.** A site RFI atlas — which channels, which hours, which seasons, trend over years. **Why VIRAC cares.** Useful for scheduling, for the radio-quiet-zone case, and for planning the 2026 receiver work (TOG25). Also a public-friendly artefact for the corpus if they agree.

### C6 — Single-dish archive joins the interferometric one

**Problem.** Two archives of the same masers on the same site, never analysed jointly. **Proposal.** Once Q-A1 (time-resolved dumps) is known, align single-dish and ISBI light curves per source; use the dish as an independent check on flare reality and on RFI (uncorrelated RFI drops in cross-correlation — G25). **Dependence.** Q-A1; C1.

## 3. Ordering and dependencies

C4 lives inside Track B and can start immediately. C1 is the flagship artefact and needs Track B pinned. C5 needs only P2 baselines. C2 feeds Track A and needs the archive staged (P1). C3 and C6 follow C1.

## 4. What we do not propose

- Anything touching the correlator or baseband (parked; see RFI/LUMI findings §11).
- New observing modes or hardware.
- Science interpretation — catalogue and flags, yes; astrophysical claims, VIRAC's.

## 5. Decisions registry

| Q# | Question | Status |
|:---|:---|:---|
| Q-C1 | Which of C1–C6 VIRAC wants at all; which first | open — raise after their two tracks are agreed, not before |
| Q-C2 | Is a re-reduced catalogue publishable, and under whose name | open |
| Q-C3 | What "residual delay/phase solving" actually means as an open item | open — ask |
| Q-C4 | Monitoring metadata retention (MDPS JSON, Tsys) across the archive | open — needed for C3 |

## 6. Devil's advocate

- **We are proposing science to scientists.** Frame every item as infrastructure that makes *their* science faster; the interpretation is theirs. If they do not want C1, nothing here happens, and Tracks A/B still stand alone.
- **C2 may not work.** Maser variability on day scales could break the epoch prior. It is a hypothesis with a cheap test, not a plan.
- **Scope creep is the real risk.** Six items on top of two tracks is too many. The point of this doc is to have them written down so we pick one, not six.

## 7. References

Keys resolve in [`corpus/irbene/sources.md`](../../corpus/irbene/sources.md): G25, AB23, IT18, MDPS, TOG25, MES22, CMP24.
