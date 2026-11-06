# Carlitos Network

**CRLTS** is an independent Bitcoin-style blockchain project. The intended design is a native coin with its own chain, nodes, SHA-256 proof-of-work mining, wallets, and block explorer—not a token deployed on another chain.

## Repository status

The repository contains the initial protocol baseline and a **local Python devnet prototype (v0.1.0)** that can create encrypted wallets, mine blocks, validate simple signed UTXO transactions, persist a local chain, and expose a loopback-only JSON API.

This prototype is experimental, intentionally simplified, and **not Bitcoin-compatible or production-secure**. No public mainnet or public testnet has launched. Do not use it for real funds.

- [Protocol baseline](PROTOCOL.md)
- [Local devnet guide and limitations](docs/DEVNET.md)

## Quick start

```bash
python -m pip install -e ".[dev]"
crlts init
crlts wallet new --file ./alice-wallet.json
crlts node --host 127.0.0.1 --port 8338
```

In another terminal, mine through the running node API (replace the placeholder with your wallet address):

```bash
curl -X POST http://127.0.0.1:8338/mine \
  -H 'Content-Type: application/json' \
  -d '{"address":"crltsd<40-hex-characters>"}'
```

Run tests with `python -m pytest`. See [docs/DEVNET.md](docs/DEVNET.md) for the complete instructions and security limitations.
