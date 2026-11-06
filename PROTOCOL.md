# Carlitos Network (CRLTS)

> Independent Bitcoin-style proof-of-work blockchain. The native node source compiles and targeted consensus unit tests pass; runtime validation and public launch remain pending.

## Status

- Phase: native-node prototype and consensus unit tests
- Network: Carlitos Network
- Native asset: CRLTS
- Consensus: SHA-256 Proof of Work with Bitcoin Core-derived chain validation
- Premine: none
- Mainnet: not launched
- Local development chain: carlitosregtest configured; its genesis and parameters pass native unit tests
- Runtime node test: blocked on the connected Windows PC by Application Control

## Initial protocol parameters

| Parameter | Value |
|---|---:|
| Target block interval | 600 seconds (10 minutes) |
| Difficulty adjustment interval | 2,016 blocks |
| Target timespan | 1,209,600 seconds (14 days) |
| Initial block subsidy | 100 CRLTS |
| Halving interval | 500,000 blocks |
| Accounting precision | 8 decimal places |
| Smallest unit | 0.00000001 CRLTS |
| Subsidy at genesis | 0 CRLTS |
| Premine | 0 CRLTS |
| Transaction fees | Paid to the block miner |
| Coinbase maturity | 100 blocks (inherited Bitcoin Core rule) |

## Monetary issuance

Subsidy is calculated in integer smallest units only. One CRLTS equals 100,000,000 base units. The genesis block is height 0 and has no reward. The first mined block is height 1 and is the first reward-bearing block (issuance index 0). The schedule is:

subsidy(height) = (100 * 100,000,000) >> floor((height - 1) / 500,000)

Thus, heights 1 through 500,000 receive 100 CRLTS; heights 500,001 through 1,000,000 receive 50 CRLTS, and so on. Subsidy becomes zero when the right shift exhausts the integer reward. Rounding dust is never minted later to force the theoretical 100,000,000 CRLTS asymptote to be reached. The integer schedule issues 99,999,999.945 CRLTS in total. The native test for this total passes.

## Consensus and validation rules

1. Use Bitcoin-style SHA-256 proof of work and cumulative-chainwork fork choice.
2. Target spacing is 600 seconds.
3. Retarget every 2,016 blocks against a 1,209,600-second target timespan.
4. The implementation inherits Bitcoin Core's four-times/one-quarter actual-timespan clamp and integer target calculation.
5. Validate block timestamps, median-time-past, future-time bounds, compact target encoding, proof-of-work limit, and difficulty transitions.
6. Validate coinbase subsidy plus fees, transaction inputs/outputs, scripts, and inherited consensus rules.
7. Use integer arithmetic; never use floating point for monetary values.
8. Coinbase maturity is the inherited Bitcoin Core default of 100 blocks. End-to-end wallet maturity testing remains pending.
9. The genesis block has no spendable premine. Its timestamp, message, merkle root, nonce, and hash are set in the C++ parameters and checked by native unit tests.

## Proposed mainnet identity (not a launch approval)

| Parameter | Proposed value |
|---|---|
| Genesis timestamp | 2026-11-06 00:00:00 UTC (1793923200) |
| Genesis coinbase message | Carlitos Network - A fair start for everyone. |
| Genesis subsidy | 0 CRLTS |
| Genesis nBits | 0x1e00ffff |
| Genesis nonce | 5,677,157 |
| Genesis merkle root | 6fb2576a8861ef3c2b3abcbaccbf4b33e9f0999cb1203cca7f20419feea1eaf0 |
| Genesis block hash | 00000045c5a492bcf1dc4adaa826bc5d4cdfcc435b822692c92860834a9d94e5 |
| Proof-of-work limit | 000000ffff000000000000000000000000000000000000000000000000000000 |
| Mainnet message-start bytes | c3 4c 54 53 |
| Mainnet P2P port | 28444 |
| Mainnet RPC port | 28446 |
| P2PKH / P2SH / WIF prefixes | 28 / 50 / 156 |
| Bech32 HRP | crl |
| DNS seeds / fixed seeds | None configured |

The genesis block was computed with zero coinbase value and SHA-256d proof of work. Its hash and parameters pass the Carlitos native unit test. The 0x1e00ffff target is 256 times easier than Bitcoin's historic 0x1d00ffff difficulty-1 target. This is a provisional bootstrap parameter, not evidence of resistance to a 51% attack. Public launch requires independent security review and meaningful, distributed hash power.

The inherited testnet, testnet4, signet, and regtest modes remain Bitcoin networks, not Carlitos networks. Do not use them as public Carlitos testnets. A separate local -chain=carlitosregtest network is included with easy on-demand mining and its own identity; its C++ parameter/genesis unit test passes. Actual daemon startup, RPC, P2P, and mined-block testing remain pending.

Wallet extended-key prefixes and derivation path/coin type still need finalization. Independent DNS seed operators and a public testnet also remain outstanding.

## Security and launch criteria

A new SHA-256 PoW network is vulnerable if its honest hashrate is small or concentrated. ASIC availability does not itself secure a chain: independent miners, diverse operators, monitoring, and a realistic attack-response plan are required. Never advertise the chain as secure or production-ready before independent review and public testing.

Before mainnet:
- Adapt all inherited test vectors to the Carlitos network identity and consensus rules.
- Run a supported-platform native build and the relevant test suite without unresolved failures.
- Test node startup, RPC, wallet creation/recovery, block generation, coinbase maturity, sends, P2P, difficulty transitions, and reorganizations.
- Run a public testnet with independent nodes and miners.
- Obtain independent security and consensus review.
- Publish reproducible binaries, checksums, release notes, and operator documentation.

## Development approach

Use a maintained Bitcoin Core codebase as the technical base rather than implementing cryptography, script validation, networking, and wallet logic from scratch. Preserve mature Bitcoin functionality where compatible, and review every inherited feature and activation parameter for Carlitos. Keep changes small, reviewable, and covered by tests.

## Governance

Development is open and community-led. Monetary and consensus rules are enforced independently by nodes. No website, founder, miner, or informal community vote can unilaterally change the rules for nodes that do not adopt such changes. Consensus upgrades require transparent code, review, release notes, and voluntary adoption.

## Disclaimer

CRLTS is a software project in development. This repository does not represent an operating blockchain, an exchange listing, a market price, or an investment offer.
