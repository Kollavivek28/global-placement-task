from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
import os
import pyotp
import time

app = FastAPI()

DATA_PATH = "/data"
SEED_FILE = f"{DATA_PATH}/seed.txt"


# -----------------------------
# Models for requests
# -----------------------------

class DecryptRequest(BaseModel):
    encrypted_seed: str


class VerifyRequest(BaseModel):
    code: str


# -----------------------------
# Helper functions
# -----------------------------

def decrypt_seed(encrypted_b64: str) -> str:
    """Decrypt Base64 encrypted seed using private key → return 64-char hex string"""

    # Load private key
    with open("student_private.pem", "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
        )

    # Base64 decode
    try:
        encrypted_bytes = base64.b64decode(encrypted_b64)
    except Exception:
        raise Exception("Invalid Base64")

    # RSA OAEP decrypt
    try:
        decrypted_bytes = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception:
        raise Exception("RSA decryption failed")

    # Convert to UTF-8 string
    try:
        seed_hex = decrypted_bytes.decode()
    except:
        raise Exception("Invalid UTF-8 output")

    # Validate length & hex format
    if len(seed_hex) != 64 or any(c not in "0123456789abcdef" for c in seed_hex.lower()):
        raise Exception("Invalid 64-character hex seed")

    return seed_hex


def load_seed() -> str:
    """Load seed from file"""
    if not os.path.exists(SEED_FILE):
        raise Exception("Seed not decrypted yet")

    with open(SEED_FILE, "r") as f:
        seed = f.read().strip()

    if len(seed) != 64:
        raise Exception("Invalid seed length in file")

    return seed


def hex_to_base32(hex_seed: str) -> str:
    """Convert hex → bytes → Base32 (pyotp requirement)"""
    seed_bytes = bytes.fromhex(hex_seed)
    return base64.b32encode(seed_bytes).decode()


# -----------------------------
# ENDPOINT 1: POST /decrypt-seed
# -----------------------------

@app.post("/decrypt-seed")
def post_decrypt_seed(req: DecryptRequest):
    try:
        seed_hex = decrypt_seed(req.encrypted_seed)

        # Ensure /data directory exists
        os.makedirs(DATA_PATH, exist_ok=True)

        # Save seed
        with open(SEED_FILE, "w") as f:
            f.write(seed_hex)

        return {"status": "ok"}

    except Exception as e:
        return {"error": str(e)}



# -----------------------------
# ENDPOINT 2: GET /generate-2fa
# -----------------------------

@app.get("/generate-2fa")
def get_generate_2fa():
    try:
        hex_seed = load_seed()

        base32_key = hex_to_base32(hex_seed)

        totp = pyotp.TOTP(base32_key, digits=6, interval=30)

        code = totp.now()

        # Remaining seconds in this period
        remaining = 30 - (int(time.time()) % 30)

        return {
            "code": code,
            "valid_for": remaining
        }

    except Exception as e:
        return {"error": str(e)}



# -----------------------------
# ENDPOINT 3: POST /verify-2fa
# -----------------------------

@app.post("/verify-2fa")
def post_verify_2fa(req: VerifyRequest):
    try:
        if not req.code:
            raise HTTPException(status_code=400, detail="Missing code")

        hex_seed = load_seed()
        base32_key = hex_to_base32(hex_seed)

        totp = pyotp.TOTP(base32_key, digits=6, interval=30)

        # ±1 time window
        valid = totp.verify(req.code, valid_window=1)

        return {"valid": bool(valid)}

    except HTTPException as h:
        raise h

    except Exception as e:
        return {"error": str(e)}
