"""Command-line workflow for the secure quantum communication mini-project."""

from __future__ import annotations

import argparse
from pathlib import Path

from aes_decryption import decrypt_message
from aes_encryption import encrypt_message
from bb84_protocol import (
    encode_qubits,
    generate_alice_bases,
    generate_alice_bits,
    generate_bob_bases,
    intercept_resend_attack,
    measure_qubits,
)
from key_generation import (
    generate_aes256_key,
    generate_aes256_key_hex,
    sift_key_details,
)
from quantum_walk import generate_random_bases
from utils import bases_to_string, bits_to_string, save_visualizations, write_text_file


PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "outputs"


def run_secure_communication(
    message: str,
    num_qubits: int = 64,
    min_sifted_bits: int = 16,
    noise_probability: float = 0.0,
    simulate_eavesdropper: bool = False,
    create_charts: bool = True,
) -> dict[str, object]:
    """Run the full BB84 + AES-256 secure communication workflow."""

    if not message.strip():
        raise ValueError("Plaintext message cannot be empty.")
    if num_qubits <= 0:
        raise ValueError("num_qubits must be positive.")
    if min_sifted_bits <= 0:
        raise ValueError("min_sifted_bits must be positive.")

    max_attempts = 5

    for attempt in range(1, max_attempts + 1):
        alice_bits = generate_alice_bits(num_qubits)
        alice_bases = generate_alice_bases(num_qubits)
        encoded_qubits = encode_qubits(alice_bits, alice_bases)

        eve_bases = []
        eve_results = []
        if simulate_eavesdropper:
            eve_bases = generate_random_bases(num_qubits)
            encoded_qubits, eve_results = intercept_resend_attack(
                encoded_qubits, eve_bases
            )

        bob_bases = generate_bob_bases(num_qubits)
        bob_results = measure_qubits(
            encoded_qubits,
            bob_bases,
            noise_probability=noise_probability,
        )

        sifted = sift_key_details(alice_bits, alice_bases, bob_bases, bob_results)
        shared_key = str(sifted["shared_key"])

        if len(shared_key) >= min_sifted_bits:
            break
    else:
        raise RuntimeError(
            "Could not generate enough sifted key bits. Increase num_qubits."
        )

    if not bool(sifted["keys_match"]):
        raise RuntimeError(
            "Alice and Bob keys do not match. Noise or eavesdropping was detected."
        )

    aes_key = generate_aes256_key(shared_key)
    aes_key_hex = generate_aes256_key_hex(shared_key)
    ciphertext = encrypt_message(message, aes_key)
    decrypted_text = decrypt_message(ciphertext, aes_key)

    visualization_files = []
    if create_charts:
        visualization_files = save_visualizations(
            alice_bases,
            bob_bases,
            shared_key,
            OUTPUT_DIR,
        )

    return {
        "attempt": attempt,
        "num_qubits": num_qubits,
        "alice_bits": alice_bits,
        "alice_bases": alice_bases,
        "bob_bases": bob_bases,
        "bob_results": bob_results,
        "shared_key": shared_key,
        "bob_shared_key": sifted["bob_shared_key"],
        "keys_match": sifted["keys_match"],
        "qber": sifted["qber"],
        "match_count": sifted["match_count"],
        "mismatch_count": sifted["mismatch_count"],
        "aes_key_hex": aes_key_hex,
        "plaintext": message,
        "ciphertext": ciphertext,
        "decrypted_text": decrypted_text,
        "visualization_files": visualization_files,
        "simulate_eavesdropper": simulate_eavesdropper,
        "eve_bases": eve_bases,
        "eve_results": eve_results,
    }


def format_report(result: dict[str, object]) -> str:
    """Create a readable report for console output and sample output file."""

    lines = [
        "Secure Data Encryption Using AES-256 and Quantum Techniques",
        "=" * 64,
        f"Qubits Used: {result['num_qubits']}",
        f"Generation Attempt: {result['attempt']}",
        f"Eavesdropper Simulation: {result['simulate_eavesdropper']}",
        "",
        f"Alice Bits:\n{bits_to_string(result['alice_bits'])}",
        "",
        f"Alice Bases:\n{bases_to_string(result['alice_bases'])}",
        "",
        f"Bob Bases:\n{bases_to_string(result['bob_bases'])}",
        "",
        f"Bob Results:\n{bits_to_string(result['bob_results'])}",
        "",
        f"Shared Secret Key:\n{result['shared_key']}",
        "",
        f"Keys Match: {result['keys_match']}",
        f"QBER: {float(result['qber']) * 100:.2f}%",
        f"Matching Bases: {result['match_count']}",
        f"Discarded Bases: {result['mismatch_count']}",
        "",
        f"AES-256 Key:\n{result['aes_key_hex']}",
        "",
        f"Plaintext:\n{result['plaintext']}",
        "",
        f"Encrypted Text:\n{result['ciphertext']}",
        "",
        f"Decrypted Text:\n{result['decrypted_text']}",
    ]

    visualization_files = result.get("visualization_files") or []
    if visualization_files:
        lines.append("")
        lines.append("Visualization Files:")
        lines.extend(str(path) for path in visualization_files)

    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line options for demonstration runs."""

    parser = argparse.ArgumentParser(
        description="BB84 QKD + AES-256 secure communication simulation"
    )
    parser.add_argument(
        "--message",
        default="HELLO WORLD",
        help="Plaintext message to encrypt.",
    )
    parser.add_argument(
        "--qubits",
        type=int,
        default=64,
        help="Number of BB84 qubits to simulate.",
    )
    parser.add_argument(
        "--noise",
        type=float,
        default=0.0,
        help="Quantum channel noise probability between 0.0 and 1.0.",
    )
    parser.add_argument(
        "--eavesdropper",
        action="store_true",
        help="Enable intercept-resend eavesdropping simulation.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the complete mini-project demonstration."""

    args = parse_arguments()
    result = run_secure_communication(
        message=args.message,
        num_qubits=args.qubits,
        noise_probability=args.noise,
        simulate_eavesdropper=args.eavesdropper,
    )
    report = format_report(result)
    print(report)

    write_text_file(OUTPUT_DIR / "sample_output.txt", report)


if __name__ == "__main__":
    main()
