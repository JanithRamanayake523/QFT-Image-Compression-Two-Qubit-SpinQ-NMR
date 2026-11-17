# Data

`spinq_measurements.csv` holds the SpinQ two-qubit NMR measurements reported in the study (Table 2).
There is no other experimental data in this repository: everything else is computed by the code.

| Column | Meaning |
|---|---|
| `example` | binary-pattern example 1 to 4 |
| `input_matrix_row_major` | the stated 2 x 2 input matrix, flattened row by row |
| `state` | computational basis state `00`, `01`, `10`, `11` |
| `theory_listed` | theoretical probability as printed in the study |
| `theory_from_matrix` | probability recomputed from the stated input matrix (`x^2 / ||x||^2`) |
| `measured` | probability measured on the SpinQ device |

The two theory columns differ for **Example 3** (see the README, "Known item to resolve").
The values are transcribed from the study; the raw instrument output files are not included.
The file is regenerated with `python scripts/export_data.py` and a test checks that it matches the code.
