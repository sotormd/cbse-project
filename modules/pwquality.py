"""
Password assessment utilities:
- pwquality(): rate strength with zxcvbn
- check_pwned(): query HaveIBeenPwned API
"""

import hashlib
import requests
import zxcvbn


def pwquality(password: str) -> int:
    """
    Get password quality using zxcvbn
    :param password: Password to assess
    :return: zxcvbn quality score (0–4)
    """
    password = password.strip()
    if not password:
        return 0
    return zxcvbn.zxcvbn(password)["score"]


def check_pwned(password: str) -> int:
    """
    Check if password appears in HaveIBeenPwned (HIBP).
    Uses k-anonymity — only first 5 chars of SHA1 sent to API.
    :param password: Password to check
    :return: number of times seen in breaches, -1 if API unavailable
    """
    sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]

    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
    except Exception:
        return -1

    hashes = (line.split(":") for line in res.text.splitlines())
    for h, c in hashes:
        if h == suffix:
            return int(c)

    return 0
