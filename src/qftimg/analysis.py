"""Additional analysis built on the same pipeline (all deterministic or seeded).

1. coefficient_closed_forms   what each QFT coefficient measures (brightness / left-right / top-bottom)
2. k_sweep, test_image_table  behaviour for K = 1..4 and for eight tiny test images
3. mse_law_*                  exact, closed-form MSE for hard top-K truncation with renormalisation
4. brightness_scaling         same shape, different brightness -> PSNR shifts by 6.02 dB per halving
5. renorm_vs_classical        effect of renormalising versus plain coefficient deletion
6. monte_carlo                random images: median PSNR, DC energy floor, ranking statistics
"""
from __future__ import annotations

import numpy as np
from .core import compress, qft_matrix, psnr, select_top_k

F4 = qft_matrix(2)

TEST_IMAGES = {
    "A Mixed values (initial example)": [200, 50, 100, 150],
    "B Smooth": [100, 110, 105, 115],
    "C Gradient": [0, 85, 170, 255],
    "D Checker": [255, 0, 0, 255],
    "E Single bright pixel": [255, 0, 0, 0],
    "F Flat": [128, 128, 128, 128],
    "G Horizontal edge": [255, 255, 0, 0],
    "H Vertical edge": [255, 0, 255, 0],
}


# ------------------------------------------------------------------ 1. meaning of the coefficients
def coefficient_closed_forms(x):
    """Return (numeric, closed_form) energy shares for x = [a, b, c, d] (image [[a, b], [c, d]]).

    |y0|^2 = (a+b+c+d)^2 / (4||x||^2)         overall brightness (DC)
    |y2|^2 = (a-b+c-d)^2 / (4||x||^2)         left-right contrast
    |y1|^2 = |y3|^2 = ((a-c)^2+(b-d)^2) / (4||x||^2)   top-bottom contrast (a conjugate pair)
    """
    x = np.asarray(x, float)
    a, b, c, d = x
    n2 = float(x @ x)
    y = F4 @ (x / np.sqrt(n2))
    numeric = np.abs(y) ** 2
    pair = ((a - c) ** 2 + (b - d) ** 2) / (4 * n2)
    closed = np.array([(a + b + c + d) ** 2 / (4 * n2), pair, (a - b + c - d) ** 2 / (4 * n2), pair])
    return numeric, closed


def max_closed_form_error(n=2000, seed=2026):
    rng = np.random.default_rng(seed)
    worst = 0.0
    for _ in range(n):
        num, cl = coefficient_closed_forms(rng.uniform(0, 255, 4))
        worst = max(worst, float(np.max(np.abs(num - cl))))
    return worst


# ------------------------------------------------------------------ 2. K sweep and test images
def k_sweep(x, Ks=(1, 2, 3, 4)):
    out = {}
    for K in Ks:
        r = compress(x, K)
        out[K] = dict(selected=r.selected, energy=r.energy_kept, x_hat=r.x_hat.tolist(), mse=r.mse, psnr=r.psnr)
    return out


def test_image_table(Ks=(1, 2, 3)):
    table = {}
    for name, v in TEST_IMAGES.items():
        x = np.array(v, float)
        r = compress(x, 2)
        row = dict(shares=(np.abs(r.y) ** 2).tolist())
        for K in Ks:
            rk = compress(x, K)
            row[K] = dict(energy=rk.energy_kept, mse=rk.mse, psnr=rk.psnr, x_hat=rk.x_hat.tolist())
        table[name] = row
    return table


# ------------------------------------------------------------------ 3. exact MSE law
def mse_law(x, K):
    """Closed-form MSE of hard top-K truncation with renormalisation (N = 4), or None if the law
    does not cover the selected set.

    With E = retained energy, n2 = ||x||^2 and S the selected set:
      * S symmetric under conjugation (contains both or neither of y1, y3):  MSE = n2 (1 - sqrt(E)) / 2
      * S = {0,1} or {0,3}  (one member of the tied pair):  MSE = n2/4 * (1 - 2 sqrt(E) + (E - E1/2)/E),  E1 = |y1|^2
    """
    x = np.asarray(x, float)
    n2 = float(x @ x)
    r = compress(x, K)
    S, E = r.selected, r.energy_kept
    if (1 in S) == (3 in S):
        return n2 * (1 - np.sqrt(E)) / 2, "symmetric"
    if S in ([0, 1], [0, 3]):
        E1 = abs(r.y[1]) ** 2
        return n2 / 4 * (1 - 2 * np.sqrt(E) + (E - E1 / 2) / E), "pair-split"
    return None, "uncovered"


