# Carlitos validation status

Last verified: 2026-11-06 (GitHub Actions)  
Source branch: `integration/bitcoin-core-v32.1`  
Validated commit: `cea5d19206e3b98475d077e8a7361b3c96d0dd1a`  
Upstream baseline: Bitcoin Core v32.1

## Current supported-platform validation

The post-fix Linux CI run supersedes the earlier Windows-only pending results.

| Check | Result |
|---|---|
| Ubuntu 24.04 CMake configure | Passed |
| Native build (node, CLI, wallet, native test binary) | Passed |
| Python reference consensus suite | Passed, 13/13 |
| Targeted native consensus validation test | Passed |
| Local `carlitosregtest` daemon/RPC smoke test | Passed |
| Wallet creation and `rcrl1` address generation | Passed |
| Mining and coinbase maturity | Passed; balance remained 0 at height 100 and matured to 100 CRLTS at height 101 |
| Additional block reward | Passed; second reward matured at height 102 |
| Wallet spend and confirmation | Passed; transaction confirmed at height 103 |
| Full CTest suite | 373 passed, 1 skipped, 0 failed (374 discovered) |
| `descriptor_tests` | Passed |
| `bip324_tests` | Passed |
| `script_assets_tests` | Skipped by CTest (the single skipped test) |

Evidence:
- Native build and CTest workflow: [run #40](https://github.com/carlitosman2312-wq/carlitos-network/actions/runs/42233327155)
- Python reference workflow: [run #34](https://github.com/carlitosman2312-wq/carlitos-network/actions/runs/42233327056)

The CTest log ends with `100% tests passed, 0 tests failed out of 374` and explicitly lists test 311, `script_assets_tests`, as skipped. Therefore the accurate summary is 373 passed, 1 skipped, 0 failed—not 374 executed tests passing.

## Windows host note

The connected Windows PC previously completed a native 601/601-step build with GCC 16.2.0, CMake 4.4.5, and Ninja 1.13.2. However, Windows Application Control blocked launching the newly rebuilt executables on that host. This local policy was not bypassed. The supported Ubuntu CI run now supplies the native execution evidence that the Windows host could not provide.

## Earlier CTest failures and adaptations

The initial Windows full-suite run was a baseline, not the final state. The initial failures prompted chain-aware test updates; the post-fix Linux run now passes the full supported CTest suite, apart from the explicitly skipped script-assets test.

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

## Remaining launch and security blockers

Green CI means the current native prototype builds and passes its present automated checks. It does **not** mean the network is ready for real funds or public launch.

Outstanding work includes:
- Deploying a public Carlitos testnet with independent nodes and seed operators; current testnet bootstrap has no DNS/fixed seeds and requires manual `-addnode`.
- Assigning and documenting a canonical wallet derivation path and BIP44 coin type.
- Reviewing the provisional custom BIP32 extended-key version bytes with wallet implementers and the relevant registry; interoperability is not established.
- Testing multi-node P2P behavior, peer discovery, sustained mining, difficulty transitions, reorganizations, backups, and wallet recovery under realistic conditions.
- Obtaining independent consensus, cryptographic, and security review.
- Reviewing the proposed proof-of-work limit. The current `0x1e00ffff` target is 256 times easier than Bitcoin's historic difficulty-1 target and is not a security guarantee.
- Preparing reproducible release binaries, checksums, operator instructions, monitoring, incident response, and a launch plan only after the above items are addressed.

## Conclusion

The native build, reference tests, local single-node regtest smoke test, and complete CTest suite are green on Ubuntu 24.04. The project remains an experimental Bitcoin Core-derived prototype. No public testnet or mainnet is deployed; do not use real funds or describe CRLTS as launched.
