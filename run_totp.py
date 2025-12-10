from totp_utils import generate_totp_code, verify_totp_code

def load_hex_seed():
    with open("decrypted_seed.txt", "r") as f:
        return f.read().strip()

if __name__ == "__main__":
    hex_seed = load_hex_seed()
    print("Seed:", repr(hex_seed))
    print("Length:", len(hex_seed))


    code = generate_totp_code(hex_seed)
    print("Generated TOTP code:", code)

    print("Verification:", verify_totp_code(hex_seed, code))
