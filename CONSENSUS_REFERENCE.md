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

The mainnet proof-of-work limit is compact target 0x1e00ffff. This is 256 times easier than Bitcoin's historic 0x1d00ffff difficulty-1 target. It is only a provisional bootstrap value and does not make the network secure against a 51% attack. Independent hash-rate analysis and review are mandatory before public launch.

The reference model follows the non-min-difficulty mainnet path in Bitcoin Core v32.1, primarily src/pow.cpp and src/consensus/params.h. The C++ node implementation is authoritative once compiled and validated.

## Run reference tests

    python -m unittest discover -s tests -v

These tests cover issuance boundaries, integer rounding, compact target encoding, retarget boundaries, timespan clamps, and proof-of-work limit handling. Passing them does not prove the C++ node is correct.

## Current engineering boundary

The Bitcoin Core v32.1 source tree has been imported and the native C++ node build completed successfully (601/601 steps). The native validation_tests suite passes 8/8, including Carlitos mainnet/devnet genesis and total issuance. The separate Python reference suite passes 13/13. The initial full upstream CTest baseline passed 95% with 14 failures and one skipped test; subsequent source-level adaptations update Bitcoin-specific address/WIF, money, RPC, miner, PoW, and chainstate fixtures, and the updated native test binary compiles. A complete post-fix rerun is pending Linux CI; BIP324 crypto-vector failures still need supported-platform reproduction. Daemon startup, RPC, wallet, P2P, mining smoke tests, public testnet, and external audit remain pending.
