"""SpinQ two-qubit NMR probability data (Table 2 of the study) and the descriptive metrics.

Probabilities are ordered |00>, |01>, |10>, |11>.
`EXAMPLES[k]["T"]` is the theoretical distribution printed in the table; `theory_from_matrix`
recomputes it from the stated binary input matrix by amplitude encoding (p = x^2 / ||x||^2).
"""
from __future__ import annotations

import numpy as np

STATES = ["00", "01", "10", "11"]

EXAMPLES = {
    1: dict(matrix=[[1, 0], [0, 1]], T=[0.500, 0.000, 0.000, 0.500], A=[0.437, 0.000, 0.000, 0.563]),
    2: dict(matrix=[[1, 1], [0, 0]], T=[0.500, 0.500, 0.000, 0.000], A=[0.475, 0.475, 0.025, 0.025]),
    3: dict(matrix=[[0, 1], [1, 0]], T=[0.000, 0.500, 0.000, 0.500], A=[0.118, 0.441, 0.118, 0.323]),
    4: dict(matrix=[[1, 1], [1, 1]], T=[0.250, 0.250, 0.250, 0.250], A=[0.195, 0.195, 0.306, 0.306]),
}

# Values printed in Table 3 of the study (the expected result for verify.py).
TABLE3 = {
    1: dict(mae=0.0315, max=0.063, tv=0.063),
    2: dict(mae=0.0250, max=0.025, tv=0.050),
    3: dict(mae=0.1180, max=0.177, tv=0.236),
    4: dict(mae=0.0555, max=0.056, tv=0.111),
}
OVERALL_MAE = 0.0575


def theory_from_matrix(matrix) -> np.ndarray:
    """Probabilities of the amplitude-encoded binary image (row-major flattening)."""
    x = np.asarray(matrix, float).ravel()
    return x ** 2 / np.sum(x ** 2)


def errors(T, A) -> dict:
    """Mean absolute error, maximum absolute error and total variation distance."""
    T, A = np.asarray(T, float), np.asarray(A, float)
    d = np.abs(A - T)
    return dict(mae=float(d.mean()), max=float(d.max()), tv=float(0.5 * d.sum()))


def overall_mae() -> float:
    return float(np.mean([np.abs(np.array(e["A"]) - np.array(e["T"])) for e in EXAMPLES.values()]))


def listed_vs_recomputed_theory() -> dict:
    """For every example: is the printed T equal to the T implied by the printed input matrix?"""
    out = {}
    for k, e in EXAMPLES.items():
        rec = theory_from_matrix(e["matrix"])
        out[k] = dict(listed=e["T"], recomputed=rec.tolist(), consistent=bool(np.allclose(rec, e["T"], atol=1e-9)))
    return out
