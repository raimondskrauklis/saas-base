# DigitalOcean Spaces (object storage)

All our products use **DigitalOcean Spaces** (S3-compatible). This template does **not** ship MinIO. Local and production both talk to Spaces (dev bucket vs prod bucket).

**Not implemented in saas-base yet.** W6 account export still writes ZIPs to `EXPORT_STORAGE_PATH` (`/tmp/app/exports`). When the storage adapter lands, that path becomes a Spaces key prefix. KP’s battle-tested client: `kp-platform/backend/app/services/storage.py` (boto3, private ACL, presigned GET, spool-to-disk, filename sanitization). Do not copy KP tender-docs / ETL key layouts or the anonymization pipeline.

**Related:** KP `STORAGE_*` / `DO_KP_FILES_BUCKET` · this clone will use the same env **names** as KP except the bucket var is generic.

---

## 1. Bucket per clone

1. DigitalOcean → **Spaces** → Create bucket (region **fra1** unless the clone is elsewhere).
2. **File listing:** restrict. Objects stay **private**.
3. Create a Spaces **access key** (Access Key + Secret). One key per environment if you can.
4. Optional CDN endpoint — only if you later serve public assets. Default: **no public ACL**; downloads use **presigned GET**.

Do not share a bucket across products. Prefixes inside one bucket (`etl/`, `tender-docs/`) are a KP pattern; a new clone gets a **new bucket**.

---

## 2. Environment

```text
STORAGE_ACCESS_KEY=...
STORAGE_SECRET_KEY=...
STORAGE_REGION=fra1
STORAGE_ENDPOINT=https://fra1.digitaloceanspaces.com
STORAGE_BUCKET=your-clone-files
STORAGE_SIGNED_URL_TTL_SECONDS=900
STORAGE_MAX_UPLOAD_MB=25
```

Use the **regional** endpoint (`https://fra1.digitaloceanspaces.com`), not `https://bucket.fra1.digitaloceanspaces.com`. Passing the bucket hostname into boto3 double-buckets the URL.

CORS: not required if the API uploads server-side (the default). Browser PUT to Spaces would need a CORS rule on the bucket — do not add that until a product actually needs it.

---

## 3. Adapter contract (when implemented)

| Operation | Behavior |
|-----------|----------|
| Upload | `upload_fileobj`, `ACL=private`, set Content-Type |
| Download | Server stream or **presigned GET** (TTL from env) |
| Delete | Best-effort; log failures |
| Key layout | `{workspace_id}/{purpose}/{uuid}_{safe_filename}` |
| Filename | Strip path segments; ASCII-safe tail (KP `sanitize_document_filename_component`) |
| Size | Enforce `STORAGE_MAX_UPLOAD_MB` with a running byte count; spool to disk (do not buffer 25 MB in RAM) |

Postgres should own metadata (`files` or equivalent): workspace, actor, key, content type, size, sha256. Spaces is not the access-control plane.

**Consumers, in order:** (1) W6 export ZIP off local disk, (2) workspace logo / optional avatar, (3) product attachments.

---

## 4. What not to copy from KP

- 300 MB ETL Range GET / CSV header prefix
- Content-addressed dataset keys without GC
- `FILE_PROCESSING_AND_ANONYMIZATION.md` (investigator LLM pipeline)
- Public CDN for private documents
