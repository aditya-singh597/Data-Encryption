"""AES-256 CBC encryption module."""

from __future__ import annotations

import base64

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

from utils import normalize_aes_key


def encrypt_message(message: str, key: bytes | str) -> str:
    """Encrypt plaintext with AES-256 in CBC mode.

    AES-256 is used because it is a widely trusted symmetric encryption
    algorithm. BB84 supplies the shared secret, and SHA-256 converts that secret
    into the fixed 32-byte key size required by AES-256.
    """

    if not isinstance(message, str):
        raise TypeError("message must be a string.")
    if not message.strip():
        raise ValueError("message cannot be empty.")

    try:
        aes_key = normalize_aes_key(key)
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        padded_message = pad(message.encode("utf-8"), AES.block_size)
        encrypted_message = cipher.encrypt(padded_message)
        payload = iv + encrypted_message
        return base64.b64encode(payload).decode("utf-8")

    except (TypeError, ValueError):
        raise
    except Exception as exc:
        raise RuntimeError("Encryption failed. Please check the message and key.") from exc
