"""AES-256 CBC decryption module."""

from __future__ import annotations

import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from utils import normalize_aes_key


def decrypt_message(ciphertext: str, key: bytes | str) -> str:
    """Decrypt a base64 encoded AES-CBC payload.

    The first 16 bytes of the decoded payload are the IV. The remaining bytes
    are the ciphertext. If the key is wrong or the data was modified, unpadding
    usually fails, which is reported as a key mismatch/corruption error.
    """

    if not isinstance(ciphertext, str):
        raise TypeError("ciphertext must be a string.")
    if not ciphertext.strip():
        raise ValueError("ciphertext cannot be empty.")

    try:
        aes_key = normalize_aes_key(key)
        payload = base64.b64decode(ciphertext, validate=True)

        if len(payload) <= AES.block_size:
            raise ValueError("ciphertext payload is too short.")

        iv = payload[: AES.block_size]
        encrypted_message = payload[AES.block_size :]
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        decrypted_padded_message = cipher.decrypt(encrypted_message)
        return unpad(decrypted_padded_message, AES.block_size).decode("utf-8")

    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Decryption failed. The key may be wrong or the ciphertext may be corrupted."
        ) from exc
    except Exception as exc:
        raise RuntimeError("Unexpected decryption failure.") from exc
