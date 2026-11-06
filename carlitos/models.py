"""Canonical transaction and block data structures for the devnet prototype."""

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any

from cryptography.hazmat.primitives.asymmetric import ec

from .consensus import NETWORK_ID
from .crypto import public_key_bytes, sign_digest


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def sha256d(value: bytes) -> str:
    return hashlib.sha256(hashlib.sha256(value).digest()).hexdigest()


@dataclass(frozen=True)
class TxInput:
    txid: str
    vout: int
    public_key: str = ""
    signature: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"txid": self.txid, "vout": self.vout, "public_key": self.public_key, "signature": self.signature}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TxInput":
        return cls(txid=str(data["txid"]), vout=int(data["vout"]), public_key=str(data.get("public_key", "")), signature=str(data.get("signature", "")))


@dataclass(frozen=True)
class TxOutput:
    amount: int
    address: str

    def to_dict(self) -> dict[str, Any]:
        return {"amount": self.amount, "address": self.address}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TxOutput":
        return cls(amount=int(data["amount"]), address=str(data["address"]))


@dataclass(frozen=True)
class Transaction:
    inputs: tuple[TxInput, ...] = field(default_factory=tuple)
    outputs: tuple[TxOutput, ...] = field(default_factory=tuple)
    version: int = 1

    def signing_digest(self, input_index: int) -> bytes:
        payload = {
            "network": NETWORK_ID,
            "version": self.version,
            "inputs": [{"txid": item.txid, "vout": item.vout} for item in self.inputs],
            "outputs": [item.to_dict() for item in self.outputs],
            "input_index": input_index,
        }
        return hashlib.sha256(canonical_json(payload)).digest()

    def to_dict(self) -> dict[str, Any]:
        return {"version": self.version, "inputs": [item.to_dict() for item in self.inputs], "outputs": [item.to_dict() for item in self.outputs]}

    @property
    def txid(self) -> str:
        return sha256d(canonical_json(self.to_dict()))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Transaction":
        return cls(
            version=int(data.get("version", 1)),
            inputs=tuple(TxInput.from_dict(item) for item in data.get("inputs", [])),
            outputs=tuple(TxOutput.from_dict(item) for item in data.get("outputs", [])),
        )

    @classmethod
    def coinbase(cls, height: int, address: str, amount: int) -> "Transaction":
        # Coinbase data is represented by its unique height marker in the devnet prototype.
        return cls(inputs=(TxInput(txid=f"coinbase:{height}", vout=0),), outputs=(TxOutput(amount=amount, address=address),))

    @classmethod
    def signed(
        cls,
        private_key: ec.EllipticCurvePrivateKey,
        coins: list[tuple[str, int, int]],
        outputs: list[TxOutput],
    ) -> "Transaction":
        """Build a signed transaction. coins contain (txid, vout, amount)."""
        public_hex = public_key_bytes(private_key).hex()
        unsigned = cls(
            inputs=tuple(TxInput(txid=txid, vout=vout, public_key=public_hex) for txid, vout, _ in coins),
            outputs=tuple(outputs),
        )
        signed_inputs = tuple(
            TxInput(
                txid=item.txid,
                vout=item.vout,
                public_key=public_hex,
                signature=sign_digest(private_key, unsigned.signing_digest(index)),
            )
            for index, item in enumerate(unsigned.inputs)
        )
        return cls(inputs=signed_inputs, outputs=tuple(outputs))


@dataclass(frozen=True)
class Block:
    height: int
    previous_hash: str
    timestamp: int
    nonce: int
    transactions: tuple[Transaction, ...]
    difficulty: int
    version: int = 1

    def header_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "height": self.height,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "difficulty": self.difficulty,
            "merkle_root": merkle_root([tx.txid for tx in self.transactions]),
        }

    @property
    def block_hash(self) -> str:
        return sha256d(canonical_json(self.header_dict()))

    @property
    def work(self) -> int:
        return 1 << (4 * self.difficulty)

    def to_dict(self) -> dict[str, Any]:
        return {**self.header_dict(), "transactions": [tx.to_dict() for tx in self.transactions], "hash": self.block_hash}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Block":
        return cls(
            version=int(data.get("version", 1)),
            height=int(data["height"]),
            previous_hash=str(data["previous_hash"]),
            timestamp=int(data["timestamp"]),
            nonce=int(data["nonce"]),
            difficulty=int(data["difficulty"]),
            transactions=tuple(Transaction.from_dict(item) for item in data.get("transactions", [])),
        )


def merkle_root(txids: list[str]) -> str:
    if not txids:
        return hashlib.sha256(b"").hexdigest()
    layer = [bytes.fromhex(item) for item in txids]
    while len(layer) > 1:
        if len(layer) % 2:
            layer.append(layer[-1])
        layer = [hashlib.sha256(hashlib.sha256(layer[i] + layer[i + 1]).digest()).digest() for i in range(0, len(layer), 2)]
    return layer[0].hex()
