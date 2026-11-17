#!/usr/bin/env python
"""Reproduce and verify every result of the two-qubit QFT image-compression study.

    python scripts/run_all.py              # full run (about 1 minute)
    python scripts/run_all.py --quick      # small Monte Carlo sizes (about 10 seconds)
    python scripts/run_all.py --skip-qiskit # no Qiskit / Aer available
    python scripts/run_all.py --n-mc 100000 --n-law 200000 --seed 7

Exit code 0 = no FAIL;  1 = at least one reported number could not be reproduced.
Reports are written to results/report.md and results/report.json.
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from qftimg.verify import run_all, write_reports, summarise  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n-law", type=int, default=50000, help="random images for the exact-MSE-law check")
    ap.add_argument("--n-mc", type=int, default=20000, help="random images per Monte Carlo group")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--quick", action="store_true", help="n-law=3000, n-mc=2000 (statistical checks get looser)")
    ap.add_argument("--skip-qiskit", action="store_true")
    ap.add_argument("--out", default=os.path.join(ROOT, "results"))
    a = ap.parse_args()
    if a.quick:
        a.n_law, a.n_mc = 3000, 2000

    checks, extra = run_all(n_law=a.n_law, n_mc=a.n_mc, seed=a.seed, use_qiskit=not a.skip_qiskit)
    params = dict(n_law=a.n_law, n_mc=a.n_mc, seed=a.seed, qiskit=not a.skip_qiskit)
    summary = write_reports(checks, extra, a.out, params)

    print()
    width = max(len(c.name) for c in checks)
    for c in checks:
        print(f"{c.status:5} {c.name:<{min(width, 88)}}  expected {c.expected}  got {c.actual}")
    print("\nSUMMARY:", summary)
    print("reports:", os.path.join(a.out, "report.md"), "and report.json")
    sys.exit(1 if summary.get("FAIL") else 0)


if __name__ == "__main__":
    main()
