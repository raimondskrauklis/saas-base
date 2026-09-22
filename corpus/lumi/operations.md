# corpus/lumi/operations.md

# LUMI — operational facts

Source keys resolve in [`corpus/irbene/sources.md`](../irbene/sources.md).

## Storage semantics

| Fact | Source |
|:---|:---|
| Scratch (`/scratch/project_46YXXXXXX`) files "can in principle be erased automatically after 90 days"; not active yet, will be activated if the space fills | ACC |
| Storage is billed per hour of use (TB-hours), not peak — designed to reward deleting intermediate data promptly | ACC |
| `/flash` is SSD-backed but still a parallel networked filesystem: open/close and metadata cost stays high; the win is bandwidth on large, well-striped accesses | ACC |
| LUMI is not an archive or publishing service. "Permanent" means for the project lifetime. **No backup, including home.** 90 days after project end all project data is irrevocably deleted. Accounts without a project, or inactive for months, are closed | ACC |
| Lustre redundancy protects against single (often dual) disk failure; server-pair failures making data temporarily inaccessible have happened. Treat Lustre as fast, not safe | ACC |
| LUMI-O data: not deleted while a project is valid; read-only for a 90-day grace period after project end; then queued for deletion. Sharing a bucket with project B does not protect it when project A ends | ACC |
| Default Lustre striping for projects created from May 2026: Progressive File Layout — 1 stripe ≤ 256 MB; 256 MB–16 GB over 4 OSTs (LUMI-P) / 8 (LUMI-F); ≥ 16 GB over 8 / 16. Earlier projects: no default striping | LUS |
| Striping guidance: stripe count > 1 only for large shared files accessed by many processes; stripe count 1 for file-per-process; stripe size 1–4 MB typical, min 512 KB, max 4 GB | LUS |

## Data transfer

| Fact | Source |
|:---|:---|
| `sftp` / `rsync`-over-SSH to login nodes works but is a single TCP stream: effective bandwidth falls with latency, and "the biggest contributor to the latency was actually the campus network of the user" in many support cases | ACC |
| Recommended path for large data: push to LUMI-O from the source site, pull from LUMI-O on LUMI (and the reverse for egress). Object tools open multiple streams and reach far higher throughput on long-distance links | ACC |
| No Globus / GridFTP support. A recipe exists for the UNICORE UFTP client but LUST cannot support it (no server access) | ACC |
| LUMI-O ↔ LUMI network bandwidth is "a lot less" than Lustre OSS ↔ compute (which sit on the same Slingshot fabric). Stage once, reuse many times | ACC |
| Multipart uploads (`s3cmd`, `rclone`) parallelise a single object; interrupted uploads leave parts as live objects that consume quota unless a bucket lifecycle policy cleans them. A user has depleted their LUMI-O quota this way | ACC |
| LUMI-O runs on a stack independent from LUMI and is usually up during LUMI downtimes; credentials at `auth.lumidata.eu` likewise | LUO, ACC |

## LUMI-O access model

| Fact | Source |
|:---|:---|
| Credentials: `auth.lumidata.eu` (independent of LUMI; key lifetime up to 1 year) or the Open OnDemand "Cloud storage configuration" app (creates 7-day keys, only recognises keys described "lumi web interface") | ACC |
| Endpoint URL `https://lumidata.eu/`; **path-style addressing only** (`https://projectnum.lumidata.eu/bucket`); virtual-hosted style unsupported because the wildcard cert covers one subdomain level. Some SDKs (notably `aws-sdk` on public buckets) need `use_path_style` / `force_path_style` / `S3_FORCE_PATH_STYLE` | ACC |
| `module load lumio` provides `rclone`, `s3cmd`, `restic` and the `lumio-conf` tool, which writes two `rclone` remotes per project — `lumi-46YXXXXXX-private` and `lumi-46YXXXXXX-public` — plus an `s3cmd` config (`~/.s3cfg-lumi-46YXXXXXX`, select with `-c`). `aws` CLI and `boto3` are not preinstalled | ACC |
| The same generated `rclone` snippet works unchanged on any external machine — there is no difference between accessing LUMI-O from LUMI or from elsewhere | ACC |
| Which remote you upload through sets the ACL of the created object (private vs public-readable). Public objects are web-readable at `https://lumidata.eu/<project>:<bucket>/<object>` or `https://<project>.lumidata.eu/<bucket>/<object>`. A private bucket may hold public objects and vice versa | ACC |
| `s3cmd setacl --recursive --acl-public s3://bucket/` / `--acl-private` toggle visibility; `s3cmd info` shows ACLs and policies. Bucket policies are the finer mechanism; ACLs only add rights | ACC |
| `rclone` FUSE-mounting buckets as a filesystem is not recommended on LUMI | ACC |
| LUMI-O is suited for sharing between projects and with the outside world, but is explicitly not a publication service (EUDAT is named for that) | ACC |

## GPU jobs with PyTorch containers

| Fact | Source |
|:---|:---|
| Official PyTorch containers are built by AMD for LUMI: matching ROCm, RCCL plugin for Slingshot, apex, torchvision/torchdata/torchtext/torchaudio. Loaded as EasyBuild modules, e.g. `PyTorch/2.7.0-rocm-6.2.4-python-3.12-singularity-20250527`; the module sets `$SIF`, `$SIFPYTORCH`, `$SINGULARITY_BIND` (project/scratch/flash mounted) and exposes `/runscripts` wrappers (`python`, `start-shell`, `conda-python-simple`) | PYT |
| Containers built with `cotainr` on the ROCm base containers follow the same instructions | PYT |
| Do **not** also load `singularity-AI-bindings` when using these modules — already included | PYT |
| Reference multi-node job: `--partition=standard-g --nodes=N --gpus-per-node=8 --tasks-per-node=8 --cpus-per-task=7 --mem=480G` | PYT |
| `MIOPEN_USER_DB_PATH` and `MIOPEN_CUSTOM_CACHE_DIR` must point to `/tmp/<user>-miopen-cache-$SLURM_NODEID` — MIOpen's cache fails on Lustre due to file-locking; recreate per job | PYT |
| `NCCL_SOCKET_IFNAME=hsn0,hsn1,hsn2,hsn3` — otherwise RCCL tries an interface it cannot use | PYT |
| `ROCR_VISIBLE_DEVICES=$SLURM_LOCALID` pins one GCD per task; check affinity with `taskset -p $$` | PYT |
| Standard PyTorch DDP env (`MASTER_ADDR`, `MASTER_PORT`, `WORLD_SIZE`, `RANK`) as on NVIDIA systems; a fixed port means two half-node jobs cannot share a node | PYT |
| `SINGULARITYENV_<VAR>` prepends inject env into the container and override container-set values | PYT |

## Implications used in planning

- Latvian copy is the backup; LUMI holds working copies only.
- Every job: pull from LUMI-O → scratch once, `/flash` only for the active training set, delete intermediates promptly.
- One `rclone` config generated once at `auth.lumidata.eu`, shared with the VIRAC-side sender; token lifetime ≥ campaign length.
- Bucket lifecycle policy for aborted multipart uploads set on day one.
- Every GPU job template starts from the PYT reference script.
