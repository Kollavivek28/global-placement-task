import base64
import pyotp
import hashlib

def hex_to_base32(hex_seed: str) -> str:
    """
    Convert 64-character hex seed into Base32 string.
    """
    seed_bytes = bytes.fromhex(hex_seed)
    base32_secret = base64.b32encode(seed_bytes).decode("utf-8")
    return base32_secret


def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current 6-digit TOTP code from 64-char hex seed.
    """
    base32_secret = hex_to_base32(hex_seed)

    totp = pyotp.TOTP(
        base32_secret,
        digits=6,
        interval=30,          # 30-second window
        digest=hashlib.sha1,  # SHA-1 required
    )

    return totp.now()


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify a TOTP code with ±valid_window tolerance.
    """
    base32_secret = hex_to_base32(hex_seed)

    totp = pyotp.TOTP(
        base32_secret,
        digits=6,
        interval=30,
        digest=hashlib.sha1,
    )

    return totp.verify(code, valid_window=valid_window)
