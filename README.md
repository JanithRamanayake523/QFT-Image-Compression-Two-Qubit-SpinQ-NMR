# qftimg: two-qubit QFT image compression, reproduced and verified

Reproduction and verification code for the study **"Quantum Fourier Transform for Image Compression:
A Two-Qubit Simulation and SpinQ NMR Demonstration"** (Marapperuma, Rashmika, Vindula, Chinthila;
Research and Development Centre for Mathematical Modelling, University of Colombo).

A 2 x 2 grayscale image is amplitude-encoded on two qubits, transformed with the Quantum Fourier Transform
(QFT), compressed by keeping the K largest coefficients, renormalised, and reconstructed with the inverse
QFT. This repository recomputes **every number reported in the study and in our presentation**, including
our additional analysis, and compares each with the reported value. One command prints a PASS / FAIL
table so that anyone can check the results independently.

> **Scope.** A four-pixel, two-qubit toy model. It is a transparent baseline, **not** evidence of scalable or
> practical image compression, and not a claim of quantum advantage. The coefficient-selection step uses
> full statevector access, which a real device does not provide. The SpinQ hardware measurements are taken
> from the study's table; this code cannot re-measure them.

## Pipeline

```
image -> x (row-major) -> |psi> = x/||x|| -> y = F4 |psi> -> keep top-K -> renormalise -> F4^dagger -> Re, x ||x|| -> image
```

Worked example (`[[200, 50], [100, 150]]`, K = 2):

| Quantity | Value |
|---|---|
| ‖x‖ | 50·√30 ≈ 273.86 |
| QFT coefficients y | (1/√30)·[5, 1−i, 1, 1+i] |
| Energy per coefficient | 83.3 %, 6.7 %, 3.3 %, 6.7 % (energy kept by the top two: 90 %) |
| Reconstruction | [158.114, 105.409, 105.409, 158.114] |
| MSE / PSNR | 1229.93 / 17.23 dB |

## Install and run

```bash
git clone <this repository>
cd <repository folder>
python -m venv .venv && source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt                          # or: pip install -e ".[dev]"

python scripts/run_all.py      # full verification, about 1 minute
python -m pytest -q            # unit tests, about 6 seconds
python scripts/make_figures.py # optional figures -> results/
```

Options for `scripts/run_all.py`:

| Option | Meaning |
|---|---|
| `--quick` | smaller random samples (about 10 s); statistical tolerances widen automatically |
| `--skip-qiskit` | run without Qiskit / Aer (the NumPy gate-level check still runs) |
| `--n-mc N`, `--n-law N` | random images per Monte Carlo group (default 20000) / for the exact-error-law check (default 50000) |
| `--seed S` | random seed (default 2026); try other seeds for an independent check |

The exit code is 0 when nothing fails and 1 otherwise. Reports are written to `results/report.md` and
`results/report.json`. Requirements: Python 3.10+, NumPy; Qiskit and qiskit-aer are optional.

Typical result: `SUMMARY: {'PASS': 70, 'FLAG': 1, 'INFO': 4}`.

## What is verified

| Group | Checks |
|---|---|
| 1. Grayscale example | F4 matrix, norm, encoded state, QFT coefficients, energy shares, top-K set and tie rule, 90 % retained energy, reconstruction, MSE, PSNR, S={0,1} versus {0,3}, lossless QFT then inverse |
| 2. Circuit | manual circuit (H, controlled-phase π/2, H, SWAP) equals F4 in NumPy and Qiskit; Qiskit built-in QFT; classical FFT; Aer 2048-shot histogram versus the exact probabilities |
| 3. SpinQ hardware | mean absolute error, maximum error and total variation distance for all four examples; overall mean absolute difference 0.0575; ranking of the examples; probabilities sum to one; printed theory versus theory implied by the stated input matrix |
| 4. Analysis | what each coefficient measures (brightness, left-right, top-bottom); K = 1 to 4 sweep; eight test images; exact closed-form MSE law; PSNR changes by 6.02 dB per halving of brightness |
| 5. Monte Carlo | median PSNR for uniform, smooth and high-contrast random images; the first coefficient always holds at least 25 % of the energy; how often the left-right coefficient outranks the tied pair |

