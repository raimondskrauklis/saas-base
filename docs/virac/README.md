# docs/virac/README.md

# VIRAC collaboration

Planning docs for work with the Ventspils International Radio Astronomy Centre on RFI mitigation and HPC data processing.

| File | What |
|:---|:---|
| [VIRAC_COLLABORATION_FINDINGS.md](VIRAC_COLLABORATION_FINDINGS.md) | Baseline findings: what exists at VIRAC and in saas-base, two tracks, decisions registry |
| [RFI_LUMI_FINDINGS.md](RFI_LUMI_FINDINGS.md) | The problem itself: data shapes and volumes, LUMI-G / LUMI-C / storage / billing, Irbene → LUMI transfer, RFI method stack, obstacles, research backlog |
| [RFI_LUMI_GENERAL_PLAN.md](RFI_LUMI_GENERAL_PLAN.md) | Phased plan P0–P6: LUMI foundations, first sample, baselines, weak-label model, Dask vs MPI benchmark, second wave, hand-over |

Sourced facts about the site and instruments: [`corpus/irbene/`](../../corpus/irbene/README.md). Meeting notes are in `internal-docs/virac/` (gitignored, contributors with access).

Execution plans follow once Q-A1–Q-A3 and Q-A9 in the RFI/LUMI findings are resolved (VIRAC meeting + `lumi-allocations`).
