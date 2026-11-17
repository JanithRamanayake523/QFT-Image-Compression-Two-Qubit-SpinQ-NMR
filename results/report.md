# Verification report

Parameters: `{'n_law': 50000, 'n_mc': 20000, 'seed': 2026, 'qiskit': True}`

Summary: **FLAG** 1, **INFO** 4, **PASS** 70


## 1 Grayscale example

| Status | Check | Source | Expected | Recomputed | Tol |
|---|---|---|---|---|---|
| PASS | QFT matrix equals F4 of Eq. (3) | paper Eq. 3 | [[0.5, 0.5, 0.5, 0.5], [0.5, 0, -0.5, 0], [0.5, -0.5, 0.5, -0.5], [0.5, 0, -0.5, 0]] | [[0.5, 0.5, 0.5, 0.5], [0.5, 3.06162e-17, -0.5, -9.18485e-17], [0.5, -0.5, 0.5, -0.5], [0.5, -9.18485e-17, -0.5, 2.75546e-16]] | 1e-12 |
| PASS | QFT matrix imaginary part | paper Eq. 3 | [[0, 0, 0, 0], [0, 0.5, 0, -0.5], [0, 0, 0, 0], [0, -0.5, 0, 0.5]] | [[0, 0, 0, 0], [0, 0.5, 6.12323e-17, -0.5], [0, 6.12323e-17, -1.22465e-16, 1.83697e-16], [0, -0.5, 1.83697e-16, 0.5]] | 1e-12 |
| PASS | F4 is unitary | paper Sec. 2.1 | True | True | - |
| PASS | ||x||_2 = 50*sqrt(30) | paper Eq. 7 | 273.861 | 273.861 | 1e-09 |
| PASS | encoded state psi | paper Eq. 9 | [0.7303, 0.1826, 0.3651, 0.5477] | [0.730297, 0.182574, 0.365148, 0.547723] | 5e-05 |
| PASS | QFT coefficients y (real part) | paper Eq. 11 | [0.912871, 0.182574, 0.182574, 0.182574] | [0.912871, 0.182574, 0.182574, 0.182574] | 1e-12 |
| PASS | QFT coefficients y (imag part) | paper Eq. 11 | [0, -0.182574, 0, 0.182574] | [0, -0.182574, 6.70767e-17, 0.182574] | 1e-12 |
| PASS | coefficient magnitudes |y| | paper Eq. 12 | [0.9129, 0.2582, 0.1826, 0.2582] | [0.912871, 0.258199, 0.182574, 0.258199] | 5e-05 |
| PASS | energy shares before QFT | deck: Results energy slide | [0.533333, 0.0333333, 0.133333, 0.3] | [0.533333, 0.0333333, 0.133333, 0.3] | 1e-12 |
| PASS | energy shares after QFT | deck: Results energy slide | [0.833333, 0.0666667, 0.0333333, 0.0666667] | [0.833333, 0.0666667, 0.0333333, 0.0666667] | 1e-12 |
| PASS | selected set S = {0, 1} (tie -> smaller index) | paper Sec. 4.3 | True | True | - |
| PASS | retained energy (K=2) | paper Eq. 15 | 0.9 | 0.9 | 1e-12 |
| PASS | energy in y0 alone | paper Sec. 5.1 | 0.833333 | 0.833333 | 1e-12 |
| PASS | coefficient retention fraction | paper Table 1 | 0.5 | 0.5 | 0 |
| PASS | reconstructed vector x_hat | paper Eq. 19 | [158.114, 105.409, 105.409, 158.114] | [158.114, 105.409, 105.409, 158.114] | 0.0005 |
| PASS | MSE | paper Eq. 26 | 1229.93 | 1229.93 | 0.005 |
| PASS | PSNR (dB) | paper Eq. 27 | 17.23 | 17.232 | 0.005 |
| PASS | S={0,3} gives the same real reconstruction | paper Sec. 3.2 | [158.114, 105.409, 105.409, 158.114] | [158.114, 105.409, 105.409, 158.114] | 1e-09 |
| PASS | QFT -> IQFT without truncation returns the input | paper Sec. 4.2 | [200, 50, 100, 150] | [200, 50, 100, 150] | 1e-09 |

