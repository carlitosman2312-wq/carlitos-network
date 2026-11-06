import time

import pytest

from carlitos.chain import Chain, ConsensusError
from carlitos.consensus import COIN
from carlitos.crypto import address_from_public_key, generate_private_key, public_key_bytes
from carlitos.models import Block, Transaction, TxOutput


def mine_to(chain: Chain, address: str, height: int):
    while chain.height < height:
        chain.mine_block(address)


def test_genesis_has_no_premine_and_first_block_has_reward():
    key = generate_private_key()
    address = address_from_public_key(public_key_bytes(key))
    chain = Chain(difficulty=1)
    assert chain.height == 0
    assert chain.balance(address) == 0
    block = chain.mine_block(address)
    assert block.height == 1
    assert chain.balance(address) == 100 * COIN


def test_coinbase_maturity_and_signed_transaction():
    sender = generate_private_key()
    recipient = generate_private_key()
    sender_address = address_from_public_key(public_key_bytes(sender))
    recipient_address = address_from_public_key(public_key_bytes(recipient))
    chain = Chain(difficulty=1)

    chain.mine_block(sender_address)
    coinbase = chain.blocks[1].transactions[0]
    tx = Transaction.signed(sender, [(coinbase.txid, 0, 100 * COIN)], [TxOutput(99 * COIN, recipient_address)])
    with pytest.raises(ConsensusError, match="maturity"):
        chain.add_transaction(tx)

    mine_to(chain, sender_address, 100)
    # The first coinbase is now mature at height 100.
    chain.add_transaction(tx)
    block = chain.mine_block(sender_address)
    assert block.height == 101
    assert chain.balance(recipient_address) == 99 * COIN
    assert chain.balance(sender_address) == 10_000 * COIN - 100 * COIN + 100 * COIN + 1 * COIN


def test_invalid_proof_of_work_is_rejected():
    key = generate_private_key()
    address = address_from_public_key(public_key_bytes(key))
    chain = Chain(difficulty=2)
    timestamp = max(int(time.time()), chain.median_time_past() + 1)
    coinbase = Transaction.coinbase(1, address, 100 * COIN)
    nonce = 0
    bad = Block(1, chain.tip.block_hash, timestamp, nonce, (coinbase,), 2)
    while bad.block_hash.startswith("00"):
        nonce += 1
        bad = Block(1, chain.tip.block_hash, timestamp, nonce, (coinbase,), 2)
    with pytest.raises(ConsensusError, match="proof-of-work"):
        chain.add_block(bad)


def test_chain_persistence_revalidates_blocks(tmp_path):
    key = generate_private_key()
    address = address_from_public_key(public_key_bytes(key))
    chain = Chain(difficulty=1)
    chain.mine_block(address)
    path = tmp_path / "chain.json"
    chain.save(path)
    restored = Chain.load(path)
    assert restored.height == 1
    assert restored.tip.block_hash == chain.tip.block_hash
    assert restored.balance(address) == 100 * COIN
