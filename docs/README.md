# docs/

Each program has its own folder. Do not drop program files in this root.

| Folder | What |
|--------|------|
| [platform-base/](platform-base/README.md) | This template: strip Revy product, port auth, tag `saas-base-v2` |
| [mini-saas/](mini-saas/README.md) | Users directory + what else belongs in the mini template |
| [starter-pack/](starter-pack/README.md) | Scaffold runbooks (login, Keycloak, bootstrap) |
| [saas-base/](saas-base/README.md) | W0–W8 already in the frozen shell |
| [agents/](agents/README.md) | Agent LOOP orchestration |
| [utils/](utils/README.md) | Shared ops runbooks (Keycloak, Mailgun, Spaces, DB, Stripe, API keys) |
| [virac/](virac/README.md) | VIRAC collaboration: RFI review loop + Dask-on-HPC findings, meeting prep |

Sourced domain facts live outside `docs/`: [`corpus/irbene/`](../corpus/irbene/README.md).
