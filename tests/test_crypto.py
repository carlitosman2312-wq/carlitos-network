from pathlib import Path

import pytest

from carlitos.crypto import address_from_public_key, generate_private_key, load_wallet, public_key_bytes, save_wallet


def test_wallet_round_trip_and_wrong_password(tmp_path: Path):
    path = tmp_path / "wallet.json"
    private_key = generate_private_key()
    address = save_wallet(path, private_key, "a-strong-test-password")
    restored = load_wallet(path, "a-strong-test-password")
    assert address == address_from_public_key(public_key_bytes(restored))
    with pytest.raises(ValueError, match="could not be decrypted"):
        load_wallet(path, "wrong-password")