def verify_mse_law(n=50000, seed=2026, Ks=(1, 2, 3, 4)):
    """Compare the law with the simulated MSE on n random images per K.  Returns summary dict."""
    rng = np.random.default_rng(seed)
    worst = 0.0
    covered = tested = 0
    by_kind = {"symmetric": 0, "pair-split": 0, "uncovered": 0}
    for _ in range(n):
        x = rng.uniform(0, 255, 4)
        for K in Ks:
            pred, kind = mse_law(x, K)
            by_kind[kind] += 1
            tested += 1
            if pred is None:
                continue
            covered += 1
            m = compress(x, K).mse
            # error measured against ||x||^2: relative error of the MSE itself is meaningless when
            # the true MSE is ~1e-13 (near-exact reconstructions), where floating-point noise dominates
            worst = max(worst, abs(pred - m) / float(x @ x))
    return dict(images=n, comparisons=tested, covered=covered, by_kind=by_kind, max_error_vs_norm2=worst)


# ------------------------------------------------------------------ 4. brightness scaling
def brightness_scaling(x, K=2, factors=(1.0, 0.5, 0.25, 0.125)):
    x = np.asarray(x, float)
    rows = []
    for f in factors:
        r = compress(x * f, K)
        rel = float(np.sum((r.x - r.x_hat) ** 2) / np.sum(r.x ** 2))     # ||x - x_hat||^2 / ||x||^2
        rows.append(dict(factor=f, mse=r.mse, psnr=r.psnr, relative_error=rel))
    return rows


# ------------------------------------------------------------------ 5. renormalisation penalty
def renorm_vs_classical(x, Ks=(1, 2, 3)):
    out = {}
    for K in Ks:
        a, b = compress(x, K, renormalize=True), compress(x, K, renormalize=False)
        out[K] = dict(mse_renorm=a.mse, mse_classical=b.mse, psnr_renorm=a.psnr, psnr_classical=b.psnr,
                      ratio=a.mse / b.mse)
    return out


# ------------------------------------------------------------------ 6. Monte Carlo
def _group_images(kind, n, rng):
    if kind == "uniform":
        imgs = rng.uniform(0, 255, (n, 4))
    elif kind == "smooth":               # one base level + small noise (sd 12)
        base = rng.uniform(40, 215, (n, 1))
        imgs = np.clip(base + rng.normal(0, 12, (n, 4)), 0, 255)
    elif kind == "contrast":             # one base level + large noise (sd 60)
        base = rng.uniform(40, 215, (n, 1))
        imgs = np.clip(base + rng.normal(0, 60, (n, 4)), 0, 255)
    else:
        raise ValueError(kind)
    return imgs[(imgs ** 2).sum(1) > 0]  # an all-zero image cannot be amplitude encoded


def monte_carlo(n=20000, seed=2026, Ks=(1, 2, 3)):
    """Random-image study.  Returns dict group -> K -> statistics, plus structural facts for the
    uniform group (DC energy floor, how often the left-right coefficient outranks the pair)."""
    rng = np.random.default_rng(seed)
    out = {}
    for kind in ("uniform", "smooth", "contrast"):
        imgs = _group_images(kind, n, rng)
        g = {}
        for K in Ks:
            ps, es = [], []
            for x in imgs:
                r = compress(x, K)
                ps.append(r.psnr)
                es.append(r.energy_kept)
            ps = np.array(ps)
            g[K] = dict(median_psnr=float(np.median(ps)), p_ge_30=float(np.mean(ps >= 30)),
                        p_ge_20=float(np.mean(ps >= 20)), mean_energy=float(np.mean(es)))
        out[kind] = g
    # structural facts (uniform images)
    imgs = _group_images("uniform", n, rng)
    dc = (imgs.sum(1) ** 2) / (4 * (imgs ** 2).sum(1))
    outranks = 0
    for x in imgs:
        y = F4 @ (x / np.linalg.norm(x))
        outranks += abs(y[2]) > abs(y[1])
    out["facts"] = dict(dc_min=float(dc.min()), dc_mean=float(dc.mean()), p_y2_outranks_pair=outranks / n)
    return out