## 2 Circuit

| Status | Check | Source | Expected | Recomputed | Tol |
|---|---|---|---|---|---|
| PASS | manual circuit (H, CP, H, SWAP) equals F4 [NumPy] | paper Sec. 4.2 | [[0.5, 0.5, 0.5, 0.5], [0.5, 3.06162e-17, -0.5, -9.18485e-17], [0.5, -0.5, 0.5, -0.5], [0.5, -9.18485e-17, -0.5, 2.75546e-16]] | [[0.5, 0.5, 0.5, 0.5], [0.5, 3.06162e-17, -0.5, -3.06162e-17], [0.5, -0.5, 0.5, -0.5], [0.5, -3.06162e-17, -0.5, 3.06162e-17]] | 1e-12 |
| PASS | manual circuit imaginary part [NumPy] | paper Sec. 4.2 | [[0, 0, 0, 0], [0, 0.5, 6.12323e-17, -0.5], [0, 6.12323e-17, -1.22465e-16, 1.83697e-16], [0, -0.5, 1.83697e-16, 0.5]] | [[0, 0, 0, 0], [0, 0.5, 0, -0.5], [0, 0, 0, 0], [0, -0.5, 0, 0.5]] | 1e-12 |
| PASS | inverse circuit equals F4-dagger [NumPy] | paper Sec. 4.2 | [[0.5, 0.5, 0.5, 0.5], [0.5, 3.06162e-17, -0.5, -9.18485e-17], [0.5, -0.5, 0.5, -0.5], [0.5, -9.18485e-17, -0.5, 2.75546e-16]] | [[0.5, 0.5, 0.5, 0.5], [0.5, 3.06162e-17, -0.5, -3.06162e-17], [0.5, -0.5, 0.5, -0.5], [0.5, -3.06162e-17, -0.5, 3.06162e-17]] | 1e-12 |
| PASS | classical FFT reference equals y | paper Sec. 4.1 step 5 | [0.912871, 0.182574, 0.182574, 0.182574] | [0.912871, 0.182574, 0.182574, 0.182574] | 1e-12 |
| PASS | classical FFT reference (imag) | paper Sec. 4.1 step 5 | [0, -0.182574, 6.70767e-17, 0.182574] | [0, -0.182574, 0, 0.182574] | 1e-12 |
| PASS | manual circuit equals F4 [Qiskit Operator] | paper Sec. 4.2 | [[0.5, 0.5, 0.5, 0.5], [0.5, 3.06162e-17, -0.5, -9.18485e-17], [0.5, -0.5, 0.5, -0.5], [0.5, -9.18485e-17, -0.5, 2.75546e-16]] | [[0.5, 0.5, 0.5, 0.5], [0.5, 3.06162e-17, -0.5, -3.06162e-17], [0.5, -0.5, 0.5, -0.5], [0.5, -3.06162e-17, -0.5, 3.06162e-17]] | 1e-09 |
| PASS | manual circuit imaginary part [Qiskit] | paper Sec. 4.2 | [[0, 0, 0, 0], [0, 0.5, 6.12323e-17, -0.5], [0, 6.12323e-17, -1.22465e-16, 1.83697e-16], [0, -0.5, 1.83697e-16, 0.5]] | [[0, 0, 0, 0], [0, 0.5, 0, -0.5], [0, 0, 0, 0], [0, -0.5, 0, 0.5]] | 1e-09 |
| PASS | Qiskit built-in QFT equals F4 | paper Sec. 4.2 | [[0.5, 0.5, 0.5, 0.5], [0.5, 3.06162e-17, -0.5, -9.18485e-17], [0.5, -0.5, 0.5, -0.5], [0.5, -9.18485e-17, -0.5, 2.75546e-16]] | [[0.5, 0.5, 0.5, 0.5], [0.5, 3.06162e-17, -0.5, -9.18485e-17], [0.5, -0.5, 0.5, -0.5], [0.5, -9.18485e-17, -0.5, 2.75546e-16]] | 1e-09 |
| PASS | Qiskit built-in QFT imaginary part | paper Sec. 4.2 | [[0, 0, 0, 0], [0, 0.5, 6.12323e-17, -0.5], [0, 6.12323e-17, -1.22465e-16, 1.83697e-16], [0, -0.5, 1.83697e-16, 0.5]] | [[0, 0, 0, 0], [0, 0.5, 6.12323e-17, -0.5], [0, 6.12323e-17, -1.22465e-16, 1.83697e-16], [0, -0.5, 1.83697e-16, 0.5]] | 1e-09 |
| PASS | Aer 2048-shot probabilities vs |y|^2 (max abs gap) | paper Sec. 4.4 | [0.833333, 0.0666667, 0.0333333, 0.0666667] | [0.842773, 0.0668945, 0.0297852, 0.0605469] | 0.04 |

