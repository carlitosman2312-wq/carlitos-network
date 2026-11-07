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
- Ubuntu 24.04 CI successfully builds the native node, CLI, wallet, and test binary; Python and targeted native consensus tests pass; a two-node regtest smoke test verifies P2P connection, block and mempool-transaction propagation, wallet maturity, mining, and confirmed spend.
- C++ node, CLI, wallet, and native test binary build successfully with GCC 16.2 / CMake 4.4.5 on the connected Windows PC.
- Python reference tests: 13/13 pass.
- Targeted native `validation_tests`: passed (10 Boost test cases), including Carlitos consensus and data-directory isolation checks.
- Full post-fix CTest on Linux: 373 passed, 1 skipped (`script_assets_tests`), 0 failed (374 tests discovered). Both `descriptor_tests` and `bip324_tests` pass. See TEST_STATUS.md for the exact workflow run and limits.
- The rebuilt Windows executables remain blocked by Windows Application Control on that PC; no attempt was made to bypass the policy. The Linux CI runtime smoke test independently verified the local regtest daemon, RPC, wallet, mining, coinbase maturity, and confirmed spend.
- GitHub Actions run #46 (native) and run #40 (Python reference) pass on commit `95d6ff2f72c821c12f0f7a5e5c316828f1db60cf`. Draft PR #2 remains open and unmerged.

See PROTOCOL.md, CONSENSUS_REFERENCE.md, UPSTREAM.md, and TEST_STATUS.md.

Not ready for real funds: the proposed mainnet proof-of-work target is provisional and 256 times easier than Bitcoin's historic difficulty-1 target. There are no public seed nodes, public testnet, audited mainnet binaries, or launched chain.
