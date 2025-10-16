"""
Generate reliably secure passwords and passphrases
"""

import os
import string
import secrets

WORDS_LIST_FILE = os.path.join("data", "words_alpha.txt")

with open(WORDS_LIST_FILE, "r") as file:
    WORDS_LIST = [x for x in file.read().split() if len(x) >= 5]


def generate_password(uppercase: bool = True, lowercase: bool = True, digits: bool = True, symbols: bool = True, length: int = 24):
    chars = str()

    if uppercase:
        chars += string.ascii_uppercase
    if lowercase:
        chars += string.ascii_lowercase
    if digits:
        chars += string.digits
    if symbols:
        chars += string.punctuation

    password = "".join(secrets.choice(chars) for _ in range(length))

    return password


def generate_passphrase(length: int = 6, separator: str = "-"):
    passphrase = separator.join(secrets.choice(WORDS_LIST) for _ in range(length))

    return passphrase