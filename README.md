# Secure Data Encryption Using AES-256 and Quantum Techniques

This mini project demonstrates an end-to-end secure communication workflow using BB84 Quantum Key Distribution, quantum-walk-based random basis generation, and AES-256 encryption.

It is designed for a 2nd semester interdisciplinary engineering demonstration and viva. The implementation is educational, modular, beginner-friendly, and suitable for GitHub upload.

## Objectives

- Generate random BB84 bases using Qiskit quantum circuits.
- Simulate Alice and Bob communicating over a quantum channel.
- Perform BB84 basis comparison and key sifting.
- Convert the sifted shared key into a 256-bit AES key using SHA-256.
- Encrypt and decrypt messages using AES-256 CBC mode.
- Visualize basis generation, basis matching, and key statistics.
- Provide both a command-line program and a Streamlit GUI.

## Technologies Used

- Python 3.10+
- Qiskit
- qiskit-aer
- PyCryptodome
- NumPy
- Matplotlib
- Streamlit
- hashlib and base64 from the Python standard library

## Concepts Used

- Quantum Walk based random basis generation
- Superposition
- Hadamard gate
- Quantum randomness
- BB84 Quantum Key Distribution
- Quantum channel simulation
- Classical channel simulation
- Basis matching
- Sifting process
- SHA-256 key derivation
- AES-256 CBC encryption and decryption
- PKCS7 padding
- Initialization Vector (IV)

## Project Structure

```text
Project/
├── quantum_walk.py
├── bb84_protocol.py
├── key_generation.py
├── aes_encryption.py
├── aes_decryption.py
├── utils.py
├── main.py
├── app.py
├── requirements.txt
├── README.md
└── outputs/
```

## Installation

Create and activate a virtual environment:

```bash
cd Project
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Recent Qiskit versions keep the Aer simulator in the separate `qiskit-aer`
package, so it is included in `requirements.txt`.

## How to Run

Run the command-line demonstration:

```bash
python main.py
```

Run with a custom message:

```bash
python main.py --message "CONFIDENTIAL DATA" --qubits 96
```

Run with simulated channel noise:

```bash
python main.py --noise 0.05
```

Run the Streamlit GUI:

```bash
streamlit run app.py
```

## Flow Explanation

1. Alice generates random classical bits.
2. Alice generates random BB84 bases using the quantum walk module.
3. Alice encodes each bit into a Qiskit quantum circuit.
4. Bob independently generates random bases.
5. Bob measures the incoming qubits using his chosen bases.
6. Alice and Bob publicly compare only their basis choices.
7. Matching-basis positions are retained during sifting.
8. The sifted bit string becomes the shared secret key.
9. SHA-256 converts the shared secret into a 256-bit AES key.
10. AES-256 CBC encrypts the plaintext with a random IV.
11. The receiver decrypts the ciphertext using the same AES key.

## Example Output

```text
Alice Bits:
10110101

Alice Bases:
+ × + × + +

Bob Bases:
+ × × × + +

Bob Results:
10100111

Shared Secret Key:
10101

AES-256 Key:
<sha256-derived key>

Plaintext:
HELLO WORLD

Encrypted Text:
<base64 ciphertext>

Decrypted Text:
HELLO WORLD
```

## Output Screenshots

Add screenshots of the terminal output and Streamlit GUI here after running the project.

Generated visualization files are saved in `outputs/`:

- `basis_distribution.png`
- `basis_matching.png`
- `key_statistics.png`
- `sample_output.txt`

## Applications

- Banking security
- Military communication
- Healthcare data protection
- Government communication
- Secure cloud transmission
- Secure messaging systems
- Quantum-safe cybersecurity education

## Advantages

- High security
- Quantum-safe communication model
- Strong randomness from quantum measurement
- AES-256 data protection
- Secure key exchange using BB84
- Protection against unauthorized access
- Modular and easy to demonstrate

## Future Scope

- Real quantum hardware integration
- Quantum internet integration
- Post-quantum cryptography hybrid models
- Advanced eavesdropping detection
- Hybrid classical-quantum systems
- Improved quantum noise models
- Network-based secure messaging demo

## Viva Notes

- BB84 is used to generate a shared secret key, not to encrypt the message directly.
- The Hadamard gate creates superposition, which produces quantum randomness after measurement.
- Basis matching is the reason Alice and Bob can agree on the same secret bits.
- Sifting discards mismatched-basis measurements.
- AES-256 is used because it is fast, widely trusted, and practical for real data encryption.
- SHA-256 converts the variable-length BB84 key into a fixed 256-bit AES key.

## Security Note

This is an educational simulation. Real QKD systems require specialized optical hardware, authenticated classical channels, rigorous privacy amplification, and physical eavesdropping analysis.
