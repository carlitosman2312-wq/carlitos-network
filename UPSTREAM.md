# Bitcoin Core upstream baseline

## Selected source baseline

- Upstream: https://github.com/bitcoin/bitcoin
- Tag: v32.1
- Commit: f0de87f040621468b956f01f526a43a010310501
- Release: https://github.com/bitcoin/bitcoin/releases/tag/v32.1

The full v32.1 source tree was fetched from the official upstream repository and merged into the integration/bitcoin-core-v32.1 branch. The upstream commit remains in the Git history as a merge parent, and upstream COPYING/license notices are retained.

## Carlitos changes made in this branch

- src/kernel/chainparams.cpp: Carlitos mainnet genesis, PoW limit, 600-second spacing, 1,209,600-second target timespan, P2P port, network magic, address prefixes, Bech32 HRP, empty seed lists, and removal of Bitcoin-specific assume-valid, assume-UTXO, and header-sync assumptions.
- src/chainparamsbase.cpp: separate Carlitos mainnet RPC port.
- src/consensus/params.h: configurable initial subsidy and first reward height with Bitcoin-compatible defaults for inherited chain types.
- src/consensus/amount.h: MAX_MONEY increased to the 100,000,000 CRLTS protocol ceiling.
- src/validation.cpp: subsidy calculation in integer base units.
- src/test/validation_tests.cpp: subsidy boundary, full issuance, chain parameters, and genesis hash tests.
- src/pow.cpp: retained upstream retarget implementation; Carlitos supplies target spacing and timespan through consensus parameters.

## Validation status

The Python reference suite passes 13 tests on the connected Windows PC. The C++ source has not yet been compiled or executed through Bitcoin Core's native tests.

The inherited testnet, testnet4, signet, and regtest chain modes remain upstream Bitcoin networks and are not Carlitos testnets. A separate carlitosregtest chain type has now been added with its own message magic, ports, address prefixes, genesis, and easy on-demand mining parameters. It is intended only for local development; it has not yet been compiled or exercised in the native functional suite.

## Before any public launch

1. Build from a clean environment and run the complete native unit and functional suites.
2. Add a separate Carlitos dev/regtest network for mining, wallets, P2P, transactions, reorganizations, and recovery testing.
3. Verify all network identifiers, address encodings, RPC ports, genesis values, and protocol activations.
4. Run multi-node public testnet with independent operators.
5. Obtain independent consensus and security audits, especially of PoW security and issuance.
6. Only then consider mainnet binaries and public mining instructions.

This is an experimental development branch, not an operating or launched blockchain.
