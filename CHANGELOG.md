# Changelog

## 1.0.0

* Reproduction and verification package for the two-qubit QFT image-compression study presented at the
  Colombo Quantum Computing Meetup (CQCM) 2026.
* `qftimg` package: pipeline, gate-level QFT with Qiskit / Aer cross-checks, SpinQ error metrics, additional
  analysis (K sweep, eight test images, exact MSE law, brightness effect, Monte Carlo).
* `scripts/run_all.py` verification (70 PASS, 1 FLAG, 0 FAIL) and a pytest suite.
* SpinQ measurements published as `data/spinq_measurements.csv`.
* Known item: SpinQ Example 3 printed theory differs from the theory implied by the stated input matrix.
