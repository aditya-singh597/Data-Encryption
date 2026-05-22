"""Basis comparison, sifting, and AES-256 key derivation."""

from __future__ import annotations

import hashlib
from typing import Sequence

from utils import (
    bits_to_string,
    ensure_equal_lengths,
    validate_bases,
    validate_bit_list,
)


def sift_key_details(
    alice_bits: Sequence[int],
    alice_bases: Sequence[str],
    bob_bases: Sequence[str],
    bob_results: Sequence[int],
) -> dict[str, object]:
    """Compare bases and keep only the bits where Alice and Bob matched.

    This is called the sifting process. Alice and Bob publicly compare basis
    choices, but they never reveal the actual bit values used for the secret key.
    """

    validate_bit_list(alice_bits, "alice_bits")
    validate_bases(alice_bases, "alice_bases")
    validate_bases(bob_bases, "bob_bases")
    validate_bit_list(bob_results, "bob_results")
    ensure_equal_lengths(alice_bits, alice_bases, bob_bases, bob_results)

    matching_indices: list[int] = []
    discarded_indices: list[int] = []
    alice_shared_bits: list[int] = []
    bob_shared_bits: list[int] = []

    for index, (alice_bit, alice_basis, bob_basis, bob_bit) in enumerate(
        zip(alice_bits, alice_bases, bob_bases, bob_results, strict=True)
    ):
        if alice_basis == bob_basis:
            matching_indices.append(index)
            alice_shared_bits.append(alice_bit)
            bob_shared_bits.append(bob_bit)
        else:
            discarded_indices.append(index)

    alice_shared_key = bits_to_string(alice_shared_bits)
    bob_shared_key = bits_to_string(bob_shared_bits)
    qber = calculate_qber(alice_shared_key, bob_shared_key)

    return {
        "matching_indices": matching_indices,
        "discarded_indices": discarded_indices,
        "alice_shared_key": alice_shared_key,
        "bob_shared_key": bob_shared_key,
        "shared_key": alice_shared_key,
        "match_count": len(matching_indices),
        "mismatch_count": len(discarded_indices),
        "qber": qber,
        "keys_match": alice_shared_key == bob_shared_key,
    }


def sift_keys(
    alice_bits: Sequence[int],
    alice_bases: Sequence[str],
    bob_bases: Sequence[str],
    bob_results: Sequence[int],
) -> str:
    """Return Alice and Bob's sifted shared secret key as a bit string."""

    details = sift_key_details(alice_bits, alice_bases, bob_bases, bob_results)
    return str(details["shared_key"])


def calculate_qber(alice_key: str, bob_key: str) -> float:
    """Calculate Quantum Bit Error Rate for matching-basis positions."""

    if len(alice_key) != len(bob_key):
        raise ValueError("Alice and Bob keys must have the same length.")
    if not alice_key:
        return 0.0

    errors = sum(alice_bit != bob_bit for alice_bit, bob_bit in zip(alice_key, bob_key))
    return errors / len(alice_key)


def generate_aes256_key(shared_secret_key: str) -> bytes:
    """Convert the BB84 bit string into a 256-bit AES key using SHA-256."""

    if not shared_secret_key:
        raise ValueError("Shared secret key cannot be empty.")

    return hashlib.sha256(shared_secret_key.encode("utf-8")).digest()


def generate_aes256_key_hex(shared_secret_key: str) -> str:
    """Return the SHA-256 derived AES key in hexadecimal for display."""

    return generate_aes256_key(shared_secret_key).hex()