## 3 SpinQ hardware

| Status | Check | Source | Expected | Recomputed | Tol |
|---|---|---|---|---|---|
| PASS | Example 1: mean absolute error | paper Table 3 | 0.0315 | 0.0315 | 6e-05 |
| PASS | Example 1: maximum absolute error | paper Table 3 | 0.063 | 0.063 | 0.0006 |
| PASS | Example 1: total variation distance | paper Table 3 | 0.063 | 0.063 | 0.0006 |
| PASS | Example 1: measured probabilities sum to 1 | paper Sec. 5.2 | 1 | 1 | 0.0025 |
| PASS | Example 2: mean absolute error | paper Table 3 | 0.025 | 0.025 | 6e-05 |
| PASS | Example 2: maximum absolute error | paper Table 3 | 0.025 | 0.025 | 0.0006 |
| PASS | Example 2: total variation distance | paper Table 3 | 0.05 | 0.05 | 0.0006 |
| PASS | Example 2: measured probabilities sum to 1 | paper Sec. 5.2 | 1 | 1 | 0.0025 |
| PASS | Example 3: mean absolute error | paper Table 3 | 0.118 | 0.118 | 6e-05 |
| PASS | Example 3: maximum absolute error | paper Table 3 | 0.177 | 0.177 | 0.0006 |
| PASS | Example 3: total variation distance | paper Table 3 | 0.236 | 0.236 | 0.0006 |
| PASS | Example 3: measured probabilities sum to 1 | paper Sec. 5.2 | 1 | 1 | 0.0025 |
| PASS | Example 4: mean absolute error | paper Table 3 | 0.0555 | 0.0555 | 6e-05 |
| PASS | Example 4: maximum absolute error | paper Table 3 | 0.056 | 0.056 | 0.0006 |
| PASS | Example 4: total variation distance | paper Table 3 | 0.111 | 0.111 | 0.0006 |
| PASS | Example 4: measured probabilities sum to 1 | paper Sec. 5.2 | 1 | 1.002 | 0.0025 |
| PASS | overall mean absolute difference (16 probabilities) | paper Sec. 5.3 | 0.0575 | 0.0575 | 5e-05 |
| PASS | ranking by MAE: Example 2 < 1 < 4 < 3 | deck: Probability errors slide | True | True | - |
| PASS | Example 1: printed T equals T from the stated matrix | paper Table 2 | [0.5, 0, 0, 0.5] | [0.5, 0, 0, 0.5] | 1e-09 |
| PASS | Example 2: printed T equals T from the stated matrix | paper Table 2 | [0.5, 0.5, 0, 0] | [0.5, 0.5, 0, 0] | 1e-09 |
| FLAG | Example 3: printed T vs T from the stated matrix | paper Table 2 | [0, 0.5, 0, 0.5] | [0, 0.5, 0.5, 0] | - |
| PASS | Example 4: printed T equals T from the stated matrix | paper Table 2 | [0.25, 0.25, 0.25, 0.25] | [0.25, 0.25, 0.25, 0.25] | 1e-09 |

## 4 Analysis

