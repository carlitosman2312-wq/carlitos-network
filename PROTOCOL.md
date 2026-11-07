# Carlitos Network (CRLTS)

> Independent Bitcoin-style proof-of-work blockchain. Ubuntu 24.04 CI has passed the native build, consensus checks, two-node regtest P2P/wallet/mining/spend smoke test, and full CTest suite (373 passed, 1 skipped, 0 failed). Public testnet deployment and launch review remain pending.

## Status

- Phase: native-node prototype with green supported-platform CI; pre-launch engineering and review
- Network: Carlitos Network
- Native asset: CRLTS
- Consensus: SHA-256 Proof of Work with Bitcoin Core-derived chain validation
- Premine: none
- Mainnet: not launched
- Local development chain: carlitosregtest configured; its genesis and parameters pass native unit tests
- Local runtime smoke test: passed on Ubuntu 24.04 CI (two nodes connected; blocks and mempool transaction propagated; wallets, `rcrl` addresses, mining, 100-block maturity, and confirmed spend on `carlitosregtest`)
- Windows host note: Application Control still blocks the rebuilt executables on that PC; the local security policy was not bypassed

## Latest automated validation

The current draft PR head, `1aff7ff030db0f45a044087fa53803849fde5198`, passed GitHub Actions on Ubuntu 24.04: native workflow #57 and reference workflow #51. The native run built node/CLI/wallet/test binaries, verified generated `carlitos.conf`, passed the Python reference suite (13/13), targeted native validation tests (10 Boost cases), BIP94 period-start retarget regression, two-node regtest smoke including timestamp rejection at height 2016, and full CTest (373 passed, 1 skipped, 0 failed of 374 discovered). See `TEST_STATUS.md` for run links and remaining launch blockers.

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
8. Coinbase maturity is the inherited Bitcoin Core default of 100 blocks. The two-node CI smoke test verified an immature balance at height 100, maturity at height 101, and a spend confirmed at height 103 on `carlitosregtest`.
9. The genesis block has no spendable premine. Its timestamp, message, merkle root, nonce, and hash are set in the C++ parameters and checked by native unit tests.
10. The BIP94 timestamp guard is active from genesis on all Carlitos networks: the first block of each 2,016-block difficulty period cannot be timestamped more than 600 seconds behind its predecessor. On public testnet, retarget uses the first block's period difficulty so a minimum-difficulty block at the period end cannot reset the next period's baseline.

## Proposed mainnet identity (not a launch approval)

| Parameter | Proposed value |
|---|---|
| Genesis timestamp | 2026-11-06 00:00:00 UTC (1793923200) |
| Genesis coinbase message | Carlitos Network \| A fair start for everyone. |
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
| BIP32 extended public/private version bytes | 043c524c / 043c5350 (provisional, custom) |
| BIP44 coin type / standard derivation path | Not assigned or registered |
| DNS seeds / fixed seeds | None configured |

The genesis block was computed with zero coinbase value and SHA-256d proof of work. Its hash and parameters pass the Carlitos native unit test. The 0x1e00ffff target is 256 times easier than Bitcoin's historic 0x1d00ffff difficulty-1 target. This is a provisional bootstrap parameter, not evidence of resistance to a 51% attack. Public launch requires independent security review and meaningful, distributed hash power.

The inherited testnet, testnet4, signet, and regtest modes remain Bitcoin networks, not Carlitos networks. Carlitos now has two separate development networks: `-chain=carlitostestnet` is a public-testnet parameter set (P2P 48444, RPC 48446, HRP `tcrl`, separate genesis, normal 10-minute retargeting with minimum-difficulty blocks allowed and BIP94 period-start difficulty anchoring); `-chain=carlitosregtest` remains local instant-mining (P2P 38444, RPC 38446, HRP `rcrl`). The public-testnet parameters have no DNS/fixed seeds yet, so nodes must be connected manually with `-addnode` until independent seed operators are provisioned. `TESTNET_OPERATIONS.md` documents safe private operator testing; no public testnet nodes are deployed or running yet.

Mainnet BIP32 extended-key version bytes are now custom (043c524c public, 043c5350 private), preventing Carlitos mainnet exports from using Bitcoin's standard xpub/xprv version bytes. These custom values are provisional and not registered in SLIP-0132; obtain registry approval before promising compatibility with third-party wallets. No BIP44 coin type or canonical wallet derivation path is assigned yet. SLIP-0044 only adds a coin type when a wallet implementing BIP44 for the coin exists, so a compliant wallet/path plan must precede that registration. Independent DNS seed operators and a public testnet also remain outstanding.

## Security and launch criteria

A new SHA-256 PoW network is vulnerable if its honest hashrate is small or concentrated. ASIC availability does not itself secure a chain: independent miners, diverse operators, monitoring, and a realistic attack-response plan are required. Never advertise the chain as secure or production-ready before independent review and public testing.

Before mainnet:
- Adapt all inherited test vectors to the Carlitos network identity and consensus rules.
- Run a supported-platform native build and the relevant test suite without unresolved failures.
- Two-node local regtest startup, RPC, wallets, block propagation, mempool relay, mining, coinbase maturity, and a confirmed spend are covered by CI. Still test public-testnet peer discovery, sustained mining, difficulty transitions, reorganizations, wallet backup/recovery, and operational monitoring.
- Run a public testnet with independent nodes and miners.
- Obtain independent security and consensus review.
- Publish reproducible binaries, checksums, release notes, and operator documentation.

## Development approach

Use a maintained Bitcoin Core codebase as the technical base rather than implementing cryptography, script validation, networking, and wallet logic from scratch. Preserve mature Bitcoin functionality where compatible, and review every inherited feature and activation parameter for Carlitos. Keep changes small, reviewable, and covered by tests.

## Governance

Development is open and community-led. Monetary and consensus rules are enforced independently by nodes. No website, founder, miner, or informal community vote can unilaterally change the rules for nodes that do not adopt such changes. Consensus upgrades require transparent code, review, release notes, and voluntary adoption.

## Disclaimer

CRLTS is a software project in development. This repository does not represent an operating blockchain, an exchange listing, a market price, or an investment offer.
