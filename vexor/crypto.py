"""AES-256-CBC encryption for C2 channel."""

import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7


def derive_key(password: bytes) -> bytes:
    return hashlib.sha256(password).digest()


def encrypt(plaintext: bytes, key: bytes) -> bytes:
    key = derive_key(key)
    iv = os.urandom(16)
    padder = PKCS7(128).padder()
    padded = padder.update(plaintext) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    enc = cipher.encryptor()
    ct = enc.update(padded) + enc.finalize()
    return base64.b64encode(iv + ct)


def decrypt(ciphertext: bytes, key: bytes) -> bytes:
    key = derive_key(key)
    data = base64.b64decode(ciphertext)
    iv, ct = data[:16], data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    dec = cipher.decryptor()
    padded = dec.update(ct) + dec.finalize()
    unpadder = PKCS7(128).unpadder()
    return unpadder.update(padded) + unpadder.finalize()
