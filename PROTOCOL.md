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

Subsidy is calculated in integer smallest units only. One CRLTS equals 100,000,000 base units. With the first mined block at height 1, the intended schedule is:

`subsidy(height) = (100 * 100,000,000) >> floor(height / 500,000)`

The implementation must define the height boundary explicitly and include consensus test vectors. Subsidy becomes zero when the right shift exhausts the integer reward. Rounding dust is never minted later to force the theoretical 100,000,000 CRLTS asymptote to be reached. The geometric schedule approaches 100 million CRLTS; integer rounding means actual issuance may be slightly lower.

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

## Network parameters still to be finalized

- Mainnet and testnet message-start bytes (network magic)
- P2P and RPC ports
- Base58 address prefixes and Bech32 human-readable prefix
- DNS seed operators and seed hostnames
- Genesis timestamp and coinbase message
- Proof-of-work limit and exact retarget clamp semantics
- Wallet derivation and descriptor defaults
- Protocol versioning and activation policy for inherited Bitcoin features

These values must be unique, documented, and covered by tests before a public network launch.

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
