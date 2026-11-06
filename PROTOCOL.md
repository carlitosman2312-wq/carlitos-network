# Carlitos Network (CRLTS)

> Independent Bitcoin-style proof-of-work blockchain. This repository currently contains the protocol design baseline, not a runnable or launched cryptocurrency.

## Status

- Phase: protocol specification and repository bootstrap
- Network: Carlitos Network
- Native asset: CRLTS
- Consensus direction: Proof of Work (SHA-256), Bitcoin Core-derived implementation
- Premine: none
- Mainnet: not launched

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

## Monetary issuance

Subsidy is calculated in integer smallest units only. One CRLTS equals 100,000,000 base units. The genesis block is height 0 and has no reward. The first mined block is height 1 and is the first reward-bearing block (issuance index 0). The schedule is:

`subsidy(height) = (100 * 100,000,000) >> floor((height - 1) / 500,000)`

Thus, heights 1 through 500,000 receive 100 CRLTS; heights 500,001 through 1,000,000 receive 50 CRLTS, and so on. The implementation must include consensus test vectors at every halving boundary. Subsidy becomes zero when the right shift exhausts the integer reward. Rounding dust is never minted later to force the theoretical 100,000,000 CRLTS asymptote to be reached. The geometric schedule approaches 100 million CRLTS; integer rounding means actual issuance may be slightly lower.

## Consensus and validation requirements

1. Use Bitcoin-style SHA-256 proof of work and cumulative-chainwork fork choice.
2. Target spacing is 600 seconds.
3. Retarget every 2,016 blocks against a 1,209,600-second target timespan.
4. If adopting Bitcoin's 4x/¼ retarget clamps, document and test exact boundary and off-by-one behavior before activation.
5. Validate block timestamps, median-time-past, future-time bounds, compact target encoding, proof-of-work limit, and difficulty transitions.
6. Validate coinbase subsidy plus fees, transaction inputs/outputs, scripts, and all inherited consensus rules.
7. Use integer arithmetic; never use floating point for monetary values.
8. Define coinbase maturity explicitly (proposed Bitcoin-like default: 100 blocks) and test it.
9. Genesis block has no spendable premine. Its exact timestamp, headline/message, merkle root, nonce, and resulting hash must be generated and verified after network parameters are finalized. Do not invent or pre-fill a genesis hash.

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

The genesis block was computed with zero coinbase value and SHA-256d proof of work. The 0x1e00ffff target is 256 times easier than Bitcoin's historic 0x1d00ffff difficulty-1 target. It is only a provisional bootstrap parameter and provides no guarantee against a 51% attack. Public launch requires independent review and meaningful, distributed hash power.

The inherited testnet, testnet4, signet, and regtest modes are still Bitcoin networks, not Carlitos test networks. Do not use them as public Carlitos networks. Wallet derivation policy and independent seed operators remain to be finalized. The source now includes a separate local -chain=carlitosregtest development network with easy on-demand mining. It is not public and has not yet passed native build or functional tests.

## Security and launch criteria

A new SHA-256 PoW network is vulnerable if its honest hashrate is small or concentrated. ASIC availability does not itself secure a chain: independent miners, diverse operators, monitoring, and a realistic attack-response plan are required. Never advertise the chain as secure or production-ready before independent review and public testing.

Before mainnet:
- Build reproducibly on supported platforms.
- Add unit, functional, consensus, and regression tests.
- Run a public testnet with independent nodes and miners.
- Test difficulty changes, reorgs, invalid blocks, wallet recovery, and backup/restore.
- Obtain independent security and consensus review.
- Publish binaries, checksums, release notes, and operator documentation.

## Development approach

Use a maintained Bitcoin Core codebase as the technical base rather than implementing cryptography, script validation, networking, and wallet logic from scratch. Preserve mature Bitcoin functionality where compatible, and review every inherited feature and activation parameter for Carlitos. Keep changes small, reviewable, and covered by tests.

## Governance

Development is open and community-led. Monetary and consensus rules are enforced independently by nodes. No website, founder, miner, or informal community vote can unilaterally change the rules for nodes that do not adopt such changes. Consensus upgrades require transparent code, review, release notes, and voluntary adoption.

## Disclaimer

CRLTS is a software project in development. This repository does not represent an operating blockchain, an exchange listing, a market price, or an investment offer.
