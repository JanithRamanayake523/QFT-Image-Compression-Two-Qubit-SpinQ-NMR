"""Gate-level two-qubit QFT.

`manual_qft_matrix()` builds the study's manual circuit (H, controlled-phase pi/2, H, SWAP)
from explicit gate matrices (no Qiskit needed) and must equal the analytic matrix F4.

Qubit-ordering convention (same as Qiskit): basis index = 2*q1 + q0, i.e. |q1 q0>.
Gate order in the circuit:  H(q1); CP(pi/2; control=q0, target=q1); H(q0); SWAP(q0,q1).

The optional functions use Qiskit / Aer; call `qiskit_available()` first.
"""
from __future__ import annotations

import numpy as np
from .core import amplitude_encode

I2 = np.eye(2)
H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
SWAP = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=complex)


def _on(gate1q, qubit):
    """Embed a 1-qubit gate on `qubit` (0 = least significant) of a 2-qubit register."""
    return np.kron(gate1q, I2) if qubit == 1 else np.kron(I2, gate1q)


def _cp(theta):
    """Controlled-phase (symmetric in the two qubits): phase on |11>."""
    return np.diag([1, 1, 1, np.exp(1j * theta)])


def manual_qft_matrix() -> np.ndarray:
    U = _on(H, 1)               # H on q1
    U = _cp(np.pi / 2) @ U      # controlled phase pi/2
    U = _on(H, 0) @ U           # H on q0
    U = SWAP @ U                # restore bit order
    return U


def manual_iqft_matrix() -> np.ndarray:
    """Inverse circuit: inverse unitary (reverse order, controlled phase -pi/2)."""
    return manual_qft_matrix().conj().T


# ----------------------------------------------------------------------------- optional: Qiskit
def qiskit_available() -> bool:
    try:
        import qiskit  # noqa: F401
        import qiskit_aer  # noqa: F401
        return True
    except Exception:
        return False


def manual_circuit(measure: bool = False, state=None):
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(2)
    if state is not None:
        qc.prepare_state(np.asarray(state, dtype=complex), [0, 1])
    qc.h(1)
    qc.cp(np.pi / 2, 0, 1)
    qc.h(0)
    qc.swap(0, 1)
    if measure:
        qc.measure_all()
    return qc


def qiskit_operator_matrix(circuit) -> np.ndarray:
    from qiskit.quantum_info import Operator
    return Operator(circuit).data


def qiskit_builtin_qft_matrix() -> np.ndarray:
    """Matrix of Qiskit's built-in 2-qubit QFT (with swaps)."""
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator
    qc = QuantumCircuit(2)
    try:
        from qiskit.circuit.library import QFTGate
        qc.append(QFTGate(2), [0, 1])
    except Exception:  # older Qiskit
        from qiskit.circuit.library import QFT
        qc.append(QFT(2, do_swaps=True), [0, 1])
    return Operator(qc).data


def aer_probabilities(x, shots: int = 2048, seed: int = 2026) -> np.ndarray:
    """Shot-based Aer experiment: prepare psi, apply the manual QFT, measure.
    Returns empirical probabilities ordered |00>,|01>,|10>,|11>."""
    from qiskit_aer import AerSimulator
    from qiskit import transpile
    psi, _ = amplitude_encode(x)
    qc = manual_circuit(measure=True, state=psi)
    sim = AerSimulator(seed_simulator=seed)
    counts = sim.run(transpile(qc, sim), shots=shots).result().get_counts()
    p = np.zeros(4)
    for bitstring, c in counts.items():
        p[int(bitstring.replace(" ", ""), 2)] += c      # Qiskit prints "q1 q0" -> index 2*q1+q0
    return p / shots


def classical_fft_reference(x) -> np.ndarray:
    """Classical reference: unitary DFT with the +i sign convention (numpy ifft * sqrt(N))."""
    psi, _ = amplitude_encode(x)
    return np.fft.ifft(psi) * np.sqrt(psi.size)
