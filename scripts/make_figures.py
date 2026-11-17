#!/usr/bin/env python
"""Optional: regenerate the main figures (needs matplotlib).  Output: results/*.png"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from qftimg import compress                      # noqa: E402
from qftimg import analysis as A, hardware as H  # noqa: E402

OUT = os.path.join(ROOT, "results")
os.makedirs(OUT, exist_ok=True)
IMG = [200, 50, 100, 150]
LAB = ["|00>", "|01>", "|10>", "|11>"]

# 1. energy before / after QFT
r = compress(IMG, 2)
fig, ax = plt.subplots(figsize=(6, 3.6))
w = 0.38
ax.bar(np.arange(4) - w / 2, np.abs(r.psi) ** 2, w, label="before QFT")
ax.bar(np.arange(4) + w / 2, np.abs(r.y) ** 2, w, label="after QFT")
ax.set_xticks(range(4)); ax.set_xticklabels(LAB); ax.set_ylabel("energy share"); ax.legend()
ax.set_title("Energy per basis state (squared amplitude)")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig_energy.png"), dpi=160); plt.close(fig)

# 2. PSNR vs K for the eight test images
tab = A.test_image_table()
fig, ax = plt.subplots(figsize=(7, 3.8))
for name, row in tab.items():
    ps = [min(row[K]["psnr"], 60) for K in (1, 2, 3)]
    ax.plot([1, 2, 3], ps, marker="o", label=name[:1])
ax.set_xlabel("K (coefficients kept)"); ax.set_ylabel("PSNR (dB, exact capped at 60)"); ax.set_xticks([1, 2, 3])
ax.legend(ncol=4, fontsize=8); ax.set_title("Quality versus K, eight test images")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig_psnr_vs_k.png"), dpi=160); plt.close(fig)

# 3. SpinQ theory versus measurement
fig, axs = plt.subplots(1, 4, figsize=(11, 2.8), sharey=True)
for ax, (k, e) in zip(axs, H.EXAMPLES.items()):
    ax.bar(np.arange(4) - 0.2, e["T"], 0.4, label="theory"); ax.bar(np.arange(4) + 0.2, e["A"], 0.4, label="SpinQ")
    ax.set_xticks(range(4)); ax.set_xticklabels(LAB, fontsize=7); ax.set_title(f"Example {k}", fontsize=9)
axs[0].legend(fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig_spinq.png"), dpi=160); plt.close(fig)
print("figures written to", OUT)
