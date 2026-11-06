# Bitcoin Core upstream baseline

## Selected source baseline

- Upstream: https://github.com/bitcoin/bitcoin
- Tag: v32.1
- Commit: f0de87f040621468b956f01f526a43a010310501
- Release: https://github.com/bitcoin/bitcoin/releases/tag/v32.1

The full v32.1 source tree was fetched from the official upstream repository and merged into the integration/bitcoin-core-v32.1 branch. The upstream commit remains in Git history as a merge parent, and upstream COPYING/license notices are retained.

## Carlitos changes made in this branch

- src/kernel/chainparams.cpp: Carlitos mainnet genesis, PoW limit, 600-second spacing, 1,209,600-second target timespan, P2P port, network magic, address prefixes, Bech32 HRP, empty seed lists, and removal of Bitcoin-specific assume-valid, assume-UTXO, and header-sync assumptions.
- src/chainparamsbase.cpp: separate Carlitos mainnet RPC port and local development RPC port.
- src/consensus/params.h: configurable initial subsidy and first reward height with Bitcoin-compatible defaults for inherited chain types.
- src/consensus/amount.h: MAX_MONEY increased to the 100,000,000 CRLTS protocol ceiling.
- src/validation.cpp: subsidy calculation in integer base units.
- src/util/chaintype.*, src/chainparams.*, src/kernel/chainparams.*, src/bitcoin-cli.cpp, src/qt/guiutil.cpp: dedicated carlitosregtest chain type, isolated from Bitcoin regtest.
- src/common/args.cpp, src/init.cpp, src/clientversion.cpp, CMakeLists.txt: Carlitos client identity, configuration name, PID file, and separate default data directory.
- src/test/validation_tests.cpp: reward boundary, total issuance, mainnet parameter/genesis, and development-network tests.
- .github/workflows/native-build.yml: Linux CI build and targeted native consensus smoke suite.

## Local validation on 2026-11-06

- CMake configure: successful.
- Native build: 601/601 steps successful. Built bitcoind.exe, bitcoin-cli.exe, bitcoin-wallet.exe, bitcoin.exe, and test_bitcoin.exe.
- Python reference tests: 13/13 pass.
- Native validation_tests: 8/8 pass.
- Full CTest: 95% passed, 14 failures, 1 skipped. Most failures are inherited test vectors still hard-coded for Bitcoin's bc1/Base58 prefixes, 21-million-coin cap, 8333 port, or 0x1d00ffff work limit. Some tests also crash or are blocked under this Windows/MSYS2/GCC environment. They are not being described as passing; see TEST_STATUS.md.
- Launching the daemon was blocked by Windows Application Control. No policy bypass was attempted, so RPC, wallet operations, P2P, and mined blocks have not been smoke-tested.
- The Git branch and commit exist locally. Git push has not completed because Git Credential Manager is waiting for GitHub authentication.

## Remaining engineering work before public use

1. Adapt or replace all inherited tests that assume Bitcoin's old mainnet identity, address prefixes, monetary ceiling, and proof-of-work limit.
2. Obtain a trusted build environment where the node executable is permitted to run; test startup, RPC, wallet creation, block generation, coinbase maturity, sends, P2P, reorganizations, restart, and recovery.
3. Finalize unique extended-key prefixes and wallet derivation path/coin type; verify import/export compatibility does not confuse Bitcoin and Carlitos keys.
4. Define independent DNS seed operators and launch a multi-node public testnet.
5. Obtain independent consensus/security audits, especially of PoW attack economics and difficulty adjustment.
6. Publish reproducible binaries, checksums, release notes, and node/wallet operator documentation only after the preceding gates pass.

This is an experimental development branch, not an operating or launched blockchain.
