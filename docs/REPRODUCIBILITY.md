# Reproducibility

## Environment used for the reference results

| Item | Version |
|---|---|
| Python | 3.13.11 |
| NumPy | 2.4.6 |
| Qiskit / Qiskit Aer | 2.4.1 / 0.17.2 |
| Matplotlib (figures only) | 3.11.0 |
| pytest | 9.0.2 |
| OS | Windows 11 |

The code also targets Python 3.10 and later; CI runs 3.10, 3.12 and 3.13 on Ubuntu.

## Randomness

All random studies use `numpy.random.default_rng(seed)` with the default seed **2026**:

| Study | Size |
|---|---|
| Exact error-law check | 50,000 random images, K = 1 to 4 |
| Monte Carlo (uniform, smooth, high contrast) | 20,000 images per group |
| Aer shot experiment | 2048 shots, simulator seed 2026 |

Statistical checks use tolerances that widen for small samples. Re-run with other seeds to confirm the claims
do not depend on one seed, for example `python scripts/run_all.py --seed 7 --n-mc 100000 --n-law 200000`.

## Expected output

`python scripts/run_all.py` prints `SUMMARY: {'PASS': 70, 'FLAG': 1, 'INFO': 4}` and exits with code 0.
The single FLAG is SpinQ Example 3 (printed theory versus the theory implied by the stated input matrix).
The full table of recomputed versus reported values is in [`results/report.md`](../results/report.md).

Reference statistics (seed 2026, 20,000 images per group), median PSNR for K = 1, 2, 3:

| Group | K = 1 | K = 2 | K = 3 |
|---|---|---|---|
| Uniform random | 12.1 dB | 17.8 dB | 24.5 dB |
| Smooth plus small noise | 28.8 dB | 33.8 dB | 40.4 dB |
| High contrast | 15.3 dB | 20.6 dB | 27.2 dB |

## What cannot be reproduced here

* The SpinQ NMR measurements: the values come from the study's table (`data/spinq_measurements.csv`); raw
  instrument output and repeated runs are not available.
* Claims about natural images or larger sizes: not studied.
