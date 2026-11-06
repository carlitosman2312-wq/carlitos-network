"""A deliberately limited, single-node development chain for CRLTS."""

from dataclasses import dataclass
import json
import os
from pathlib import Path
import time

from .consensus import COINBASE_MATURITY, MAX_MONEY, subsidy
from .crypto import address_from_public_key, verify_digest
from .models import Block, Transaction, TxOutput

GENESIS_TIMESTAMP = 1_700_000_000
GENESIS_PREVIOUS_HASH = "0" * 64
DEVNET_DIFFICULTY = 1  # One leading hexadecimal zero; intentionally easy for local testing.
MAX_FUTURE_SECONDS = 7_200


class ConsensusError(ValueError):
    pass


@dataclass(frozen=True)
class UTXO:
    txid: str
    vout: int
    amount: int
    address: str
    height: int
    coinbase: bool

    def to_dict(self) -> dict[str, object]:
        return {"txid": self.txid, "vout": self.vout, "amount": self.amount, "address": self.address, "height": self.height, "coinbase": self.coinbase}


class Chain:
    def __init__(self, difficulty: int = DEVNET_DIFFICULTY) -> None:
        if not 1 <= difficulty <= 4:
            raise ValueError("devnet difficulty must be between 1 and 4 leading hex zeroes")
        self.difficulty = difficulty
        self.blocks: list[Block] = [Block(0, GENESIS_PREVIOUS_HASH, GENESIS_TIMESTAMP, 0, tuple(), difficulty)]
        self.utxos: dict[tuple[str, int], UTXO] = {}
        self.mempool: list[Transaction] = []

    @property
    def height(self) -> int:
        return len(self.blocks) - 1

    @property
    def tip(self) -> Block:
        return self.blocks[-1]

    @property
    def chainwork(self) -> int:
        return sum(block.work for block in self.blocks[1:])

    def median_time_past(self) -> int:
        stamps = sorted(block.timestamp for block in self.blocks[-11:])
        return stamps[len(stamps) // 2]

    def get_utxos(self, address: str, mature_only: bool = False) -> list[UTXO]:
        results = []
        for item in self.utxos.values():
            if item.address != address:
                continue
            if mature_only and item.coinbase and self.height - item.height < COINBASE_MATURITY:
                continue
            results.append(item)
        return sorted(results, key=lambda item: (item.height, item.txid, item.vout))

    def balance(self, address: str, mature_only: bool = False) -> int:
        return sum(item.amount for item in self.get_utxos(address, mature_only=mature_only))

    def _validate_transaction(self, tx: Transaction, spent: set[tuple[str, int]] | None = None) -> int:
        if not tx.inputs or not tx.outputs:
            raise ConsensusError("transaction must contain at least one input and output")
        if len(tx.inputs) > 100 or len(tx.outputs) > 100:
            raise ConsensusError("transaction exceeds devnet input/output limits")
        total_out = sum(output.amount for output in tx.outputs)
        if any(output.amount <= 0 or output.amount > MAX_MONEY for output in tx.outputs):
            raise ConsensusError("transaction output amount is outside the monetary range")
        if any(len(output.address) != 46 or not output.address.startswith("crltsd") or any(ch not in "0123456789abcdef" for ch in output.address[6:]) for output in tx.outputs):
            raise ConsensusError("transaction contains an invalid CRLTS devnet address")
        if total_out > MAX_MONEY:
            raise ConsensusError("transaction output total exceeds maximum money")
        seen: set[tuple[str, int]] = set()
        total_in = 0
        for index, txin in enumerate(tx.inputs):
            key = (txin.txid, txin.vout)
            if key in seen or (spent is not None and key in spent):
                raise ConsensusError("transaction contains a duplicate or already-spent input")
            seen.add(key)
            coin = self.utxos.get(key)
            if coin is None:
                raise ConsensusError(f"referenced output does not exist or is already spent: {txin.txid}:{txin.vout}")
            if coin.coinbase and self.height + 1 - coin.height < COINBASE_MATURITY:
                raise ConsensusError("coinbase output has not reached 100-block maturity")
            try:
                public = bytes.fromhex(txin.public_key)
            except ValueError:
                raise ConsensusError("input public key is malformed") from None
            if address_from_public_key(public) != coin.address:
                raise ConsensusError("input public key does not control the referenced output")
            if not verify_digest(public, tx.signing_digest(index), txin.signature):
                raise ConsensusError("input signature is invalid")
            total_in += coin.amount
            if total_in > MAX_MONEY:
                raise ConsensusError("transaction input total exceeds maximum money")
        if total_in < total_out:
            raise ConsensusError("transaction spends more than its inputs")
        return total_in - total_out

    def add_transaction(self, tx: Transaction) -> str:
        if any(existing.txid == tx.txid for existing in self.mempool):
            raise ConsensusError("transaction is already in the mempool")
        already_pending = {
            (txin.txid, txin.vout)
            for existing in self.mempool
            for txin in existing.inputs
        }
        self._validate_transaction(tx, spent=already_pending)
        self.mempool.append(tx)
        return tx.txid

    def _apply_transaction(self, tx: Transaction, height: int, coinbase: bool) -> None:
        if not coinbase:
            for txin in tx.inputs:
                self.utxos.pop((txin.txid, txin.vout))
        for index, output in enumerate(tx.outputs):
            self.utxos[(tx.txid, index)] = UTXO(tx.txid, index, output.amount, output.address, height, coinbase)

    def validate_block(self, block: Block, now: int | None = None) -> tuple[int, list[Transaction]]:
        if block.height != self.height + 1:
            raise ConsensusError("block height is not the next chain height")
        if block.previous_hash != self.tip.block_hash:
            raise ConsensusError("block does not extend the current tip")
        if block.difficulty != self.difficulty:
            raise ConsensusError("block uses an unexpected devnet difficulty")
        if block.timestamp <= self.median_time_past():
            raise ConsensusError("block timestamp must be greater than median-time-past")
        current_time = int(time.time()) if now is None else now
        if block.timestamp > current_time + MAX_FUTURE_SECONDS:
            raise ConsensusError("block timestamp is too far in the future")
        if not block.block_hash.startswith("0" * self.difficulty):
            raise ConsensusError("block does not satisfy the devnet proof-of-work target")
        if not block.transactions:
            raise ConsensusError("block must contain a coinbase transaction")
        if len(block.transactions[0].inputs) != 1:
            raise ConsensusError("first transaction must be the coinbase transaction")
        coinbase_input = block.transactions[0].inputs[0]
        if coinbase_input.txid != f"coinbase:{block.height}" or coinbase_input.vout != 0 or coinbase_input.public_key or coinbase_input.signature:
            raise ConsensusError("coinbase transaction has an invalid height marker")
        if any(not tx.inputs or tx.inputs[0].txid.startswith("coinbase:") for tx in block.transactions[1:]):
            raise ConsensusError("block contains an unexpected coinbase transaction")
        txids = [tx.txid for tx in block.transactions]
        if len(txids) != len(set(txids)):
            raise ConsensusError("block contains duplicate transactions")

        # Validate regular transactions against a temporary view so an invalid block is atomic.
        original = self.utxos
        self.utxos = dict(original)
        total_fees = 0
        regular = list(block.transactions[1:])
        try:
            spent: set[tuple[str, int]] = set()
            for tx in regular:
                fee = self._validate_transaction(tx, spent=spent)
                spent.update((item.txid, item.vout) for item in tx.inputs)
                total_fees += fee
                self._apply_transaction(tx, block.height, coinbase=False)
        except Exception:
            self.utxos = original
            raise
        self.utxos = original
        coinbase_outputs = block.transactions[0].outputs
        if not coinbase_outputs:
            raise ConsensusError("coinbase transaction must create at least one output")
        if any(output.amount <= 0 or output.amount > MAX_MONEY for output in coinbase_outputs):
            raise ConsensusError("coinbase output amount is outside the monetary range")
        if any(len(output.address) != 46 or not output.address.startswith("crltsd") or any(ch not in "0123456789abcdef" for ch in output.address[6:]) for output in coinbase_outputs):
            raise ConsensusError("coinbase contains an invalid CRLTS devnet address")
        coinbase_total = sum(output.amount for output in coinbase_outputs)
        if coinbase_total > subsidy(block.height) + total_fees:
            raise ConsensusError("coinbase pays more than subsidy plus transaction fees")
        if coinbase_total > MAX_MONEY:
            raise ConsensusError("coinbase exceeds maximum money")
        return total_fees, regular

    def add_block(self, block: Block) -> None:
        _, regular = self.validate_block(block)
        # All validation succeeded; now apply state changes.
        self._apply_transaction(block.transactions[0], block.height, coinbase=True)
        for tx in regular:
            self._apply_transaction(tx, block.height, coinbase=False)
        self.blocks.append(block)
        included = {tx.txid for tx in block.transactions}
        self.mempool = [tx for tx in self.mempool if tx.txid not in included]

    def mine_block(self, reward_address: str, max_transactions: int = 1_000, now: int | None = None) -> Block:
        if not reward_address.startswith("crltsd") or len(reward_address) != 46:
            raise ValueError("reward address is not a valid CRLTS devnet address")
        timestamp = max(int(time.time()) if now is None else now, self.median_time_past() + 1)
        selected: list[Transaction] = []
        fees = 0
        spent: set[tuple[str, int]] = set()
        for tx in self.mempool[:max_transactions]:
            try:
                fee = self._validate_transaction(tx, spent=spent)
            except ConsensusError:
                continue
            selected.append(tx)
            fees += fee
            spent.update((item.txid, item.vout) for item in tx.inputs)
        height = self.height + 1
        reward = subsidy(height) + fees
        coinbase = Transaction.coinbase(height, reward_address, reward)
        transactions = (coinbase, *selected)
        nonce = 0
        while True:
            candidate = Block(height, self.tip.block_hash, timestamp, nonce, tuple(transactions), self.difficulty)
            if candidate.block_hash.startswith("0" * self.difficulty):
                self.add_block(candidate)
                return candidate
            nonce += 1

    def export(self) -> dict[str, object]:
        return {"format": 1, "difficulty": self.difficulty, "blocks": [block.to_dict() for block in self.blocks]}

    @classmethod
    def from_export(cls, data: dict[str, object]) -> "Chain":
        if data.get("format") != 1:
            raise ValueError("unsupported chain database format")
        chain = cls(difficulty=int(data["difficulty"]))
        blocks = [Block.from_dict(item) for item in data["blocks"]]  # type: ignore[index]
        if not blocks or blocks[0].height != 0 or blocks[0].block_hash != chain.blocks[0].block_hash:
            raise ConsensusError("chain database has an invalid genesis block")
        for block in blocks[1:]:
            chain.add_block(block)
        return chain

    def save(self, path: str | Path) -> None:
        destination = Path(path).expanduser()
        destination.parent.mkdir(parents=True, exist_ok=True)
        temp = destination.with_suffix(destination.suffix + ".tmp")
        temp.write_text(json.dumps(self.export(), indent=2) + "\n", encoding="utf-8")
        os.replace(temp, destination)

    @classmethod
    def load(cls, path: str | Path, difficulty: int = DEVNET_DIFFICULTY) -> "Chain":
        source = Path(path).expanduser()
        if not source.exists():
            return cls(difficulty=difficulty)
        data = json.loads(source.read_text(encoding="utf-8"))
        return cls.from_export(data)
