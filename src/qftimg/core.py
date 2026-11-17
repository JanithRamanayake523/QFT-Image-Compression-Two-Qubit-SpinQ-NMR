"""Core pipeline:  image -> x -> |psi> -> y = F|psi> -> top-K -> renormalise -> F^dagger -> x_hat.

All conventions follow the study:
* row-major flattening of the image,
* QFT matrix F[j,k] = exp(2*pi*i*j*k/N)/sqrt(N)  (for N=4 this is the matrix F4 of the study),
* hard top-K selection by coefficient magnitude, ties broken by the smaller index,
* real part of the inverse transform, rescaled by ||x||_2,
* MSE = mean((x - x_hat)^2),  PSNR = 10 log10(255^2 / MSE).
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

PEAK = 255.0


def qft_matrix(n_qubits: int = 2) -> np.ndarray:
    """Unitary QFT matrix on n qubits (N = 2**n)."""
    N = 2 ** n_qubits
    j, k = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
    return np.exp(2j * np.pi * j * k / N) / np.sqrt(N)


def amplitude_encode(x):
    """Return (psi, norm) with psi = x / ||x||_2.  x is the flattened image."""
    x = np.asarray(x, dtype=float).ravel()
    norm = float(np.linalg.norm(x))
    if norm == 0.0:
        raise ValueError("an all-zero image cannot be amplitude encoded")
    return x / norm, norm


def energy_shares(v) -> np.ndarray:
    """Squared magnitude of every entry (these sum to 1 for a normalised state)."""
    return np.abs(np.asarray(v)) ** 2


def select_top_k(y, K: int, decimals: int = 12):
    """Indices of the K largest-magnitude coefficients.

    Magnitudes are rounded to `decimals` places so that mathematically equal values
    (e.g. the conjugate pair y1, y3) are treated as ties; ties go to the smaller index.
    Returns a sorted list of indices.
    """
    mags = np.round(np.abs(np.asarray(y)), decimals)
    order = sorted(range(len(mags)), key=lambda i: (-mags[i], i))
    return sorted(order[:K])


def mse(x, x_hat) -> float:
    x, x_hat = np.asarray(x, float).ravel(), np.asarray(x_hat, float).ravel()
    return float(np.mean((x - x_hat) ** 2))


def psnr(mse_value: float, peak: float = PEAK) -> float:
    """PSNR in dB; +inf for a (numerically) exact reconstruction."""
    return float("inf") if mse_value < 1e-9 else float(10 * np.log10(peak ** 2 / mse_value))


@dataclass
class CompressionResult:
    x: np.ndarray
    norm: float
    psi: np.ndarray
    y: np.ndarray
    selected: list
    y_trunc: np.ndarray
    energy_kept: float          # sum |y_k|^2 over the kept set, BEFORE renormalisation
    coeff_fraction: float       # K / N
    psi_f: np.ndarray           # renormalised truncated state
    x_hat: np.ndarray
    mse: float
    psnr: float


def compress(x, K: int, renormalize: bool = True, selected=None, n_qubits: int | None = None) -> CompressionResult:
    """Run the full pipeline on a flattened image x with hard top-K truncation.

    renormalize=False models "classical deletion" (no renormalisation) and is used only
    in the renormalisation-penalty analysis.  `selected` overrides the top-K choice.
    """
    x = np.asarray(x, dtype=float).ravel()
    N = x.size
    n = n_qubits if n_qubits is not None else int(round(np.log2(N)))
    if 2 ** n != N:
        raise ValueError("image size must be a power of two (pad with zeros first)")
    F = qft_matrix(n)
    psi, norm = amplitude_encode(x)
    y = F @ psi
    S = list(selected) if selected is not None else select_top_k(y, K)
    y_t = np.zeros(N, dtype=complex)
    y_t[S] = y[S]
    E = float(np.sum(np.abs(y_t) ** 2))
    psi_f = y_t / np.sqrt(E) if renormalize else y_t
    x_hat = norm * (F.conj().T @ psi_f).real
    m = mse(x, x_hat)
    return CompressionResult(x=x, norm=norm, psi=psi, y=y, selected=S, y_trunc=y_t, energy_kept=E,
                             coeff_fraction=len(S) / N, psi_f=psi_f, x_hat=x_hat, mse=m, psnr=psnr(m))
