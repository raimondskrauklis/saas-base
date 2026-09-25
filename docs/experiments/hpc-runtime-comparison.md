# HPC runtime comparison

One synthetic kernel, three CPU launchers, and a separate GPU check. The CPU launchers computed the same windows. The GPU check is not part of that comparison.

## Kernel

Each window `w` is a 256×256 matrix of uniform random values from a fixed seed, `20260926 + w`. The work per window is a singular-value decomposition. The result is one checksum: SHA-256 of the singular values, concatenated in window order, as little-endian float64.

The frozen size is 512 windows. Every process sets one BLAS thread before NumPy is imported (`OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`).

## CPU stack

The three CPU runs used one container on one node. The probe printed:

```
Python 3.14.7
dask 2026.8.0
mpi4py 4.1.2
MPI Open MPI v5.0.11, package: Open MPI rattler@86e0e58551c1 Distribution, ident: 5.0.11, repo rev: v5.0.11rc1, Sep 16, 2026
```

## How the three launchers ran

Serial used one process and one CPU. It computed every window in order.

MPI used four ranks inside that same container. One allocated task held four CPUs. `mpirun --bind-to none -n 4` started the kernel. Rank `r` owned windows where `w % 4 == r`. Rank 0 gathered the pairs, sorted them by window index, and printed the checksum. The library line and `mpi_size 4` come from that rank. The four ranks shared the CPU set `[0, 13, 17, 19]`. This was Open MPI via `mpirun`. It was not `dask-mpi`.

Dask used one process on four CPUs. That process started `LocalCluster(n_workers=4, threads_per_worker=1, processes=True)`, mapped the windows in index order, and gathered the results in that same order before the checksum.

## CPU results

| Launcher | Checksum | Wall time |
|:---|:---|:---|
| Serial, 1 process | `0ceb53337f8e80b2c6b322519c970b0e2c5e84797219170bee610cd8c99af548` | 3.296969 s |
| Open MPI, 4 ranks | `0ceb53337f8e80b2c6b322519c970b0e2c5e84797219170bee610cd8c99af548` | 1.488767 s |
| Dask, 4 workers | `0ceb53337f8e80b2c6b322519c970b0e2c5e84797219170bee610cd8c99af548` | 3.027481 s |

The three checksums match. The wall times are this kernel, this shape, and this one-thread setup.

### Serial log

```
mode serial
windows 512
matrix 256
checksum 0ceb53337f8e80b2c6b322519c970b0e2c5e84797219170bee610cd8c99af548
wall_s 3.296969
```

### MPI log

```
mode mpi
windows 512
matrix 256
checksum 0ceb53337f8e80b2c6b322519c970b0e2c5e84797219170bee610cd8c99af548
wall_s 1.488767
mpi_library Open MPI v5.0.11, package: Open MPI rattler@86e0e58551c1 Distribution, ident: 5.0.11, repo rev: v5.0.11rc1, Sep 16, 2026
mpi_size 4
```

### Dask log

```
mode dask
windows 512
matrix 256
checksum 0ceb53337f8e80b2c6b322519c970b0e2c5e84797219170bee610cd8c99af548
wall_s 3.027481
```

## GPU check

A second job ran one array operation on an AMD Instinct GPU. It is not a fourth row in the table above.

The operation builds a 4×4 matrix of ones in float64 on the GPU, multiplies it by itself, and sums the result. The expected sum is 64. The job printed `array_op 64.0`.

The device log:

```
GPU[0]		: VRAM Total Memory (B): 68702699520
GPU[0]		: VRAM Total Used Memory (B): 10985472
GPU[0]		: Card Series: 		AMD INSTINCT MI200 (MCM) OAM LC MBA HPE C2
GPU[0]		: Card Model: 		0x7408
GPU[0]		: Card Vendor: 		Advanced Micro Devices, Inc. [AMD/ATI]
GPU[0]		: Card SKU: 		D65201
GPU[0]		: GFX Version: 		gfx9010
array_op 64.0
```
