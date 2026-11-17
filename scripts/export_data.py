#!/usr/bin/env python
"""Write data/spinq_measurements.csv from the SpinQ table stored in qftimg.hardware."""
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from qftimg import hardware as H  # noqa: E402

out = os.path.join(ROOT, "data", "spinq_measurements.csv")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", newline="", encoding="utf8") as f:
    w = csv.writer(f)
    w.writerow(["example", "input_matrix_row_major", "state", "theory_listed", "theory_from_matrix", "measured"])
    for k, e in H.EXAMPLES.items():
        flat = [v for row in e["matrix"] for v in row]
        rec = H.theory_from_matrix(e["matrix"])
        for i, s in enumerate(H.STATES):
            w.writerow([k, " ".join(map(str, flat)), s, f"{e['T'][i]:.3f}", f"{rec[i]:.3f}", f"{e['A'][i]:.3f}"])
print("wrote", out)
