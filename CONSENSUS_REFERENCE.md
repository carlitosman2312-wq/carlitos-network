# Consensus reference model

## Purpose and status

This is an executable reference for the Carlitos issuance schedule and Bitcoin-style SHA-256 proof-of-work target adjustment. It is separate from the C++ node implementation and must not be used to validate production blocks.

## Issuance

- Genesis height 0 has zero subsidy and no spendable premine.
- The first reward-bearing block is height 1.
- Heights 1 through 500,000 pay 100 CRLTS.
- Heights 500,001 through 1,000,000 pay 50 CRLTS, and so on.
- One CRLTS equals 100,000,000 base units. All calculations use integer arithmetic.
- Fractional base units are discarded at each right shift and never issued later.
- The complete geometric schedule produces 99,999,999.945 CRLTS because of integer rounding.

## Difficulty

- Target block spacing: 600 seconds.
- Target timespan: 1,209,600 seconds.
- Adjustment interval: 2,016 blocks.
- The next block is retargeted when its height is divisible by 2,016.
- The retarget window uses the ancestor at last_height minus (interval minus 1), matching Bitcoin Core.
- Actual timespan is clamped to one quarter through four times the target timespan.
- The new target is old_target times clamped_actual_timespan divided by target_timespan, rounded down and capped by the Carlitos proof-of-work limit.
- No minimum-difficulty exception is enabled on the proposed mainnet.
- BIP94 timewarp protection is enabled from genesis on all Carlitos networks. The first block in each difficulty period cannot be timestamped more than 600 seconds earlier than its predecessor.
- Public testnet permits minimum-difficulty blocks after idle periods, but retargets use the first block's difficulty for the period, not a late min-difficulty block.

The mainnet proof-of-work limit is compact target 0x1e00ffff. This is 256 times easier than Bitcoin's historic 0x1d00ffff difficulty-1 target. It is only a provisional bootstrap value and does not make the network secure against a 51% attack. Independent hash-rate analysis and review are mandatory before public launch.

The reference model follows the non-min-difficulty mainnet path in Bitcoin Core v32.1, primarily src/pow.cpp and src/consensus/params.h. The C++ node implementation is authoritative once compiled and validated.

## Run reference tests

    python -m unittest discover -s tests -v

These tests cover issuance boundaries, integer rounding, compact target encoding, retarget boundaries, timespan clamps, and proof-of-work limit handling. Passing them does not prove the C++ node is correct.

## Current engineering boundary

The Bitcoin Core v32.1 source tree has been imported. Current PR head `1aff7ff030db0f45a044087fa53803849fde5198` passed native workflow #57 and Python reference workflow #51 on Ubuntu 24.04. The native workflow built node/CLI/wallet/test binaries, checked the generated config example, passed 10 targeted native validation Boost cases and 13/13 Python reference tests, passed the BIP94 period-start difficulty regression, and completed the two-node regtest smoke including a valid-PoW header rejection at height 2016 with `time-timewarp-attack`. Full CTest reported 100% passed, 0 failed of 374 discovered (373 passed, 1 skipped: `script_assets_tests`). Public testnet deployment, independent seed operators, wallet derivation/coin-type decisions, registry review of extended-key versions, and independent security review remain outstanding.
