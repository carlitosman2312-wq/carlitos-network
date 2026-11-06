# Carlitos Network

CRLTS is an independent Bitcoin Core-derived SHA-256 proof-of-work blockchain project.

The objective is a native coin with its own blockchain, nodes, mining, wallets, and block explorer—not a token on another blockchain.

## Current status

- Bitcoin Core v32.1 source tree imported on branch integration/bitcoin-core-v32.1.
- Carlitos mainnet genesis, 100 CRLTS initial subsidy, 500,000-block halving schedule, and 100,000,000 CRLTS money range patched in C++.
- Mainnet network magic, ports, address prefixes, Bech32 HRP, and data directory separated from Bitcoin.
- Separate local -chain=carlitosregtest configured for easy development mining; it is not a public testnet.
- C++ node, CLI, wallet, and native test binary build successfully with GCC 16.2 / CMake 4.4.5 on the connected Windows PC.
- Python reference tests: 13/13 pass.
- Bitcoin Core native validation_tests suite: 8/8 pass, including Carlitos mainnet genesis, Carlitos development genesis, and total issuance.
- Full upstream CTest run: 95% passed; 14 tests failed and one was skipped. Several still expect Bitcoin's old address prefixes, monetary ceiling, port, or proof-of-work limit; other failures are specific to the Windows/MSYS2/GCC test environment. See TEST_STATUS.md.
- The daemon executable could not be launched on the Windows PC because Windows Application Control blocked it. Runtime mining/RPC tests therefore remain pending.
- Git commit is local on integration/bitcoin-core-v32.1; pushing to GitHub is waiting for Git Credential Manager authentication.

See PROTOCOL.md, CONSENSUS_REFERENCE.md, UPSTREAM.md, and TEST_STATUS.md.

Not ready for real funds: the proposed mainnet proof-of-work target is provisional and 256 times easier than Bitcoin's historic difficulty-1 target. There are no public seed nodes, public testnet, audited mainnet binaries, or launched chain.
