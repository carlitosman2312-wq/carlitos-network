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
- Initial full CTest baseline (before fork-specific fixture adaptations): 95% passed, 14 failures, 1 skipped. Since that baseline, source fixtures for Carlitos address/WIF prefixes, money ceiling, RPC addresses, miner/regtest, PoW retarget vectors, transaction invalid cases, and zero minimum-chainwork have been updated and the native test binary recompiles. The full post-fix suite has not yet been rerun because Windows Application Control blocks the rebuilt test executable; Linux CI is pending. BIP324 cryptographic vector failures still require supported-platform reproduction. See TEST_STATUS.md.
- Launching the daemon was blocked by Windows Application Control. No policy bypass was attempted, so RPC, wallet operations, P2P, and mined blocks have not been smoke-tested.
- The integration branch and commits are pushed to GitHub. Draft PR #2 is open but not merged; the latest Linux Actions runs are queued, so their results are not yet available.

## Remaining engineering work before public use

1. Run the adapted full C++ suite on Linux CI, verify the chain-aware test fixture changes, and fix any remaining failures (notably the BIP324 crypto-vector suite if reproducible).
2. Obtain a trusted build environment where the node executable is permitted to run; test startup, RPC, wallet creation, block generation, coinbase maturity, sends, P2P, reorganizations, restart, and recovery.
3. Mainnet BIP32 extended-key bytes are now distinct (043c524c / 043c5350) and their vectors were migrated, but those custom bytes are provisional and need SLIP-0132 registration. Design a compatible wallet derivation scheme, implement a BIP44-capable wallet path if desired, then request a SLIP-0044 coin type; verify imports cannot confuse Bitcoin and Carlitos keys.
4. Define independent DNS seed operators and launch a multi-node public testnet.
5. Obtain independent consensus/security audits, especially of PoW attack economics and difficulty adjustment.
6. Publish reproducible binaries, checksums, release notes, and node/wallet operator documentation only after the preceding gates pass.

This is an experimental development branch, not an operating or launched blockchain.
