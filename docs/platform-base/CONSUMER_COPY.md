# Copy saas-base into a consumer repo

Recipe for P5. Copy the **whole** tagged `saas-base-v2` tree. Do not clone this repo over the consumer folder. Do not copy a directory menu. Do **not** record the tag SHA here — that lives in the follow-up docs commit after the tag exists.

**Source:** annotated tag `saas-base-v2` on `raimondskrauklis/saas-base`.  
**Example consumer:** `../irbene_gate`.

## Out-list (skip — do not overwrite)

These paths stay the consumer’s:

- `docs/vision.md`
- `docs/platform-base/`
- `palantir/`
- `polimi/`
- `exercises/`
- root learning `Pipfile` and `Pipfile.lock` (app Pipfile stays `backend/Pipfile`)
- consumer root `.env.example`

If a source path would replace an Out-list file, skip it.

## `.gitignore`

**Merge**, do not replace. Keep the consumer’s learning-dir ignores. Add missing template rules (at least `node_modules/`, frontend `dist` / `*.local`, `backend/.venv`, `.env` files with the template exceptions for `*.example`).

## Copy

From a checkout of `saas-base-v2`, copy every path except the Out-list into the consumer working tree. App env examples live under `backend/.env.example`, `frontend/.env.example`, and `deploy/env-examples/` — those **are** copied. Root `.env.example` on the consumer is Out-list.

After copy, note the upstream tag name in the **consumer** `docs/platform-base/` (consumer-owned; not this template file).

Then overlay identity (P6): app name, realm, hosts, DB URLs. Do not import ontology tables.
