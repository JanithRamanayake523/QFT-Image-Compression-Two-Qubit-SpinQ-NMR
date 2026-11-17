"""Run every check and compare it with the value reported in the study / presentation.

Status values
  PASS  the recomputed value matches the reported value within the stated tolerance
  FAIL  mismatch (a reported number cannot be reproduced)
  FLAG  the numbers reproduce, but the reported data contain an internal inconsistency to review
  INFO  informational value, no expected value
  SKIP  check not run (e.g. Qiskit not installed)
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
import numpy as np

from . import analysis as A
from . import circuits as C
from . import hardware as H
from .core import compress, qft_matrix, amplitude_encode, psnr


@dataclass
class Check:
    group: str
    name: str
    source: str
    expected: object
    actual: object
    tol: object
    status: str
    note: str = ""


def _fmt(v):
    if isinstance(v, (list, tuple, np.ndarray)):
        return "[" + ", ".join(_fmt(i) for i in v) + "]"
    if isinstance(v, (float, np.floating)):
        return "inf" if np.isinf(v) else f"{v:.6g}"
    return str(v)


class Runner:
    def __init__(self):
        self.checks: list[Check] = []

    def close(self, group, name, source, expected, actual, tol, note=""):
        e, a = np.asarray(expected, float), np.asarray(actual, float)
        ok = bool(np.all(np.isclose(a, e, atol=tol, rtol=0)) or (np.all(np.isinf(a)) and np.all(np.isinf(e))))
        self.checks.append(Check(group, name, source, _fmt(expected), _fmt(actual), tol, "PASS" if ok else "FAIL", note))

    def truth(self, group, name, source, actual_bool, note=""):
        self.checks.append(Check(group, name, source, "True", str(bool(actual_bool)), "-", "PASS" if actual_bool else "FAIL", note))

    def info(self, group, name, source, actual, note=""):
        self.checks.append(Check(group, name, source, "-", _fmt(actual), "-", "INFO", note))

    def flag(self, group, name, source, expected, actual, note):
        self.checks.append(Check(group, name, source, _fmt(expected), _fmt(actual), "-", "FLAG", note))

    def skip(self, group, name, source, note):
        self.checks.append(Check(group, name, source, "-", "-", "-", "SKIP", note))


IMG = [200, 50, 100, 150]


def run_all(n_law=50000, n_mc=20000, seed=2026, use_qiskit=True, log=print):
    R = Runner()
    t0 = time.time()

    # ------------------------------------------------------------------ 1. grayscale example
    log("[1/5] grayscale example (study Sec. 3, Table 1)")
    g = "1 Grayscale example"
    r = compress(IMG, 2)
    F4 = qft_matrix(2)
    paper_F4 = 0.5 * np.array([[1, 1, 1, 1], [1, 1j, -1, -1j], [1, -1, 1, -1], [1, -1j, -1, 1j]])
    R.close(g, "QFT matrix equals F4 of Eq. (3)", "paper Eq. 3", paper_F4.real.tolist(), F4.real.tolist(), 1e-12)
    R.close(g, "QFT matrix imaginary part", "paper Eq. 3", paper_F4.imag.tolist(), F4.imag.tolist(), 1e-12)
    R.truth(g, "F4 is unitary", "paper Sec. 2.1", np.allclose(F4.conj().T @ F4, np.eye(4)))
    R.close(g, "||x||_2 = 50*sqrt(30)", "paper Eq. 7", 50 * np.sqrt(30), r.norm, 1e-9)
    R.close(g, "encoded state psi", "paper Eq. 9", [0.7303, 0.1826, 0.3651, 0.5477], r.psi, 5e-5)
    y_exact = np.array([5, 1 - 1j, 1, 1 + 1j]) / np.sqrt(30)
    R.close(g, "QFT coefficients y (real part)", "paper Eq. 11", y_exact.real, r.y.real, 1e-12)
    R.close(g, "QFT coefficients y (imag part)", "paper Eq. 11", y_exact.imag, r.y.imag, 1e-12)
    R.close(g, "coefficient magnitudes |y|", "paper Eq. 12", [0.9129, 0.2582, 0.1826, 0.2582], np.abs(r.y), 5e-5)
    R.close(g, "energy shares before QFT", "deck: Results energy slide", [16 / 30, 1 / 30, 4 / 30, 9 / 30], np.abs(r.psi) ** 2, 1e-12)
    R.close(g, "energy shares after QFT", "deck: Results energy slide", [25 / 30, 2 / 30, 1 / 30, 2 / 30], np.abs(r.y) ** 2, 1e-12)
    R.truth(g, "selected set S = {0, 1} (tie -> smaller index)", "paper Sec. 4.3", r.selected == [0, 1])
    R.close(g, "retained energy (K=2)", "paper Eq. 15", 0.9, r.energy_kept, 1e-12)
    R.close(g, "energy in y0 alone", "paper Sec. 5.1", 25 / 30, abs(r.y[0]) ** 2, 1e-12)
    R.close(g, "coefficient retention fraction", "paper Table 1", 0.5, r.coeff_fraction, 0)
    R.close(g, "reconstructed vector x_hat", "paper Eq. 19", [158.114, 105.409, 105.409, 158.114], r.x_hat, 5e-4)
    R.close(g, "MSE", "paper Eq. 26", 1229.93, r.mse, 5e-3)
    R.close(g, "PSNR (dB)", "paper Eq. 27", 17.23, r.psnr, 5e-3)
    alt = compress(IMG, 2, selected=[0, 3])
    R.close(g, "S={0,3} gives the same real reconstruction", "paper Sec. 3.2", r.x_hat, alt.x_hat, 1e-9)
    full = compress(IMG, 4)
    R.close(g, "QFT -> IQFT without truncation returns the input", "paper Sec. 4.2", IMG, full.x_hat, 1e-9)

    # ------------------------------------------------------------------ 2. circuits
    log("[2/5] gate-level circuit checks (study Sec. 4.2, 4.4)")
    g = "2 Circuit"
    R.close(g, "manual circuit (H, CP, H, SWAP) equals F4 [NumPy]", "paper Sec. 4.2", F4.real.tolist(), C.manual_qft_matrix().real.tolist(), 1e-12)
    R.close(g, "manual circuit imaginary part [NumPy]", "paper Sec. 4.2", F4.imag.tolist(), C.manual_qft_matrix().imag.tolist(), 1e-12)
    R.close(g, "inverse circuit equals F4-dagger [NumPy]", "paper Sec. 4.2", F4.conj().T.real.tolist(), C.manual_iqft_matrix().real.tolist(), 1e-12)
    R.close(g, "classical FFT reference equals y", "paper Sec. 4.1 step 5", r.y.real, C.classical_fft_reference(IMG).real, 1e-12)
    R.close(g, "classical FFT reference (imag)", "paper Sec. 4.1 step 5", r.y.imag, C.classical_fft_reference(IMG).imag, 1e-12)
    if use_qiskit and C.qiskit_available():
        R.close(g, "manual circuit equals F4 [Qiskit Operator]", "paper Sec. 4.2", F4.real.tolist(), C.qiskit_operator_matrix(C.manual_circuit()).real.tolist(), 1e-9)
        R.close(g, "manual circuit imaginary part [Qiskit]", "paper Sec. 4.2", F4.imag.tolist(), C.qiskit_operator_matrix(C.manual_circuit()).imag.tolist(), 1e-9)
        R.close(g, "Qiskit built-in QFT equals F4", "paper Sec. 4.2", F4.real.tolist(), C.qiskit_builtin_qft_matrix().real.tolist(), 1e-9)
        R.close(g, "Qiskit built-in QFT imaginary part", "paper Sec. 4.2", F4.imag.tolist(), C.qiskit_builtin_qft_matrix().imag.tolist(), 1e-9)
        p = C.aer_probabilities(IMG, shots=2048, seed=seed)
        R.close(g, "Aer 2048-shot probabilities vs |y|^2 (max abs gap)", "paper Sec. 4.4", np.abs(r.y) ** 2, p, 0.04,
                note="statistical; 4-sigma band for 2048 shots is about 0.04")
    else:
        for nm in ("manual circuit vs F4 [Qiskit Operator]", "Qiskit built-in QFT vs F4", "Aer 2048-shot histogram"):
            R.skip(g, nm, "paper Sec. 4.2 / 4.4", "Qiskit / Aer not installed")

    # ------------------------------------------------------------------ 3. hardware table
    log("[3/5] SpinQ probability table (study Tables 2 and 3)")
    g = "3 SpinQ hardware"
    for k, e in H.EXAMPLES.items():
        er = H.errors(e["T"], e["A"])
        for key, label in (("mae", "mean absolute error"), ("max", "maximum absolute error"), ("tv", "total variation distance")):
            R.close(g, f"Example {k}: {label}", "paper Table 3", H.TABLE3[k][key], er[key], 6e-4 if key != "mae" else 6e-5)
        s_a = float(np.sum(e["A"]))
        R.close(g, f"Example {k}: measured probabilities sum to 1", "paper Sec. 5.2", 1.0, s_a, 2.5e-3,
                note="rounding of the printed values" if abs(s_a - 1) > 1e-9 else "")
    R.close(g, "overall mean absolute difference (16 probabilities)", "paper Sec. 5.3", H.OVERALL_MAE, H.overall_mae(), 5e-5)
    maes = {k: H.errors(e["T"], e["A"])["mae"] for k, e in H.EXAMPLES.items()}
    R.truth(g, "ranking by MAE: Example 2 < 1 < 4 < 3", "deck: Probability errors slide", sorted(maes, key=maes.get) == [2, 1, 4, 3])
    for k, c in H.listed_vs_recomputed_theory().items():
        if c["consistent"]:
            R.close(g, f"Example {k}: printed T equals T from the stated matrix", "paper Table 2", c["listed"], c["recomputed"], 1e-9)
        else:
            R.flag(g, f"Example {k}: printed T vs T from the stated matrix", "paper Table 2", c["listed"], c["recomputed"],
                   "The stated input matrix [[0,1],[1,0]] amplitude-encodes to probability 0.5 on |01> and |10>, "
                   "but the table lists 0.5 on |01> and |11>. Table 3 values follow the LISTED T. "
                   "Check with the experimenters which pattern was actually run (e.g. [[0,1],[0,1]] gives |01>,|11>).")

    # ------------------------------------------------------------------ 4. analysis
    log("[4/5] additional analysis (K sweep, eight images, error law, brightness)")
    g = "4 Analysis"
    R.truth(g, "coefficient closed forms (brightness / left-right / top-bottom)", "analysis", A.max_closed_form_error() < 1e-12)
    sw = A.k_sweep(IMG)
    R.close(g, "K=1 reconstruction is one flat value 136.9", "deck: Analysis K sweep", [136.9] * 4, sw[1]["x_hat"], 0.05)
    R.close(g, "K=1 PSNR", "deck: Analysis K sweep", 13.0, sw[1]["psnr"], 0.05)
    R.close(g, "K=2 PSNR", "deck: Analysis K sweep", 17.2, sw[2]["psnr"], 0.05)
    R.close(g, "K=3 PSNR", "deck: Analysis K sweep", 20.1, sw[3]["psnr"], 0.05)
    R.close(g, "K=4 returns the image exactly (MSE)", "deck: Analysis K sweep", 0.0, sw[4]["mse"], 1e-9)
    tab = A.test_image_table()
    B, Cg, Ed = tab["B Smooth"], tab["C Gradient"], tab["E Single bright pixel"]
    R.close(g, "smooth image B: PSNR at K=1", "deck: Analysis eight test images", 33.2, B[1]["psnr"], 0.1)
    R.close(g, "smooth image B: PSNR at K=3", "deck: Analysis eight test images", 46.2, B[3]["psnr"], 0.1)
    R.truth(g, "gradient C stays below 16 dB at K=3", "deck: Analysis eight test images", Cg[3]["psnr"] < 16)
    R.close(g, "single bright pixel E: PSNR at K=3 (about 16 dB)", "deck: Analysis eight test images", 16.0, Ed[3]["psnr"], 0.1)
    R.close(g, "single bright pixel E spreads energy evenly", "deck: Analysis eight test images", [0.25] * 4, Ed["shares"], 1e-12)
    exact = [(n, K) for n in ("F Flat",) for K in (1, 2, 3)] + [("D Checker", 3), ("G Horizontal edge", 3), ("H Vertical edge", 2), ("H Vertical edge", 3)]
    R.truth(g, "images reconstructed exactly (missing bars): F all K; D,G at K=3; H at K=2,3", "deck: Analysis eight test images",
            all(tab[n][K]["mse"] < 1e-9 for n, K in exact))
    law = A.verify_mse_law(n=n_law, seed=seed)
    R.truth(g, f"exact MSE law ({law['covered']} comparisons on {law['images']} random images, max |pred-sim|/||x||^2 = {law['max_error_vs_norm2']:.2e})",
            "deck: Analysis error and brightness", law["max_error_vs_norm2"] < 1e-9,
            note=f"covered by law: {law['by_kind']}; remaining sets are K=3 with S={{0,1,2}}-type")
    bs = A.brightness_scaling(IMG)
    R.close(g, "PSNR gain per halving of brightness (dB)", "deck: Analysis error and brightness", 20 * np.log10(2), [bs[i + 1]["psnr"] - bs[i]["psnr"] for i in range(3)], 1e-6)
    R.close(g, "relative error stays 6.6% at every brightness", "deck: Analysis error and brightness", [0.0656] * 4, [b["relative_error"] for b in bs], 5e-4)
    rc = A.renorm_vs_classical(IMG)
    R.info(g, "renormalised vs classical-deletion MSE ratio (K=1,2,3)", "analysis", [rc[K]["ratio"] for K in (1, 2, 3)],
           note="ratio != 1: renormalisation changes the result; it is not always better or worse")

    # ------------------------------------------------------------------ 5. Monte Carlo
    log(f"[5/5] Monte Carlo ({n_mc} images per group; this is the slowest step)")
    g = "5 Monte Carlo"
    mc = A.monte_carlo(n=n_mc, seed=seed)
    widen = max(1.0, (20000 / n_mc) ** 0.5)      # statistical tolerances widen for smaller samples
    R.close(g, "uniform random images: median PSNR at K=2", "deck: Is the initial example typical", 17.7, mc["uniform"][2]["median_psnr"], 0.3 * widen, note="statistical")
    R.close(g, "smooth images: median PSNR at K=2 (about 34 dB)", "deck: Is the initial example typical", 34.0, mc["smooth"][2]["median_psnr"], 0.7 * widen, note="statistical")
    R.close(g, "high-contrast images: median PSNR at K=2 (about 21 dB)", "deck: Is the initial example typical", 21.0, mc["contrast"][2]["median_psnr"], 0.7 * widen, note="statistical")
    R.truth(g, "DC coefficient always holds at least 25% of the energy (non-negative pixels)", "deck: Is the initial example typical", mc["facts"]["dc_min"] >= 0.25 - 1e-12,
            note=f"smallest observed share {mc['facts']['dc_min']:.4f}")
    R.close(g, "left-right coefficient outranks the pair (about 41%)", "deck: Is the initial example typical", 0.41, mc["facts"]["p_y2_outranks_pair"], 0.02 * widen, note="statistical")
    R.info(g, "median PSNR K=1,2,3 (uniform)", "analysis", [mc["uniform"][K]["median_psnr"] for K in (1, 2, 3)])
    R.info(g, "median PSNR K=1,2,3 (smooth)", "analysis", [mc["smooth"][K]["median_psnr"] for K in (1, 2, 3)])
    R.info(g, "median PSNR K=1,2,3 (high contrast)", "analysis", [mc["contrast"][K]["median_psnr"] for K in (1, 2, 3)])

    log(f"done in {time.time() - t0:.1f} s")
    return R.checks, dict(test_images=tab, k_sweep=sw, mse_law=law, brightness=bs, renorm=rc, monte_carlo=mc)


def summarise(checks):
    s = {}
    for c in checks:
        s[c.status] = s.get(c.status, 0) + 1
    return s


def write_reports(checks, extra, outdir, params):
    import os
    os.makedirs(outdir, exist_ok=True)
    summary = summarise(checks)
    with open(os.path.join(outdir, "report.json"), "w", encoding="utf8") as f:
        json.dump(dict(params=params, summary=summary, checks=[asdict(c) for c in checks], details=extra), f, indent=2, default=float)
    lines = ["# Verification report", "", f"Parameters: `{params}`", "", "Summary: " + ", ".join(f"**{k}** {v}" for k, v in sorted(summary.items())), ""]
    group = None
    for c in checks:
        if c.group != group:
            group = c.group
            lines += ["", f"## {group}", "", "| Status | Check | Source | Expected | Recomputed | Tol |", "|---|---|---|---|---|---|"]
        lines.append(f"| {c.status} | {c.name} | {c.source} | {c.expected} | {c.actual} | {c.tol} |")
    notes = [c for c in checks if c.note and c.status in ("FLAG", "FAIL")]
    if notes:
        lines += ["", "## Items to review", ""]
        lines += [f"- **{c.status}** {c.name}: {c.note}" for c in notes]
    with open(os.path.join(outdir, "report.md"), "w", encoding="utf8") as f:
        f.write("\n".join(lines) + "\n")
    return summary
