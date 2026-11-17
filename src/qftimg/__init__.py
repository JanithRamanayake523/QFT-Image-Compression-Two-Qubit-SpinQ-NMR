"""Reproducible two-qubit QFT image-compression study.

Modules
-------
core       QFT matrix, amplitude encoding, top-K truncation, reconstruction, MSE/PSNR
circuits   gate-level QFT (NumPy) and optional Qiskit / Aer cross-checks
hardware   SpinQ NMR probability table and the descriptive error metrics
analysis   additional analysis: K sweep, eight test images, exact error law,
           brightness scaling, renormalisation penalty, Monte Carlo
verify     runs every check and compares it with the expected (reported) value
"""
from .core import (qft_matrix, amplitude_encode, select_top_k, compress, mse, psnr,  # noqa: F401
                   energy_shares, CompressionResult)