Status values: **PASS** reproduced within tolerance, **FAIL** not reproduced, **FLAG** reproduced but the
reported data contain an inconsistency to review, **INFO** informational, **SKIP** not run.

### Known item to resolve: SpinQ Example 3 (reported as FLAG)

The stated input matrix `[[0,1],[1,0]]` flattens to `[0,1,1,0]`, whose ideal probabilities are 0.5 on |01⟩ and
|10⟩. The study's table lists the theory as 0.5 on |01⟩ and |11⟩ (the pattern `[[0,1],[0,1]]`), and the error
table was computed from the listed values. Please confirm which pattern was run on the device. If it was
`[[0,1],[1,0]]`, the Example 3 theoretical column and its mean absolute error (0.118) need to be recomputed.

```bash
python -c "from qftimg import hardware as H; print(H.listed_vs_recomputed_theory()[3])"
```

## Conventions (they must match the study)

* basis order `|00>, |01>, |10>, |11>`; image flattened row by row, `[[a, b], [c, d]] -> [a, b, c, d]`
* `F[j,k] = exp(2*pi*i*j*k/N) / sqrt(N)`; for N = 4 this is the study's F4; the inverse is the conjugate transpose
* top-K by coefficient magnitude, rounded to 12 decimals so equal magnitudes tie; ties go to the smaller index
* `MSE = mean((x - x_hat)^2)`, `PSNR = 10 log10(255^2 / MSE)`; PSNR is infinite for an exact reconstruction
* Qiskit ordering: basis index = 2·q1 + q0; manual circuit `h(1); cp(pi/2, 0, 1); h(0); swap(0, 1)`

## Use as a library

```python
from qftimg import compress

r = compress([200, 50, 100, 150], K=2)
print(r.selected, r.energy_kept, r.x_hat, r.mse, r.psnr)

compress(sixteen_pixels, K=8)     # a 4 x 4 image on 4 qubits; any power-of-two length works
```

## The exact error law (our analysis, N = 4)

With `E` the retained energy before renormalisation, `n2 = ||x||^2` and `S` the kept set:

* S symmetric under conjugation (both or neither of y1, y3 kept): `MSE = n2 (1 - sqrt(E)) / 2`
* S = {0,1} or {0,3} (one member of the tied pair): `MSE = n2/4 (1 - 2 sqrt(E) + (E - E1/2)/E)`, `E1 = |y1|^2`

The law is checked against simulation on random images and covers about 90 % of the K = 1 to 4 cases.

## Repository layout

```
.
├── README.md  LICENSE  CITATION.cff  pyproject.toml  requirements.txt
├── src/qftimg/
│   ├── core.py        pipeline: encode, QFT, top-K, renormalise, inverse QFT, MSE / PSNR
│   ├── circuits.py    NumPy gate-level QFT; optional Qiskit operator, built-in QFT and Aer shots
│   ├── hardware.py    SpinQ probability table, error metrics, theory-versus-matrix consistency
│   ├── analysis.py    additional analysis (coefficients, K sweep, eight images, error law, brightness, Monte Carlo)
│   └── verify.py      all checks and the report writer
├── scripts/
│   ├── run_all.py     command-line entry point (reproduce and verify everything)
│   └── make_figures.py  optional matplotlib figures
├── tests/             pytest suite
├── results/           reference verification report (report.md / report.json) and figures
├── docs/
│   ├── paper/         the study (PDF)
│   └── presentation/  conference presentation (PPTX and PDF)
└── .github/workflows/ continuous integration (tests plus the verification run)
```

## Limitations

* All results concern a 2 x 2 image on two qubits and do not extend to natural images or larger sizes.
* Loading an arbitrary image into amplitudes and reading the coefficients back are not efficient in general.
* The Monte Carlo statements are about random 2 x 2 images only.
* One hardware run per pattern, no repeated runs, no confidence intervals.

## Citation

Please cite the study; see [`CITATION.cff`](CITATION.cff) (GitHub shows a "Cite this repository" button).
Add the journal reference and DOI there once the study is published.

## License

MIT, see [`LICENSE`](LICENSE). Please confirm the copyright holder line in `LICENSE` with all co-authors
(and your institution's policy) before publishing.
