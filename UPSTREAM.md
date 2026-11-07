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

The current draft PR head `1aff7ff030db0f45a044087fa53803849fde5198` passed both workflows:
- Native build and consensus workflow #57: https://github.com/carlitosman2312-wq/carlitos-network/actions/runs/42334222080
- Python reference workflow #51 (13/13): https://github.com/carlitosman2312-wq/carlitos-network/actions/runs/42334222101
- Native node, CLI, wallet, and test binary build: passed.
- Generated `carlitos.conf` ports and network sections: passed.
- Targeted native `validation_tests`: 10 Boost cases passed.
- New `pow_tests` BIP94 period-start retarget regression: passed.
- Two-node `carlitosregtest` smoke: P2P, block sync, mempool relay, wallets, maturity, and a confirmed 1 CRLTS spend passed.
- The extended smoke test built a valid-PoW candidate header at height 2016 that passed median-time-past but violated BIP94; the node rejected it with `time-timewarp-attack`.
- Full CTest: 374 discovered, 373 passed, 1 skipped (`script_assets_tests`), 0 failed.

The native workflow includes the generated configuration check, Python reference tests, targeted native tests, the two-node smoke, and the full CTest run. This validates the present native prototype on Ubuntu 24.04. It does not validate a deployed public testnet, real-world mining security, third-party wallet interoperability, or readiness for real funds.

The BIP94 changes do not alter genesis hashes, subsidy, halving, proof-of-work limit, or block reward schedule. They do change timestamp and retarget consensus behavior from genesis.

The connected Windows PC built all 601 native build steps but Windows Application Control blocked launching the rebuilt executables. That local policy was not bypassed; Ubuntu CI provides the runtime evidence.

## Remaining engineering work before public use

1. Deploy several independently operated Carlitos public-testnet nodes and seed operators; current peer discovery is manual via `-addnode`.
2. Exercise sustained public-testnet mining, difficulty transitions, reorgs, peer discovery, wallet backup/recovery, restart, and recovery with independent operators.
3. Replace the inherited Bitcoin descriptor derivation paths before real-fund wallets: current mainnet paths use coin type `0'`, test-chain paths use `1'`, and purposes `44'`, `49'`, `84'`, and `86'`. Agree on a CRLTS-specific BIP44 path, add chain-aware wallet tests, then request a SLIP-0044 coin type once the wallet implementing BIP44 is ready. The custom BIP32 bytes (043c524c / 043c5350 mainnet) remain provisional and need SLIP-0132 review/registration.
4. Provision DNS/fixed seed infrastructure, a faucet, block explorer, monitoring, and public operator documentation after seed operators and wallet standards are in place.
5. Obtain independent consensus, cryptographic, and security review, including PoW attack economics and difficulty adjustment.
6. Establish a verified private vulnerability-disclosure route and incident response, then publish reproducible binaries, checksums, and release instructions only after the preceding gates pass.

This is an experimental development branch, not an operating or launched blockchain.
