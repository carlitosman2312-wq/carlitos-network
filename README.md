# Carlitos Network

CRLTS is an independent Bitcoin Core-derived SHA-256 proof-of-work blockchain project.

The objective is a native coin with its own blockchain, nodes, mining, wallets, and block explorer—not a token on another blockchain.

## Current status

- Bitcoin Core v32.1 source tree imported on branch integration/bitcoin-core-v32.1.
- Carlitos mainnet genesis, 100 CRLTS initial subsidy, 500,000-block halving schedule, and 100,000,000 CRLTS money range patched in C++.
- Mainnet network magic, ports, address prefixes, Bech32 HRP, extended-key serialization versions, and data directory separated from Bitcoin.
- Mainnet BIP32 public/private versions use provisional custom bytes `043c524c` / `043c5350`; they are not yet registered in SLIP-0132. BIP44 coin type and canonical derivation path remain unassigned.
- Separate `-chain=carlitostestnet` public-testnet parameter set (P2P 48444 / RPC 48446, 10-minute retargeting, manual `-addnode` bootstrap; not deployed yet).
- Separate local `-chain=carlitosregtest` for instant mining (P2P 38444 / RPC 38446, HRP `rcrl`); it is not a public testnet.
- Extended BIP32 serialization prefixes are isolated for mainnet, testnet, and regtest; these provisional custom values still need external wallet review and registry work.
- Ubuntu CI now builds the native node, runs consensus tests and a node/wallet/coinbase-maturity/transaction smoke test, then runs the full CTest suite. Results are pending.
- C++ node, CLI, wallet, and native test binary build successfully with GCC 16.2 / CMake 4.4.5 on the connected Windows PC.
- Python reference tests: 13/13 pass.
- Bitcoin Core native validation_tests suite: 8/8 pass, including Carlitos mainnet genesis, Carlitos development genesis, and total issuance.
- Baseline full upstream CTest (before Carlitos-specific fixture updates): 95% passed; 14 tests failed and one was skipped. Chain-specific address/WIF, money, RPC, miner, PoW, and chainstate test fixtures have since been adapted and the updated native test binary compiles. A complete post-fix rerun is pending Linux CI; cryptographic BIP324 failures still require supported-platform reproduction. See TEST_STATUS.md.
- The daemon executable could not be launched on the Windows PC because Windows Application Control blocked it. Runtime mining/RPC tests therefore remain pending.
- The integration branch has been pushed to GitHub. Draft PR #2 is open for review and CI validation; it has not been merged into main.

See PROTOCOL.md, CONSENSUS_REFERENCE.md, UPSTREAM.md, and TEST_STATUS.md.

Not ready for real funds: the proposed mainnet proof-of-work target is provisional and 256 times easier than Bitcoin's historic difficulty-1 target. There are no public seed nodes, public testnet, audited mainnet binaries, or launched chain.
