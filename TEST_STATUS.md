# Carlitos validation status

Last verified: 2026-11-07 (GitHub Actions)  
Source branch: `integration/bitcoin-core-v32.1`  
Validated commit: `95d6ff2f72c821c12f0f7a5e5c316828f1db60cf`  
Upstream baseline: Bitcoin Core v32.1

## Current supported-platform validation

The current PR head passed both GitHub Actions workflows on Ubuntu 24.04:

- Native build and consensus workflow: [run #46](https://github.com/carlitosman2312-wq/carlitos-network/actions/runs/42322325345)
- Python reference workflow: [run #40](https://github.com/carlitosman2312-wq/carlitos-network/actions/runs/42322325313)

| Check | Result |
|---|---|
| Ubuntu 24.04 CMake configure | Passed |
| Native node, CLI, wallet, and native test binary build | Passed |
| Python reference consensus suite | Passed, 13/13 |
| Targeted native `validation_tests` | Passed; 10 Boost test cases, no errors |
| Carlitos mainnet/testnet/regtest validation and genesis checks | Passed within native validation tests |
| Default data root and network-specific data-directory isolation | Passed within native validation tests |
| Two-node `carlitosregtest` P2P smoke test | Passed; node B connected to node A |
| Block synchronization | Passed; node B followed node A through blocks 100–103 |
| Mempool transaction relay | Passed; receiver node observed the transaction before mining |
| Wallet creation and `rcrl1` address generation | Passed on both nodes |
| Coinbase maturity | Passed; balance was 0 at height 100, 100 CRLTS at height 101, and 200 CRLTS at height 102 |
| Confirmed wallet spend | Passed; 1.0 CRLTS spend confirmed at height 103 and credited to receiver wallet |
| Full CTest suite | 374 discovered; 373 passed, 1 skipped, 0 failed |
| `descriptor_tests` | Passed |
| `bip324_tests` | Passed |
| `script_assets_tests` | Skipped by CTest (the single skipped test) |

The native CI log explicitly reports:

`PASS: two Carlitos regtest nodes connected; blocks and mempool transaction propagated; wallets, rcrl addresses, 100-block maturity, mining, and confirmed spend verified`

The CTest log ends with `100% tests passed, 0 tests failed out of 374` and explicitly lists test 311, `script_assets_tests`, as skipped. The accurate summary is therefore 373 passed, 1 skipped, 0 failed—not 374 executed tests passing.

## Windows host note

The connected Windows PC previously completed a native 601/601-step build with GCC 16.2.0, CMake 4.4.5, and Ninja 1.13.2. However, Windows Application Control blocked launching the newly rebuilt executables on that host. This local policy was not bypassed. Ubuntu CI supplies the current supported-platform build and runtime execution evidence.

## Earlier CTest failures and adaptations

The initial Windows full-suite run was a baseline, not the final state. The initial failures prompted chain-aware test updates; the current post-fix Linux run passes the full supported CTest suite apart from the explicitly skipped script-assets test.

The adaptations include:
- Re-encoding mainnet Base58/WIF and Bech32 vectors for Carlitos address prefixes while preserving key/hash payloads.
- Re-encoding Taproot address vectors for the Carlitos Bech32 HRP.
- Re-encoding WIF fixtures in key, bloom, and descriptor tests while preserving private-key bytes.
- Updating RPC and utility fixtures to Carlitos P2PKH/P2SH/WIF prefixes.
- Running inherited fixed pre-mined block fixtures against isolated Bitcoin regtest parameters where the Carlitos coinbase subsidy changes the transaction ID and Merkle root.
- Updating invalid-transaction fixtures to test the Carlitos 100,000,000 CRLTS money limit.
- Making peer-port assertions use the selected chain's configured port.
- Running historical proof-of-work retarget vectors against an isolated Bitcoin testnet parameter copy.
- Avoiding unsigned underflow in the zero-minimum-chainwork fixture.
- Adding and validating distinct Carlitos mainnet, public-testnet, and local-regtest extended-key serialization prefixes.
- Testing that Carlitos uses its own default data root and separate data-directory children for its public-testnet and regtest chains.

## Remaining launch and security blockers

Green CI means the current native prototype builds and passes its present automated checks. It does **not** mean the network is ready for real funds or public launch.

Outstanding work includes:
- Deploying a public Carlitos testnet with independent nodes and seed operators; current testnet bootstrap has no DNS/fixed seeds and requires manual `-addnode`.
- Assigning and documenting a canonical wallet derivation path and BIP44 coin type.
- Reviewing the provisional custom BIP32 extended-key version bytes with wallet implementers and the relevant registry; interoperability is not established.
- Testing public-testnet peer discovery, sustained multi-operator mining, difficulty transitions, reorganizations, backups, and wallet recovery under realistic conditions. Local two-node regtest P2P and transaction relay now pass.
- Obtaining independent consensus, cryptographic, and security review.
- Reviewing the proposed proof-of-work limit. The current `0x1e00ffff` target is 256 times easier than Bitcoin's historic difficulty-1 target and is not a security guarantee.
- Preparing reproducible release binaries, checksums, operator instructions, monitoring, incident response, and a launch plan only after the above items are addressed.

## Conclusion

The native build, Python reference tests, targeted native validation, two-node local regtest P2P/wallet/mining/maturity/spend smoke test, and full CTest suite are green on Ubuntu 24.04 for the validated commit. The project remains an experimental Bitcoin Core-derived prototype. No public testnet or mainnet is deployed; do not use real funds or describe CRLTS as launched.
