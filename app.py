"""Streamlit GUI for the BB84 + AES-256 mini-project."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from aes_decryption import decrypt_message
from aes_encryption import encrypt_message
from bb84_protocol import (
    encode_qubits,
    generate_alice_bases,
    generate_alice_bits,
    generate_bob_bases,
    measure_qubits,
)
from key_generation import (
    generate_aes256_key,
    generate_aes256_key_hex,
    sift_key_details,
)
from utils import bases_to_string, bits_to_string, save_visualizations


PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "outputs"


def initialize_state() -> None:
    """Create Streamlit session defaults."""

    defaults = {
        "qkd_result": None,
        "ciphertext": "",
        "decrypted_text": "",
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def generate_qkd_key(num_qubits: int, noise_probability: float) -> dict[str, object]:
    """Run the quantum part of the project and return display data."""

    alice_bits = generate_alice_bits(num_qubits)
    alice_bases = generate_alice_bases(num_qubits)
    qubits = encode_qubits(alice_bits, alice_bases)
    bob_bases = generate_bob_bases(num_qubits)
    bob_results = measure_qubits(
        qubits,
        bob_bases,
        noise_probability=noise_probability,
    )
    sifted = sift_key_details(alice_bits, alice_bases, bob_bases, bob_results)
    shared_key = str(sifted["shared_key"])

    if not shared_key:
        raise RuntimeError("No bases matched. Please generate the key again.")
    if not bool(sifted["keys_match"]):
        raise RuntimeError("Key mismatch detected. Reduce noise and try again.")

    chart_files = save_visualizations(alice_bases, bob_bases, shared_key, OUTPUT_DIR)

    return {
        "alice_bits": alice_bits,
        "alice_bases": alice_bases,
        "bob_bases": bob_bases,
        "bob_results": bob_results,
        "shared_key": shared_key,
        "aes_key": generate_aes256_key(shared_key),
        "aes_key_hex": generate_aes256_key_hex(shared_key),
        "qber": sifted["qber"],
        "match_count": sifted["match_count"],
        "mismatch_count": sifted["mismatch_count"],
        "chart_files": chart_files,
    }


def render_protocol_outputs(result: dict[str, object]) -> None:
    """Render BB84 protocol data in the GUI."""

    st.subheader("Quantum Key Distribution")
    col1, col2 = st.columns(2)

    with col1:
        st.caption("Alice Bits")
        st.code(bits_to_string(result["alice_bits"]))
        st.caption("Alice Bases")
        st.code(bases_to_string(result["alice_bases"]))

    with col2:
        st.caption("Bob Bases")
        st.code(bases_to_string(result["bob_bases"]))
        st.caption("Bob Results")
        st.code(bits_to_string(result["bob_results"]))

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    metric_col1.metric("Matching Bases", result["match_count"])
    metric_col2.metric("Discarded Bases", result["mismatch_count"])
    metric_col3.metric("QBER", f"{float(result['qber']) * 100:.2f}%")

    st.caption("Shared Secret Key")
    st.code(result["shared_key"])
    st.caption("AES-256 Key")
    st.code(result["aes_key_hex"])


def main() -> None:
    """Start the Streamlit app."""

    st.set_page_config(
        page_title="Secure Quantum AES-256",
        layout="wide",
    )
    initialize_state()

    st.markdown(
        """
        <style>
        .stApp {
            background: #f8fafc;
        }
        section[data-testid="stSidebar"] {
            background: #0f172a;
        }
        section[data-testid="stSidebar"] * {
            color: #f8fafc;
        }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Secure Data Encryption Using AES-256 and Quantum Techniques")

    with st.sidebar:
        st.header("Simulation")
        num_qubits = st.slider("Qubits", min_value=16, max_value=256, value=64, step=8)
        noise_probability = st.slider(
            "Noise probability",
            min_value=0.0,
            max_value=0.30,
            value=0.0,
            step=0.01,
        )

    plaintext = st.text_area(
        "Plaintext Message",
        value="HELLO WORLD",
        height=110,
    )

    button_col1, button_col2, button_col3 = st.columns([1, 1, 1])
    with button_col1:
        generate_clicked = st.button("Generate Key", use_container_width=True)
    with button_col2:
        encrypt_clicked = st.button("Encrypt", use_container_width=True)
    with button_col3:
        decrypt_clicked = st.button("Decrypt", use_container_width=True)

    if generate_clicked:
        try:
            st.session_state.qkd_result = generate_qkd_key(
                num_qubits,
                noise_probability,
            )
            st.session_state.ciphertext = ""
            st.session_state.decrypted_text = ""
            st.success("Shared key generated successfully.")
        except Exception as exc:
            st.error(str(exc))

    if encrypt_clicked:
        try:
            if st.session_state.qkd_result is None:
                st.session_state.qkd_result = generate_qkd_key(
                    num_qubits,
                    noise_probability,
                )

            st.session_state.ciphertext = encrypt_message(
                plaintext,
                st.session_state.qkd_result["aes_key"],
            )
            st.session_state.decrypted_text = ""
            st.success("Message encrypted successfully.")
        except Exception as exc:
            st.error(str(exc))

    if decrypt_clicked:
        try:
            if st.session_state.qkd_result is None:
                raise RuntimeError("Generate a key before decrypting.")
            if not st.session_state.ciphertext:
                raise RuntimeError("Encrypt a message before decrypting.")

            st.session_state.decrypted_text = decrypt_message(
                st.session_state.ciphertext,
                st.session_state.qkd_result["aes_key"],
            )
            st.success("Message decrypted successfully.")
        except Exception as exc:
            st.error(str(exc))

    if st.session_state.qkd_result:
        render_protocol_outputs(st.session_state.qkd_result)

    st.subheader("Classical AES-256 Channel")
    col1, col2 = st.columns(2)
    with col1:
        st.caption("Encrypted Text")
        st.code(st.session_state.ciphertext or "No ciphertext generated yet.")
    with col2:
        st.caption("Decrypted Text")
        st.code(st.session_state.decrypted_text or "No plaintext recovered yet.")

    if st.session_state.qkd_result:
        st.subheader("Visualizations")
        image_cols = st.columns(3)
        for image_col, chart_file in zip(
            image_cols,
            st.session_state.qkd_result["chart_files"],
            strict=False,
        ):
            image_col.image(str(chart_file), use_container_width=True)


if __name__ == "__main__":
    main()
