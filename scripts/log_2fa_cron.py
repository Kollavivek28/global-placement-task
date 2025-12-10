#!/usr/bin/env python3
import sys
import os

# Add parent directory so we can import totp_utils.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from totp_utils import generate_totp_code
from datetime import datetime, timezone

SEED_FILE = "/data/seed.txt"

def load_hex_seed():
    try:
        with open(SEED_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("ERROR: /data/seed.txt NOT FOUND")
        return None

def main():
    hex_seed = load_hex_seed()
    if not hex_seed:
        return

    try:
        code = generate_totp_code(hex_seed)
    except Exception as e:
        print(f"ERROR generating TOTP: {e}")
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} - 2FA Code: {code}")

if __name__ == "__main__":
    main()
