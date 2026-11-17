# Contributing

Thank you for helping to check this work. Useful contributions:

* **Independent re-runs.** Run `python scripts/run_all.py` (try other seeds, for example `--seed 7 --n-mc 100000`)
  and open an issue with `results/report.md` if any check fails.
* **Corrections to the reported data.** If you find a mismatch with the study, open an issue that names the
  table, equation or slide and the value you recomputed.
* **Code.** Keep the conventions in the README (basis order, flattening, tie rule, MSE / PSNR definitions).
  Run `python -m pytest -q` and `python scripts/run_all.py --quick` before opening a pull request, and add a test
  for any new behaviour.

Please do not change the values in `src/qftimg/hardware.py` or `data/` without a reference to the source
measurement; they are transcribed from the study.
