import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization

def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP.

    Args:
        encrypted_seed_b64: Base64-encoded ciphertext string
        private_key: RSA private key object

    Returns:
        Decrypted 64-character hex seed
    """

    # 1. Base64 decode the encrypted seed
    encrypted_bytes = base64.b64decode(encrypted_seed_b64)

    # 2. RSA/OAEP decrypt with SHA-256
    decrypted_bytes = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        )
    )

    # 3. Decode bytes to UTF-8 string (hex text)
    hex_seed = decrypted_bytes.decode("utf-8")

    # 4. Validate: must be 64-character hex string
    if len(hex_seed) != 64:
        raise ValueError(f"Invalid seed length {len(hex_seed)}. Expected 64.")

    allowed = "0123456789abcdef"
    if any(ch not in allowed for ch in hex_seed.lower()):
        raise ValueError("Seed contains invalid characters.")

    # 5. Return hex seed
    return hex_seed


# ------------ Runner function to load files --------------

def run_decrypt():
    # Load private key
    with open("student_private.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )

    # Load encrypted seed (Base64)
    with open("encrypted_seed.txt", "r") as f:
        encrypted_seed_b64 = f.read().strip()

    # Decrypt it
    hex_seed = decrypt_seed(encrypted_seed_b64, private_key)

    # Save output (DO NOT COMMIT)
    with open("decrypted_seed.txt", "w") as f:
        f.write(hex_seed)

    print("Decrypted seed saved to decrypted_seed.txt")


# Run automatically
run_decrypt()
