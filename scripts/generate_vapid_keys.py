#!/usr/bin/env python3
"""
Web Push bildirimleri için VAPID anahtar çifti üretir.
Çıktıyı .env dosyasına ekleyin (VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY).

Kullanım: python scripts/generate_vapid_keys.py
"""

import base64

from cryptography.hazmat.primitives.asymmetric.ec import SECP256R1, generate_private_key
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def main() -> None:
    private_key = generate_private_key(SECP256R1())
    public_key = private_key.public_key()

    private_value = private_key.private_numbers().private_value
    private_bytes = private_value.to_bytes(32, "big")
    public_bytes = public_key.public_bytes(
        Encoding.X962, PublicFormat.UncompressedPoint
    )

    print(f"VAPID_PRIVATE_KEY={_b64url(private_bytes)}")
    print(f"VAPID_PUBLIC_KEY={_b64url(public_bytes)}")


if __name__ == "__main__":
    main()
