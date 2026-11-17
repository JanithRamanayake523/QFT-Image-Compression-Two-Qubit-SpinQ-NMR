import numpy as np

from qftimg import hardware as H
from qftimg import analysis as A
from qftimg.verify import run_all, summarise

IMG = [200, 50, 100, 150]


def test_table3_reproduced():
    for k, e in H.EXAMPLES.items():
        er = H.errors(e["T"], e["A"])
        assert abs(er["mae"] - H.TABLE3[k]["mae"]) < 6e-5
        assert abs(er["max"] - H.TABLE3[k]["max"]) < 6e-4
        assert abs(er["tv"] - H.TABLE3[k]["tv"]) < 6e-4
    assert abs(H.overall_mae() - 0.0575) < 5e-5


def test_example3_listed_theory_is_inconsistent_with_matrix():
    c = H.listed_vs_recomputed_theory()
    assert c[1]["consistent"] and c[2]["consistent"] and c[4]["consistent"]
    assert not c[3]["consistent"]       # documented data flag, see README


def test_coefficient_closed_forms():
    assert A.max_closed_form_error(n=300) < 1e-12


def test_k_sweep_values():
    sw = A.k_sweep(IMG)
    assert np.allclose(sw[1]["x_hat"], 136.931, atol=1e-3)
    assert round(sw[1]["psnr"], 1) == 13.0 and round(sw[3]["psnr"], 1) == 20.1
    assert sw[4]["mse"] < 1e-9


def test_exact_mse_law():
    res = A.verify_mse_law(n=1500)
    assert res["max_error_vs_norm2"] < 1e-9 and res["covered"] > 0


def test_brightness_scaling():
    rows = A.brightness_scaling(IMG)
    gains = [rows[i + 1]["psnr"] - rows[i]["psnr"] for i in range(3)]
    assert np.allclose(gains, 20 * np.log10(2))
    assert np.allclose([r["relative_error"] for r in rows], 0.0656, atol=5e-4)


def test_eight_images_exact_cases():
    t = A.test_image_table()
    assert all(t["F Flat"][K]["mse"] < 1e-9 for K in (1, 2, 3))
    assert t["D Checker"][3]["mse"] < 1e-9 and t["H Vertical edge"][2]["mse"] < 1e-9


def test_dc_energy_floor():
    mc = A.monte_carlo(n=1500)
    assert mc["facts"]["dc_min"] >= 0.25


def test_full_verification_has_no_failures():
    checks, _ = run_all(n_law=800, n_mc=1500, log=lambda *_: None)
    s = summarise(checks)
    assert s.get("FAIL", 0) == 0
