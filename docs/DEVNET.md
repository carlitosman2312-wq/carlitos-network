# CRLTS local devnet prototype

This repository now includes a small Python prototype to exercise the first parts of the CRLTS design. It is intentionally **not Bitcoin-compatible and not suitable for real funds**. It is a local learning and integration scaffold, not a replacement for the Bitcoin Core-derived production implementation described in `PROTOCOL.md`.

## What works in this prototype

- Deterministic genesis block with no premine and a zero genesis subsidy.
- Integer-only monetary accounting, including the 100 CRLTS subsidy and 500,000-block halving schedule.
- Local secp256k1 ECDSA keys and encrypted wallet files (PBKDF2-HMAC-SHA256 + AES-256-GCM).
- A simplified UTXO ledger with signatures, duplicate-input checks, fees, and 100-block coinbase maturity.
- SHA-256d block identifiers and an intentionally easy local proof-of-work target.
- JSON chain persistence with block revalidation on load.
- Loopback-only JSON API for status, block lookup, balances, transaction submission, and mining.
- Automated tests and a GitHub Actions test workflow.

## Important differences from the intended protocol

The devnet uses a fixed, intentionally weak proof-of-work target (one leading hexadecimal zero by default). It does not implement Bitcoin's compact target format, 2,016-block difficulty adjustment, full script system, peer-to-peer gossip/synchronization, transaction replacement, fee policy, or Bitcoin Core's consensus rules. Its address encoding is a temporary development format (`crltsd` + HASH160 hex), not the final Base58/Bech32 format. The current API is unauthenticated and must stay bound to `127.0.0.1`.

Do not expose the node RPC to the internet, use the wallet with real funds, advertise this as a secure network, or launch a public mainnet from this code.

## Requirements

- Python 3.11 or newer
- `cryptography` (installed by the package manager)

## Quick start

```bash
python -m pip install -e ".[dev]"
crlts init
crlts wallet new --file ./alice-wallet.json
```

Start the node:

```bash
crlts node --host 127.0.0.1 --port 8338
```

In a second terminal, mine a block to the wallet address printed when the wallet was created by calling the running node API:

```bash
curl -X POST http://127.0.0.1:8338/mine \
  -H 'Content-Type: application/json' \
  -d '{"address":"crltsd<40-hex-characters>"}'
```

Inspect node status and balances:

```bash
curl http://127.0.0.1:8338/info
curl http://127.0.0.1:8338/address/crltsd<40-hex-characters>
```

The offline `crlts mine` command can also mine directly into a local database while the node is stopped; do not use offline mining against the same database while a node process is running. Coinbase rewards become spendable after 100 confirmations. Keep wallet files encrypted, back them up offline, and never share the password or private key.

## Test

```bash
python -m pip install -e ".[dev]"
pytest
```

## Next engineering milestones

1. Replace this educational chain engine with a reviewed Bitcoin Core-derived implementation.
2. Finalize and test mainnet/testnet magic bytes, ports, address prefixes, proof-of-work limit, and exact retarget semantics.
3. Implement P2P networking, peer discovery, cumulative-work chain selection, and robust reorganization handling.
4. Add the full script/transaction validation model and consensus test vectors.
5. Add reproducible cross-platform builds, fuzzing, public testnet operations, and independent security review.
