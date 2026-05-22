"""Quantum Walk based random basis generation for BB84.

Quantum Walk idea used here:
    A quantum walk uses a quantum "coin" to place the walker into a
    superposition of possible directions. In this educational simulation, each
    qubit acts as a quantum coin. A Hadamard gate creates an equal superposition
    of 0 and 1, and measurement collapses it into a truly quantum-random value.

Mapping:
    measured 0 -> '+' rectilinear basis
    measured 1 -> '×' diagonal basis
"""

from __future__ import annotations

from qiskit import QuantumCircuit

from utils import (
    DIAGONAL_BASIS,
    RECTILINEAR_BASIS,
    sample_quantum_circuit,
    validate_positive_integer,
)


def _build_quantum_walk_circuit(n: int) -> QuantumCircuit:
    """Build a simple quantum-walk-inspired coin circuit.

    The Hadamard gate is used because it converts |0> into a superposition:
        H|0> = (|0> + |1>) / sqrt(2)

    That means a later measurement gives 0 or 1 with quantum randomness. A line
    of controlled-Z gates adds phase interaction between neighboring coins,
    representing a lightweight walk/interference step while keeping the output
    beginner-friendly for a mini-project demonstration.
    """

    circuit = QuantumCircuit(n, name="quantum_walk_basis_generator")

    # Superposition step: every qubit becomes a quantum coin with two possible
    # outcomes at once until measurement happens.
    for qubit_index in range(n):
        circuit.h(qubit_index)

    # Interference step: neighboring quantum coins receive phase coupling, a
    # compact way to demonstrate the "walk" aspect without hiding the BB84 flow.
    for qubit_index in range(n - 1):
        circuit.cz(qubit_index, qubit_index + 1)

    return circuit


def generate_random_bases(n: int) -> list[str]:
    """Generate n BB84 basis choices using quantum measurement.

    Args:
        n: Number of basis symbols required.

    Returns:
        A list containing '+' and '×' symbols.

    Raises:
        ValueError: If n is not a positive integer.
    """

    validate_positive_integer(n, "n")

    # Local simulators and statevector fallbacks have practical qubit limits.
    # The protocol can still request any n, so we generate the basis stream in
    # small quantum-walk chunks and concatenate the measured quantum-random bits.
    max_chunk_size = 16
    measured_bits: list[int] = []

    while len(measured_bits) < n:
        chunk_size = min(max_chunk_size, n - len(measured_bits))
        circuit = _build_quantum_walk_circuit(chunk_size)
        measured_bits.extend(sample_quantum_circuit(circuit, chunk_size))

    return [
        RECTILINEAR_BASIS if bit == 0 else DIAGONAL_BASIS
        for bit in measured_bits
    ]


if __name__ == "__main__":
    print(generate_random_bases(10))