| Status | Check | Source | Expected | Recomputed | Tol |
|---|---|---|---|---|---|
| PASS | coefficient closed forms (brightness / left-right / top-bottom) | analysis | True | True | - |
| PASS | K=1 reconstruction is one flat value 136.9 | deck: Analysis K sweep | [136.9, 136.9, 136.9, 136.9] | [136.931, 136.931, 136.931, 136.931] | 0.05 |
| PASS | K=1 PSNR | deck: Analysis K sweep | 13 | 12.9889 | 0.05 |
| PASS | K=2 PSNR | deck: Analysis K sweep | 17.2 | 17.232 | 0.05 |
| PASS | K=3 PSNR | deck: Analysis K sweep | 20.1 | 20.1354 | 0.05 |
| PASS | K=4 returns the image exactly (MSE) | deck: Analysis K sweep | 0 | 2.52435e-28 | 1e-09 |
| PASS | smooth image B: PSNR at K=1 | deck: Analysis eight test images | 33.2 | 33.1794 | 0.1 |
| PASS | smooth image B: PSNR at K=3 | deck: Analysis eight test images | 46.2 | 46.1932 | 0.1 |
| PASS | gradient C stays below 16 dB at K=3 | deck: Analysis eight test images | True | True | - |
| PASS | single bright pixel E: PSNR at K=3 (about 16 dB) | deck: Analysis eight test images | 16 | 15.9653 | 0.1 |
| PASS | single bright pixel E spreads energy evenly | deck: Analysis eight test images | [0.25, 0.25, 0.25, 0.25] | [0.25, 0.25, 0.25, 0.25] | 1e-12 |
| PASS | images reconstructed exactly (missing bars): F all K; D,G at K=3; H at K=2,3 | deck: Analysis eight test images | True | True | - |
| PASS | exact MSE law (179531 comparisons on 50000 random images, max |pred-sim|/||x||^2 = 2.22e-16) | deck: Analysis error and brightness | True | True | - |
| PASS | PSNR gain per halving of brightness (dB) | deck: Analysis error and brightness | 6.0206 | [6.0206, 6.0206, 6.0206] | 1e-06 |
| PASS | relative error stays 6.6% at every brightness | deck: Analysis error and brightness | [0.0656, 0.0656, 0.0656, 0.0656] | [0.0655964, 0.0655964, 0.0655964, 0.0655964] | 0.0005 |
| INFO | renormalised vs classical-deletion MSE ratio (K=1,2,3) | analysis | - | [1.04555, 0.983946, 1.00848] | - |

## 5 Monte Carlo

| Status | Check | Source | Expected | Recomputed | Tol |
|---|---|---|---|---|---|
| PASS | uniform random images: median PSNR at K=2 | deck: Is the initial example typical | 17.7 | 17.7596 | 0.3 |
| PASS | smooth images: median PSNR at K=2 (about 34 dB) | deck: Is the initial example typical | 34 | 33.8399 | 0.7 |
| PASS | high-contrast images: median PSNR at K=2 (about 21 dB) | deck: Is the initial example typical | 21 | 20.619 | 0.7 |
| PASS | DC coefficient always holds at least 25% of the energy (non-negative pixels) | deck: Is the initial example typical | True | True | - |
| PASS | left-right coefficient outranks the pair (about 41%) | deck: Is the initial example typical | 0.41 | 0.40975 | 0.02 |
| INFO | median PSNR K=1,2,3 (uniform) | analysis | - | [12.1138, 17.7596, 24.5462] | - |
| INFO | median PSNR K=1,2,3 (smooth) | analysis | - | [28.7916, 33.8399, 40.4023] | - |
| INFO | median PSNR K=1,2,3 (high contrast) | analysis | - | [15.2961, 20.619, 27.1588] | - |

## Items to review

- **FLAG** Example 3: printed T vs T from the stated matrix: The stated input matrix [[0,1],[1,0]] amplitude-encodes to probability 0.5 on |01> and |10>, but the table lists 0.5 on |01> and |11>. Table 3 values follow the LISTED T. Check with the experimenters which pattern was actually run (e.g. [[0,1],[0,1]] gives |01>,|11>).
