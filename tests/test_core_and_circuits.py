import numpy as np
import pytest

from qftimg import compress, qft_matrix, amplitude_encode, select_top_k, mse, psnr
from qftimg import circuits as C

IMG = [200, 50, 100, 150]


def test_f4_matches_study_matrix():
    expected = 0.5 * np.array([[1, 1, 1, 1], [1, 1j, -1, -1j], [1, -1, 1, -1], [1, -1j, -1, 1j]])
    assert np.allclose(qft_matrix(2), expected)


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_qft_is_unitary(n):
    F = qft_matrix(n)
    assert np.allclose(F.conj().T @ F, np.eye(2 ** n))


def test_amplitude_encoding():
    psi, norm = amplitude_encode(IMG)
    assert np.isclose(norm, 50 * np.sqrt(30))
    assert np.isclose(np.sum(psi ** 2), 1)
    assert np.allclose(psi, np.array([4, 1, 2, 3]) / np.sqrt(30))


def test_coefficients_and_selection():
    r = compress(IMG, 2)
    assert np.allclose(r.y, np.array([5, 1 - 1j, 1, 1 + 1j]) / np.sqrt(30))
    assert r.selected == [0, 1]                      # tie between y1 and y3 -> smaller index
    assert np.isclose(r.energy_kept, 0.9)


def test_headline_numbers():
    r = compress(IMG, 2)
    assert np.allclose(r.x_hat, [158.114, 105.409, 105.409, 158.114], atol=1e-3)
    assert round(r.mse, 2) == 1229.93
    assert round(r.psnr, 2) == 17.23


def test_tie_choice_does_not_change_real_reconstruction():
    assert np.allclose(compress(IMG, 2).x_hat, compress(IMG, 2, selected=[0, 3]).x_hat)


def test_k_equals_n_is_lossless_and_psnr_infinite():
    r = compress(IMG, 4)
    assert np.allclose(r.x_hat, IMG)
    assert psnr(r.mse) == float("inf")


def test_select_top_k_ties():
    assert select_top_k([1.0, 0.5, 0.5, 0.5], 2) == [0, 1]
    assert select_top_k([0.5, 0.5, 1.0, 0.5], 2) == [0, 2]


def test_zero_image_rejected():
    with pytest.raises(ValueError):
        amplitude_encode([0, 0, 0, 0])


def test_non_power_of_two_rejected():
    with pytest.raises(ValueError):
        compress([1, 2, 3], 1)


def test_larger_image_runs():
    rng = np.random.default_rng(0)
    r = compress(rng.uniform(1, 255, 16), 8)         # 4x4 image, 4 qubits
    assert r.x_hat.shape == (16,) and r.psnr > 0


def test_manual_circuit_equals_f4_numpy():
    assert np.allclose(C.manual_qft_matrix(), qft_matrix(2))
    assert np.allclose(C.manual_iqft_matrix(), qft_matrix(2).conj().T)


def test_classical_fft_reference():
    r = compress(IMG, 2)
    assert np.allclose(C.classical_fft_reference(IMG), r.y)


@pytest.mark.skipif(not C.qiskit_available(), reason="Qiskit / Aer not installed")
def test_qiskit_circuits():
    F = qft_matrix(2)
    assert np.allclose(C.qiskit_operator_matrix(C.manual_circuit()), F)
    assert np.allclose(C.qiskit_builtin_qft_matrix(), F)


@pytest.mark.skipif(not C.qiskit_available(), reason="Qiskit / Aer not installed")
def test_aer_shots_match_probabilities():
    p = C.aer_probabilities(IMG, shots=2048, seed=1)
    assert np.max(np.abs(p - np.abs(compress(IMG, 2).y) ** 2)) < 0.04
