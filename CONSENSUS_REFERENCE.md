# Consensus reference model

## Purpose and status

This is an executable, testable reference for two parts of the proposed Carlitos rules:

- block subsidy and the 500,000-reward-block halving schedule;
- Bitcoin-mainnet-style SHA-256 proof-of-work target adjustment.

It is deliberately separate from Bitcoin Core's C++ implementation. It is not a node, miner, wallet, P2P protocol, or production consensus implementation. The Python model must not be used to validate real blocks.

## Exact schedule

Block height 0 is the genesis block and has a subsidy of zero. Height 1 is the first reward-bearing block. Heights 1–500,000 pay 100 CRLTS; heights 500,001–1,000,000 pay 50 CRLTS, and so on.

All amounts are integer base units. One CRLTS is 100,000,000 base units. The subsidy right-shifts by one bit at each halving boundary, discarding fractional base units. There is no premine and no later issuance of rounding dust.

## Difficulty model

- Target spacing: 600 seconds.
- Target timespan: 1,209,600 seconds.
- Adjustment interval: 2,016 blocks.
- Retarget occurs for the next block when its height is divisible by 2,016.
- The retarget window's first timestamp is the timestamp of the ancestor at `last_height - (interval - 1)`, matching Bitcoin Core's retarget-window convention.
- Actual timespan is clamped to between one quarter and four times the target timespan.
- New target is `old_target * clamped_actual_timespan // target_timespan`, capped at the proof-of-work limit.
- There is no minimum-difficulty exception and no no-retarget mode in the proposed mainnet model.
- Compact `nBits` encoding is used; negative, zero, overflowing, and above-limit targets must be rejected during block validation.

This reference uses the Bitcoin mainnet proof-of-work limit and initial `nBits` as provisional starting parameters, not as final Carlitos network identifiers. The target and retarget approach are based on Bitcoin Core v32.1's `src/kernel/chainparams.cpp`, `src/consensus/params.h`, and `src/pow.cpp`. Review these upstream sources directly before porting behavior.

## Tests

Run locally:

```sh
python -m unittest discover -s tests -v
```

The tests cover genesis issuance, halving boundaries, compact-target conversion and error flags, retarget boundaries, timespan clamping, and proof-of-work-limit capping.

## Next integration step

Port these chosen parameters into a pinned Bitcoin Core source baseline and add C++ consensus tests plus functional regtest tests. The Python tests are a specification aid; passing them does not prove the C++ node is correct or secure.
