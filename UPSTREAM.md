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
- src/util/chaintype.*, src/chainparams.*, src/kernel/chainparams.*, src/bitcoin-cli.cpp, src/qt/guiutil.cpp: dedicated carlitostestnet (public testnet parameters) and carlitosregtest (local instant-mining) chain types, isolated from Bitcoin's networks.
- src/kernel/chainparams.cpp: custom BIP32 extended-key serialization versions for Carlitos mainnet, public testnet, and regtest; all are distinct from Bitcoin's xpub/xprv versions.
- .github/workflows/ci.yml: the original large Bitcoin Core cross-platform CI matrix is preserved at contrib/upstream/bitcoin-core-ci.yml, outside GitHub's active workflow directory, so the fork runs its focused Carlitos validation workflows instead.
- src/common/args.cpp, src/init.cpp, src/clientversion.cpp, CMakeLists.txt: Carlitos client identity, configuration name, PID file, and separate default data directory.
- src/test/validation_tests.cpp: reward boundary, total issuance, mainnet parameter/genesis, and development-network tests.
- .github/workflows/native-build.yml: Linux CI build and targeted native consensus smoke suite.

## Automated validation status (Ubuntu 24.04)

The last fully validated consensus implementation is commit `95d6ff2f72c821c12f0f7a5e5c316828f1db60cf`:
- Native build workflow #46 passed: https://github.com/carlitosman2312-wq/carlitos-network/actions/runs/42322325345
- Python reference workflow #40 passed (13/13): https://github.com/carlitosman2312-wq/carlitos-network/actions/runs/42322325313
- Targeted native `validation_tests`: 10 Boost cases passed.
- Two-node `carlitosregtest` smoke: P2P connected, blocks and mempool transaction propagated, wallets/address generation worked, 100-block coinbase maturity verified, and a 1 CRLTS spend confirmed.
- Full CTest: 374 discovered, 373 passed, 1 skipped (`script_assets_tests`), 0 failed.

Follow-up commits in draft PR #2 add Carlitos testnet/regtest config-section recognition, generated `carlitos.conf`, CLI help/port coverage, and BIP94 timewarp/retarget hardening. Those follow-ups require a fresh native CI pass before being considered validated. The BIP94 changes do not alter genesis hashes, subsidy, halving, proof-of-work limit, or block reward schedule.

The connected Windows PC built all 601 native build steps but Windows Application Control blocked launching the rebuilt executables. This local policy was not bypassed; Ubuntu CI provides the runtime execution evidence above.

## Remaining engineering work before public use

1. Keep the latest config/generator/BIP94 follow-up commits under native Linux CI, including the new BIP94 retarget regression case and full CTest suite.
2. Obtain a trusted build environment where the node executable is permitted to run; test startup, RPC, wallet creation, block generation, coinbase maturity, sends, P2P, reorganizations, restart, and recovery.
3. Mainnet BIP32 extended-key bytes are now distinct (043c524c / 043c5350) and their vectors were migrated, but those custom bytes are provisional and need SLIP-0132 registration. Design a compatible wallet derivation scheme, implement a BIP44-capable wallet path if desired, then request a SLIP-0044 coin type; verify imports cannot confuse Bitcoin and Carlitos keys.
4. Deploy multiple independent `carlitostestnet` nodes, register DNS seed operators, and validate cross-operator mining, retargeting, reorgs, and wallet interoperability.
5. Obtain independent consensus/security audits, especially of PoW attack economics and difficulty adjustment.
6. Publish reproducible binaries, checksums, release notes, and node/wallet operator documentation only after the preceding gates pass.

This is an experimental development branch, not an operating or launched blockchain.
