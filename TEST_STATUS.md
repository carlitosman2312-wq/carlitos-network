# Carlitos validation status

Last verified: 2026-11-07 (GitHub Actions)  
Source branch: `integration/bitcoin-core-v32.1`  
Validated PR head: `1aff7ff030db0f45a044087fa53803849fde5198`  
Upstream baseline: Bitcoin Core v32.1

## Current supported-platform validation

Both workflows passed on the same PR head on Ubuntu 24.04:

- Native build and consensus workflow #57: https://github.com/carlitosman2312-wq/carlitos-network/actions/runs/42334222080
- Python reference workflow #51: https://github.com/carlitosman2312-wq/carlitos-network/actions/runs/42334222101

| Check | Result |
|---|---|
| Ubuntu 24.04 CMake configure | Passed |
| Native node, CLI, wallet, and native test binary build | Passed |
| Generated `carlitos.conf` verification | Passed; generated P2P/RPC ports and Carlitos network sections verified |
| Python reference consensus suite | Passed, 13/13 |
| Targeted native `validation_tests` | Passed; 10 Boost test cases |
| Carlitos chain parameter and genesis checks | Passed |
| Default data root and network-specific data-directory isolation | Passed |
| Native BIP94 retarget regression in `pow_tests` | Passed; confirms period-start difficulty is used on Carlitos testnet |
| Two-node `carlitosregtest` P2P smoke | Passed; node B connected to node A |
| Block synchronization and mempool relay | Passed; blocks and the spend transaction propagated |
| Wallets and `rcrl1` address generation | Passed on both nodes |
| Coinbase maturity | Passed; 0 CRLTS at height 100, 100 CRLTS at height 101, 200 CRLTS at height 102 |
| Confirmed wallet spend | Passed; a 1 CRLTS spend confirmed at height 103 and credited to the receiver |
| BIP94 timestamp rejection | Passed; smoke test prepared a valid-PoW header for height 2016 whose timestamp passed median-time-past but violated the 600-second BIP94 timewarp rule; node rejected it with `time-timewarp-attack` |
| Full CTest suite | 374 discovered; 373 passed, 1 skipped, 0 failed |

The native workflow log explicitly reports:

`PASS: two Carlitos regtest nodes connected; blocks and mempool transaction propagated; wallets, rcrl addresses, 100-block maturity, mining, confirmed spend, and BIP94 timestamp rejection verified`

CTest reports `100% tests passed, 0 tests failed out of 374`; test 311, `script_assets_tests`, was skipped. The accurate result is 373 passed, 1 skipped, 0 failed—not 374 executed tests passing.

## What this validation establishes

The current code can be configured, compiled, and run on Ubuntu 24.04. The generated configuration example, reference consensus calculations, native chain validation, BIP94 retarget behavior, local two-node P2P, wallet/maturity/spend path, and BIP94 timestamp rejection all passed their automated checks.

The BIP94 changes alter timestamp/retarget consensus behavior from genesis. They do not alter the Carlitos genesis hashes, initial subsidy, halving interval, proof-of-work limit, or block reward schedule.

These are prototype and regtest results. They do not establish public-testnet liveness, real-world mining security, wallet interoperability, resistance to attacks, or readiness for real funds.

## Windows host note

The connected Windows PC previously completed a native 601/601-step build with GCC 16.2.0, CMake 4.4.5, and Ninja 1.13.2. Windows Application Control blocked launching the rebuilt executables on that host. The local policy was not bypassed. The Ubuntu Actions workflow supplies supported-platform runtime evidence.

## Test adaptations

The inherited Bitcoin tests were adapted for Carlitos network identity and consensus:
- Mainnet Base58/WIF and Bech32 vectors use Carlitos prefixes/HRP while preserving key/hash payloads.
- Taproot address vectors and descriptor fixtures use Carlitos Bech32 HRP and extended-key serialization versions.
- Wallet, key, bloom, descriptor, RPC, and utility fixtures use the matching Carlitos address and WIF prefixes.
- Inherited fixed pre-mined fixtures run against isolated Bitcoin regtest parameters where Carlitos subsidy changes coinbase transaction IDs and Merkle roots.
- Invalid-transaction fixtures exercise the Carlitos 100,000,000 CRLTS money limit.
- Peer-port checks use the selected chain's configured P2P port.
- Historical proof-of-work vectors use isolated Bitcoin testnet parameters.
- Zero-minimum-chainwork fixtures avoid unsigned underflow.
- Carlitos mainnet, public-testnet, and regtest extended-key serialization prefixes are tested.
- Carlitos mainnet data root and public-testnet/regtest data-directory isolation are tested.
- A native retarget regression tests BIP94's period-start anchor on public testnet.
- The two-node smoke exercises a height-2016 BIP94 timewarp rejection with a proof-of-work-valid header.

## Remaining launch and security blockers

Green CI does **not** mean the network is ready for public launch or real funds. Outstanding work includes:
- No Carlitos mainnet or public-testnet nodes are deployed. There are no DNS/fixed seeds or independent seed operators; testnet peers must currently be connected manually with `-addnode`.
- No independent miner/operator set, block explorer, monitoring, public faucet, or sustained public-testnet history exists.
- The current descriptor-wallet generator still uses Bitcoin BIP44 coin types: `0'` on mainnet and `1'` on test chains, with purposes `44'`, `49'`, `84'`, and `86'`. Carlitos therefore does not yet have an isolated derivation namespace; reusing a seed across Bitcoin and Carlitos can derive the same child keys. A CRLTS-specific path and SLIP-0044 coin type must be selected and implemented before real-fund wallets are used. BIP44's published registration guidance requires an implementing wallet.
- The custom BIP32 extended-key versions are provisional and not registered in SLIP-0132. Do not promise third-party wallet compatibility.
- SECURITY.md explains the fork-specific disclosure policy, but a verified private vulnerability-reporting channel has not been established.
- Independent consensus, cryptographic, PoW-economics, and security review remains outstanding.
- The proposed `0x1e00ffff` PoW target is 256 times easier than Bitcoin's historic difficulty-1 target. It is a provisional parameter, not a security guarantee.
- Public-testnet peer discovery, sustained multi-operator mining, difficulty transitions, reorganizations, wallet backup/recovery, and restart/recovery still need real network exercise.
- Reproducible release binaries, checksums, release notes, incident response, and launch operations are not yet complete.

The manual operator guide is in `TESTNET_OPERATIONS.md`; it is for coordinated private testing only, not evidence of a deployed public testnet.

## Conclusion

Native build, generated config, Python reference tests, targeted native consensus checks, BIP94 retarget and timestamp-rejection checks, two-node local regtest P2P/wallet/mining/maturity/spend, and full CTest all passed on PR head `1aff7ff030db0f45a044087fa53803849fde5198`. The project remains an experimental Bitcoin Core-derived prototype. No public testnet or mainnet is deployed. Do not use real funds or describe CRLTS as launched.
