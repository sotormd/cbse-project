"""
Cryptographic functions, classes and other utilities
"""
import os
import hmac
import time
import struct
import base64
import argon2
from Crypto.Hash import SHA3_512
from Crypto.Cipher import AES
from Crypto.Cipher import ChaCha20_Poly1305


def generate(bits: int) -> bytes:
    """
    Generate cryptographically secure random bits
    :param bits: Length of output
    :return: Cryptographically secure random bits
    """
    return os.urandom(bits // 8)


def encode(data: bytes) -> bytes:
    """
    Encode data in urlsafe base64
    :param data: Data to be encoded
    :return: Urlsafe base64 encoded data
    """
    return base64.urlsafe_b64encode(data)


def decode(data: bytes) -> bytes:
    """
    Decode urlsafe base64 data
    :param data: Data to be decoded
    :return: Decoded data
    """
    return base64.urlsafe_b64decode(data)


def compare(a: str, b: str) -> bool:
    """
    Cryptographically secure string comparison
    :param a: First string
    :param b: Second string
    :return: True if 'a' is equal to 'b' else False
    """
    return hmac.compare_digest(a, b)


def digest(data: bytes) -> bytes:
    """
    Hash data using SHA3/512
    :param data: Data to hash
    :return: 512 bit digest of data
    """
    hasher = SHA3_512.new(data)
    return hasher.digest()


def argon2_derive(pw: bytes, salt: bytes, length: int = 32) -> bytes:
    """
    Argon2 key derivation (raw)
    :param pw: Password
    :param salt: Salt
    :param length: Length of output
    :return: Derived key (raw)
    """
    return argon2.low_level.hash_secret_raw(
        secret=pw,
        salt=salt,
        time_cost=3,
        memory_cost=65536,
        parallelism=4,
        hash_len=length,
        type=argon2.low_level.Type.ID
    )


class AESGCM:
    def __init__(self, key: bytes):
        if len(key) != 32:
            raise ValueError("Incorrect key length for AES")
        self.key = key

    @classmethod
    def generate_key(cls, bits: int = 256) -> bytes:
        """
        Generate an AES GCM key of suitable bits
        :param bits: Length of key; must be 128, 192 or 256
        :return: Generated key
        """
        if bits not in [128, 192, 256]:
            raise ValueError("Incorrect AES key length")
        return generate(bits)

    def encrypt(self, plaintext: bytes, header: bytes = b"") -> bytes:
        """
        Encrypt data using AES GCM
        :param plaintext: Plaintext to encrypt
        :param header: Additional authenticated but unencrypted data (optional)
        :return: Encrypted ciphertext
        """
        cipher = AES.new(self.key, AES.MODE_GCM)
        if header is not None:
            cipher.update(header)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        ciphertext = cipher.nonce + ciphertext + tag
        return ciphertext

    def decrypt(self, ciphertext: bytes, header: bytes = b"") -> bytes:
        """
        Decrypt data using AES GCM
        :param ciphertext: Ciphertext to decrypt
        :param header: Additional authenticated but unencrypted data (optional)
        :return: Decrypted plaintext
        """
        nonce, ciphertext, tag = ciphertext[:16], ciphertext[16:-16], ciphertext[-16:]
        cipher = AES.new(self.key, AES.MODE_GCM, nonce)
        if header is not None:
            cipher.update(header)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext


class XChaCha20Poly1305:
    def __init__(self, key: bytes):
        if len(key) != 32:
            raise ValueError("Incorrect key length for XChaCha20Poly1305")
        self.key = key

    @classmethod
    def generate_key(cls) -> bytes:
        """
        Generate a XChaCha20 Poly1305 key of suitable bits
        :return: 256 bit XChaCha20 Poly1305 key
        """
        return generate(256)

    def encrypt(self, plaintext: bytes, header: bytes = b"") -> bytes:
        """
        Encrypt data using XChaCha20 Poly1305
        :param plaintext: Plaintext to encrypt
        :param header: Additional authenticated but unencrypted data (optional)
        :return: Encrypted ciphertext
        """
        nonce = generate(192)
        cipher = ChaCha20_Poly1305.new(key=self.key, nonce=nonce)
        if header is not None:
            cipher.update(header)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        ciphertext = nonce + ciphertext + tag
        return ciphertext

    def decrypt(self, ciphertext: bytes, header: bytes = b"") -> bytes:
        """
        Decrypt data using XChaCha20 Poly1305
        :param ciphertext: Ciphertext to decrypt
        :param header: Additional authenticated but unencrypted data (optional)
        :return: Decrypted plaintext
        """
        nonce, ciphertext, tag = ciphertext[:24], ciphertext[24:-16], ciphertext[-16:]
        cipher = ChaCha20_Poly1305.new(key=self.key, nonce=nonce)
        if header is not None:
            cipher.update(header)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext


class OTP:
    def __init__(self, key: str, digits: int = 6, digest: str = "sha1"):
        self.key = key
        if len(key) < 16:
            raise ValueError("Incorrect key length")
        self.digits = digits
        self.digest = digest

    def hotp(self, cur_counter: int) -> str:
        """
        Generate HMAC based one time password (HOTP)
        :param cur_counter: Current counter
        :return: Current HOTP
        """
        key = base64.b32decode(self.key.upper() + '=' * ((8 - len(self.key)) % 8))
        counter = struct.pack('>Q', cur_counter)
        mac = hmac.new(key, counter, self.digest).digest()
        offset = mac[-1] & 0x0f
        binary = struct.unpack('>L', mac[offset:offset + 4])[0] & 0x7fffffff
        return str(binary)[-self.digits:].zfill(self.digits)

    def totp(self, interval: int = 30) -> str:
        """
        Generate time based one time password (TOTP)
        :param interval: Time step
        :return: Current TOTP
        """
        return self.hotp(int(time.time() / interval))
