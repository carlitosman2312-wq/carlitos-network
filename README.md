# Carlitos Network

CRLTS is an independent Bitcoin Core-derived SHA-256 proof-of-work blockchain project.

The objective is a native coin with its own blockchain, nodes, mining, wallets, and block explorer—not a token on another blockchain.

## Current status

- Bitcoin Core v32.1 source tree imported on branch integration/bitcoin-core-v32.1.
- Carlitos mainnet genesis, 100 CRLTS initial subsidy, 500,000-block halving schedule, and 100,000,000 CRLTS money range patched in C++.
- Mainnet network magic, ports, address prefixes, Bech32 HRP, extended-key serialization versions, and data directory separated from Bitcoin.
- Mainnet BIP32 public/private versions use provisional custom bytes `043c524c` / `043c5350`; they are not registered in SLIP-0132. The descriptor wallet still derives with Bitcoin coin type `0'` on mainnet and `1'` on test chains, so a CRLTS-specific derivation path/SLIP-0044 coin type remains a launch blocker.
- Separate `-chain=carlitostestnet` public-testnet parameter set (P2P 48444 / RPC 48446, 10-minute retargeting, manual `-addnode` bootstrap; not deployed yet).
- Separate local `-chain=carlitosregtest` for instant mining (P2P 38444 / RPC 38446, HRP `rcrl`); it is not a public testnet.
- BIP94 timewarp protection is enforced from genesis on all Carlitos networks; on public testnet, retargets anchor to the first block of each period to prevent min-difficulty resets.
- Extended BIP32 serialization prefixes are isolated for mainnet, testnet, and regtest; these provisional custom values still need external wallet review and registry work.
- Ubuntu 24.04 native workflow #57 passes on PR head `1aff7ff030db0f45a044087fa53803849fde5198`: native build, generated config, Python reference suite, targeted native consensus, BIP94 retarget test, two-node regtest smoke including BIP94 timestamp rejection, and full CTest.
- C++ node, CLI, wallet, and native test binary build successfully with GCC 16.2 / CMake 4.4.5 on the connected Windows PC.
- Python reference workflow #51 on the same head: 13/13 tests pass.
- Targeted native `validation_tests`: 10 Boost test cases pass, including Carlitos consensus and data-directory isolation.
- Full CTest on Linux: 374 discovered, 373 passed, 1 skipped (`script_assets_tests`), 0 failed. See TEST_STATUS.md for workflow details and limitations.
- The rebuilt Windows executables remain blocked by Windows Application Control on that PC; no attempt was made to bypass the policy. The Linux CI runtime smoke test independently verified the local regtest daemon, RPC, wallet, mining, coinbase maturity, and confirmed spend.
- Current validated PR head: `1aff7ff030db0f45a044087fa53803849fde5198`; native workflow #57 and reference workflow #51 passed. Draft PR #2 remains open for review.

See PROTOCOL.md, CONSENSUS_REFERENCE.md, UPSTREAM.md, and TEST_STATUS.md.

Not ready for real funds: the proposed mainnet proof-of-work target is provisional and 256 times easier than Bitcoin's historic difficulty-1 target. There are no deployed public seed nodes, independent public-testnet operators, audited mainnet binaries, or launched chain.
