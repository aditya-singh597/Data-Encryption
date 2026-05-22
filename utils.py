"""Utility helpers for the secure quantum communication demo.

This file keeps small shared operations in one place so the project modules stay
focused on their own responsibilities: quantum basis generation, BB84, key
derivation, and AES encryption.
"""

from __future__ import annotations

import secrets
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np


RECTILINEAR_BASIS = "+"
DIAGONAL_BASIS = "×"
VALID_BASES = {RECTILINEAR_BASIS, DIAGONAL_BASIS}


def validate_positive_integer(value: int, name: str = "value") -> None:
    """Raise a clear error when a required count is not a positive integer."""

    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer.")


def validate_bit_list(bits: Sequence[int], name: str = "bits") -> None:
    """Validate that a sequence contains only classical binary values 0 and 1."""

    if not bits:
        raise ValueError(f"{name} cannot be empty.")

    invalid_bits = [bit for bit in bits if bit not in (0, 1)]
    if invalid_bits:
        raise ValueError(f"{name} must contain only 0 and 1 values.")


def validate_bases(bases: Sequence[str], name: str = "bases") -> None:
    """Validate BB84 basis symbols.

    In this project '+' means rectilinear basis and '×' means diagonal basis.
    """

    if not bases:
        raise ValueError(f"{name} cannot be empty.")

    invalid_bases = [basis for basis in bases if basis not in VALID_BASES]
    if invalid_bases:
        raise ValueError(f"{name} must contain only '+' and '×' values.")


def ensure_equal_lengths(*sequences: Sequence[object]) -> None:
    """Raise an error if protocol lists do not describe the same qubits."""

    lengths = {len(sequence) for sequence in sequences}
    if len(lengths) != 1:
        raise ValueError("All protocol sequences must have the same length.")


def bits_to_string(bits: Iterable[int]) -> str:
    """Convert a list of bits into a compact string such as '10101'."""

    return "".join(str(bit) for bit in bits)


def bases_to_string(bases: Iterable[str]) -> str:
    """Convert basis symbols into a readable spaced string."""

    return " ".join(bases)


def normalize_aes_key(key: bytes | str) -> bytes:
    """Return a valid 32-byte AES-256 key.

    AES-256 requires exactly 256 bits, which is 32 bytes. The BB84 sifted key is
    a variable-length bit string, so the project hashes it with SHA-256 before
    encryption. If a caller already passes 32 bytes, those bytes are used as-is.
    """

    import hashlib

    if isinstance(key, bytes):
        if len(key) == 32:
            return key
        if not key:
            raise ValueError("AES key bytes cannot be empty.")
        return hashlib.sha256(key).digest()

    if isinstance(key, str):
        if not key:
            raise ValueError("Shared secret key cannot be empty.")
        return hashlib.sha256(key.encode("utf-8")).digest()

    raise TypeError("AES key must be provided as bytes or string.")


def _bitstring_to_qubit_order(bitstring: str, num_bits: int) -> list[int]:
    """Convert a Qiskit result bitstring into qubit-index order.

    Qiskit count keys are printed with the highest classical bit on the left.
    Reversing gives a beginner-friendly list where index 0 is qubit 0.
    """

    clean_bitstring = bitstring.replace(" ", "")
    if len(clean_bitstring) < num_bits:
        clean_bitstring = clean_bitstring.zfill(num_bits)

    return [int(bit) for bit in clean_bitstring[::-1][:num_bits]]


def sample_quantum_circuit(circuit, num_bits: int) -> list[int]:
    """Measure a Qiskit circuit once and return classical bits.

    The preferred path uses qiskit-aer, which is the normal local simulator for
    Qiskit projects. The fallback uses Qiskit's Statevector class, so the code
    can still run in environments where Aer is installed separately.
    """

    validate_positive_integer(num_bits, "num_bits")

    seed = secrets.randbits(32)

    try:
        from qiskit import transpile
        from qiskit_aer import AerSimulator

        measured_circuit = circuit.copy()
        if measured_circuit.num_clbits == 0:
            measured_circuit.measure_all()

        simulator = AerSimulator(seed_simulator=seed)
        compiled_circuit = transpile(measured_circuit, simulator)
        result = simulator.run(compiled_circuit, shots=1).result()
        counts = result.get_counts()
        sampled_bitstring = max(counts, key=counts.get)
        return _bitstring_to_qubit_order(sampled_bitstring, num_bits)

    except Exception:
        from qiskit.quantum_info import Statevector

        # Statevector cannot simulate measurement operations directly. The BB84
        # modules pass unmeasured circuits here, but this keeps the helper safer.
        if hasattr(circuit, "remove_final_measurements"):
            state_circuit = circuit.remove_final_measurements(inplace=False)
        else:
            state_circuit = circuit

        state = Statevector.from_instruction(state_circuit)
        probabilities = state.probabilities()
        rng = np.random.default_rng(secrets.randbits(64))
        sampled_index = int(rng.choice(len(probabilities), p=probabilities))
        sampled_bitstring = format(sampled_index, f"0{state_circuit.num_qubits}b")
        return _bitstring_to_qubit_order(sampled_bitstring, num_bits)


def save_visualizations(
    alice_bases: Sequence[str],
    bob_bases: Sequence[str],
    shared_key: str,
    output_dir: str | Path,
) -> list[Path]:
    """Create matplotlib charts for the mini-project output folder."""

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    validate_bases(alice_bases, "alice_bases")
    validate_bases(bob_bases, "bob_bases")
    ensure_equal_lengths(alice_bases, bob_bases)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    saved_files: list[Path] = []

    alice_counts = Counter(alice_bases)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(
        ["Rectilinear (+)", "Diagonal (×)"],
        [alice_counts[RECTILINEAR_BASIS], alice_counts[DIAGONAL_BASIS]],
        color=["#2563eb", "#16a34a"],
    )
    ax.set_title("Alice Basis Generation Distribution")
    ax.set_ylabel("Count")
    ax.grid(axis="y", alpha=0.25)
    basis_file = output_path / "basis_distribution.png"
    fig.tight_layout()
    fig.savefig(basis_file, dpi=160)
    plt.close(fig)
    saved_files.append(basis_file)

    matching_count = sum(
        alice_basis == bob_basis
        for alice_basis, bob_basis in zip(alice_bases, bob_bases, strict=True)
    )
    mismatching_count = len(alice_bases) - matching_count

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(
        [matching_count, mismatching_count],
        labels=["Matching bases", "Discarded bases"],
        autopct="%1.1f%%",
        colors=["#0f766e", "#f97316"],
        startangle=90,
    )
    ax.set_title("BB84 Basis Matching")
    matching_file = output_path / "basis_matching.png"
    fig.tight_layout()
    fig.savefig(matching_file, dpi=160)
    plt.close(fig)
    saved_files.append(matching_file)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(
        ["Total qubits", "Matching bases", "Secret key bits"],
        [len(alice_bases), matching_count, len(shared_key)],
        color=["#334155", "#0891b2", "#7c3aed"],
    )
    ax.set_title("Key Generation Statistics")
    ax.set_ylabel("Count")
    ax.grid(axis="y", alpha=0.25)
    stats_file = output_path / "key_statistics.png"
    fig.tight_layout()
    fig.savefig(stats_file, dpi=160)
    plt.close(fig)
    saved_files.append(stats_file)

    return saved_files


def write_text_file(path: str | Path, content: str) -> None:
    """Write UTF-8 text and create parent folders if required."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
