"""BB84 Quantum Key Distribution protocol simulation.

BB84 is a Quantum Key Distribution (QKD) protocol. QKD does not encrypt the
message directly; it helps Alice and Bob create a shared secret key. The key is
then used by a classical encryption algorithm such as AES-256.

The BB84 idea:
    1. Alice creates random bits.
    2. Alice encodes each bit in a random basis.
    3. Bob measures each qubit in his own random basis.
    4. Alice and Bob publicly compare only their bases, not the bit values.
    5. Bits where the bases match become the sifted shared key.
"""

from __future__ import annotations

import secrets
from typing import Sequence

from qiskit import QuantumCircuit

from quantum_walk import generate_random_bases
from utils import (
    DIAGONAL_BASIS,
    RECTILINEAR_BASIS,
    ensure_equal_lengths,
    sample_quantum_circuit,
    validate_bases,
    validate_bit_list,
    validate_positive_integer,
)


def generate_alice_bits(n: int) -> list[int]:
    """Generate Alice's random classical bits."""

    validate_positive_integer(n, "n")
    return [secrets.randbits(1) for _ in range(n)]


def generate_alice_bases(n: int) -> list[str]:
    """Generate Alice's BB84 bases using the quantum walk module."""

    return generate_random_bases(n)


def generate_bob_bases(n: int) -> list[str]:
    """Generate Bob's independent BB84 bases using the quantum walk module."""

    return generate_random_bases(n)


def encode_qubits(bits: Sequence[int], bases: Sequence[str]) -> list[QuantumCircuit]:
    """Encode Alice's bits into BB84 qubit states.

    Encoding rules:
        bit 0, basis + -> |0>
        bit 1, basis + -> |1>
        bit 0, basis × -> |+>
        bit 1, basis × -> |->

    The diagonal basis states |+> and |-> are created with the Hadamard gate.
    """

    validate_bit_list(bits, "bits")
    validate_bases(bases, "bases")
    ensure_equal_lengths(bits, bases)

    encoded_qubits: list[QuantumCircuit] = []

    for index, (bit, basis) in enumerate(zip(bits, bases, strict=True)):
        circuit = QuantumCircuit(1, name=f"alice_qubit_{index}")

        if basis == RECTILINEAR_BASIS:
            if bit == 1:
                circuit.x(0)  # |0> becomes |1>

        elif basis == DIAGONAL_BASIS:
            if bit == 0:
                circuit.h(0)  # |0> becomes |+>
            else:
                circuit.x(0)
                circuit.h(0)  # |1> becomes |->

        encoded_qubits.append(circuit)

    return encoded_qubits


def measure_qubits(
    qubits: Sequence[QuantumCircuit],
    bob_bases: Sequence[str],
    noise_probability: float = 0.0,
) -> list[int]:
    """Measure incoming qubits using Bob's bases.

    If Bob uses the same basis as Alice, the measurement gives the correct bit.
    If Bob uses a different basis, quantum mechanics makes the result random.
    Qiskit simulation naturally produces that behavior.
    """

    if not qubits:
        raise ValueError("qubits cannot be empty.")
    validate_bases(bob_bases, "bob_bases")
    ensure_equal_lengths(qubits, bob_bases)

    if not 0.0 <= noise_probability <= 1.0:
        raise ValueError("noise_probability must be between 0.0 and 1.0.")

    bob_results: list[int] = []
    random_source = secrets.SystemRandom()

    for qubit_circuit, bob_basis in zip(qubits, bob_bases, strict=True):
        measurement_circuit = qubit_circuit.copy()

        # Measuring in the diagonal basis means applying Hadamard before the
        # final Z-basis measurement. This maps |+> -> |0> and |-> -> |1>.
        if bob_basis == DIAGONAL_BASIS:
            measurement_circuit.h(0)

        measured_bit = sample_quantum_circuit(measurement_circuit, 1)[0]

        # Optional quantum channel noise for demonstrations and viva questions.
        if noise_probability > 0 and random_source.random() < noise_probability:
            measured_bit = 1 - measured_bit

        bob_results.append(measured_bit)

    return bob_results


def intercept_resend_attack(
    qubits: Sequence[QuantumCircuit],
    eve_bases: Sequence[str],
) -> tuple[list[QuantumCircuit], list[int]]:
    """Bonus: simulate a simple eavesdropper.

    Eve measures each qubit in her own random basis and sends a newly encoded
    qubit to Bob. Wrong-basis measurements introduce detectable errors in the
    sifted key.
    """

    eve_results = measure_qubits(qubits, eve_bases)
    resent_qubits = encode_qubits(eve_results, eve_bases)
    return resent_qubits, eve_results
