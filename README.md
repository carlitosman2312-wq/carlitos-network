# Carlitos Network

CRLTS is an independent Bitcoin Core-derived SHA-256 proof-of-work blockchain project.

The objective is a native coin with its own chain, nodes, mining, wallets, and block explorer?not a token on another blockchain.

## Current status

- Bitcoin Core v32.1 source tree imported on branch integration/bitcoin-core-v32.1.
- Carlitos mainnet genesis and monetary consensus rules patched in C++.
- Mainnet network identity and RPC port configured.
- Python reference model and 13 passing tests.
- C++ tests added for reward boundaries, total issuance, mainnet parameters, genesis hash, and the isolated Carlitos development chain.
- A separate -chain=carlitosregtest network is configured for local mining tests; it is not a public testnet.
- Full C++ build, native test suite, independent security review, DNS seeds, and mainnet launch remain pending.

See PROTOCOL.md, CONSENSUS_REFERENCE.md, and UPSTREAM.md for specifications and remaining work.

**Not ready for real funds:** the proposed proof-of-work bootstrap target is provisional and much easier than Bitcoin's historic difficulty-1 target. No public mainnet or testnet has been launched.
