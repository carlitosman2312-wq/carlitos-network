# Bitcoin Core upstream baseline

## Selected source baseline

- Upstream repository: https://github.com/bitcoin/bitcoin
- Selected tag: `v32.1`
- Release reference: https://github.com/bitcoin/bitcoin/releases/tag/v32.1
- Official release page: https://bitcoincore.org/en/releases/

As checked on 2026-11-06, the GitHub releases page identifies Bitcoin Core 32.1 as the latest release. The release page reports a verified signed tag. Before importing or building the source, verify the published release signatures and deterministic release checksums using Bitcoin Core's official release instructions.

## Upstream files reviewed

The following files at tag `v32.1` were reviewed as references for the parameter mapping:

- `src/kernel/chainparams.cpp` — chain-specific genesis block, proof-of-work limit, target spacing/timespan, halving interval, network magic, ports, address prefixes, and seed configuration.
- `src/consensus/params.h` — consensus parameter structure and difficulty adjustment interval calculation.
- `src/pow.cpp` — next-work-required logic, timespan clamps, compact target handling, and proof-of-work target validation.

The Carlitos Python reference model follows the non-min-difficulty mainnet retarget path as a starting point. It does not copy or replace these C++ files.

## Import/integration status

**Not yet imported.** This repository does not currently contain the Bitcoin Core source tree, and no C++ consensus files have been patched. The Python model is a testable protocol reference only.

The next implementation phase should:

1. Import a verified copy of the selected upstream source into a dedicated branch or a true fork.
2. Preserve upstream history and license notices.
3. Change only Carlitos-specific parameters first, in particular chain parameters and subsidy interval.
4. Add C++ unit tests that assert the exact reward-height boundaries and difficulty-retarget boundaries.
5. Add regtest/functional tests for genesis, mining, invalid proof of work, chainwork selection, reorgs, and wallet behavior.
6. Build from a clean environment and keep the upstream diff reviewable.

Do not use the Python reference tests as a substitute for Bitcoin Core's C++ or functional test suites.
