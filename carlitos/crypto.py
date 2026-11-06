"""Development-wallet cryptography (secp256k1 ECDSA + encrypted key files)."""

import hashlib
import json
import os
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

WALLET_VERSION = 1
WALLET_AAD = b"CRLTS-DEVNET-WALLET-v1"
PBKDF2_ITERATIONS = 600_000


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def hash160(data: bytes) -> bytes:
    first = sha256(data)
    try:
        return hashlib.new("ripemd160", first).digest()
    except ValueError as exc:  # pragma: no cover - depends on OpenSSL build
        raise RuntimeError("this Python/OpenSSL build does not provide RIPEMD-160") from exc


def public_key_bytes(private_key: ec.EllipticCurvePrivateKey) -> bytes:
    return private_key.public_key().public_bytes(
        serialization.Encoding.X962,
        serialization.PublicFormat.CompressedPoint,
    )


def address_from_public_key(public_key: bytes) -> str:
    """Return a clearly development-only address, not a finalized mainnet format."""
    return "crltsd" + hash160(public_key).hex()


def generate_private_key() -> ec.EllipticCurvePrivateKey:
    return ec.generate_private_key(ec.SECP256K1())


def private_key_from_hex(secret_hex: str) -> ec.EllipticCurvePrivateKey:
    if len(secret_hex) != 64:
        raise ValueError("private key must be exactly 32 bytes of hexadecimal")
    secret = int(secret_hex, 16)
    return ec.derive_private_key(secret, ec.SECP256K1())


def private_key_hex(private_key: ec.EllipticCurvePrivateKey) -> str:
    number = private_key.private_numbers().private_value
    return number.to_bytes(32, "big").hex()


def sign_digest(private_key: ec.EllipticCurvePrivateKey, digest: bytes) -> str:
    signature = private_key.sign(digest, ec.ECDSA(hashes.SHA256()))
    return signature.hex()


def verify_digest(public_key: bytes, digest: bytes, signature_hex: str) -> bool:
    try:
        key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256K1(), public_key)
        key.verify(bytes.fromhex(signature_hex), digest, ec.ECDSA(hashes.SHA256()))
        return True
    except (ValueError, InvalidSignature):
        return False


def _derive_wallet_key(password: str, salt: bytes) -> bytes:
    if not password:
        raise ValueError("wallet password cannot be empty")
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=PBKDF2_ITERATIONS)
    return kdf.derive(password.encode("utf-8"))


def save_wallet(path: str | Path, private_key: ec.EllipticCurvePrivateKey, password: str) -> str:
    """Write an AES-GCM encrypted wallet; return its public address."""
    destination = Path(path).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    secret = bytes.fromhex(private_key_hex(private_key))
    salt = os.urandom(16)
    nonce = os.urandom(12)
    encryption_key = _derive_wallet_key(password, salt)
    ciphertext = AESGCM(encryption_key).encrypt(nonce, secret, WALLET_AAD)
    public = public_key_bytes(private_key)
    wallet = {
        "version": WALLET_VERSION,
        "network": "carlitos-devnet",
        "address": address_from_public_key(public),
        "public_key": public.hex(),
        "kdf": {"name": "PBKDF2-HMAC-SHA256", "iterations": PBKDF2_ITERATIONS, "salt": salt.hex()},
        "cipher": {"name": "AES-256-GCM", "nonce": nonce.hex(), "ciphertext": ciphertext.hex()},
    }
    temp = destination.with_suffix(destination.suffix + ".tmp")
    temp.write_text(json.dumps(wallet, indent=2) + "\n", encoding="utf-8")
    try:
        os.chmod(temp, 0o600)
    except OSError:  # pragma: no cover - platform-dependent
        pass
    temp.replace(destination)
    return wallet["address"]


def load_wallet(path: str | Path, password: str) -> ec.EllipticCurvePrivateKey:
    source = Path(path).expanduser()
    wallet = json.loads(source.read_text(encoding="utf-8"))
    if wallet.get("version") != WALLET_VERSION or wallet.get("network") != "carlitos-devnet":
        raise ValueError("unsupported wallet format or network")
    salt = bytes.fromhex(wallet["kdf"]["salt"])
    nonce = bytes.fromhex(wallet["cipher"]["nonce"])
    ciphertext = bytes.fromhex(wallet["cipher"]["ciphertext"])
    key = _derive_wallet_key(password, salt)
    try:
        secret = AESGCM(key).decrypt(nonce, ciphertext, WALLET_AAD)
    except Exception as exc:
        raise ValueError("wallet could not be decrypted; check the password") from exc
    private_key = ec.derive_private_key(int.from_bytes(secret, "big"), ec.SECP256K1())
    expected = address_from_public_key(public_key_bytes(private_key))
    if expected != wallet.get("address"):
        raise ValueError("wallet integrity check failed")
    return private_key
