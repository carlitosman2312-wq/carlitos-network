# Carlitos validation status

Run date: 2026-11-06  
Source branch: integration/bitcoin-core-v32.1  
Upstream baseline: Bitcoin Core v32.1

## Build environment

- Windows PC connected through the user's authorized remote desktop.
- GCC 16.2.0 (MSYS2 UCRT64)
- CMake 4.4.5
- Ninja 1.13.2
- SQLite 3.54.1, Boost 1.92.0
- Configure command: cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_GUI=OFF -DBUILD_TESTS=ON -DBUILD_BENCH=OFF -DWITH_ZMQ=OFF -DENABLE_IPC=OFF -DWITH_CCACHE=OFF
- Build command: cmake --build build --parallel 2

## Results

| Check | Result |
|---|---|
| CMake configure | Passed |
| Native build | Passed, 601/601 steps |
| Python consensus reference | Passed, 13/13 |
| Native validation suite | 8/8 passed before the latest public-testnet additions; rerun pending Linux CI |
| Carlitos mainnet parameter/genesis and BIP32 prefix assertions | Compiled; earlier genesis/consensus test passed |
| Carlitos public-testnet parameter/genesis test | Added and compiled; runtime execution pending |
| Carlitos regtest parameter/genesis and address-prefix assertions | Compiled; earlier regtest genesis test passed before HRP update |
| Carlitos total issuance test | Passed in earlier native validation run |
| Full upstream CTest baseline (before fork-specific test adaptations) | 95% passed; 14 failed; 1 skipped; complete post-fix rerun pending Linux CI |
| Daemon runtime smoke test on Windows | Blocked by Windows Application Control |
| Python smoke-test syntax | Passed (`py_compile`) |
| Linux end-to-end node smoke test | Added to GitHub Actions; result pending |
| GitHub push | Passed; branch is tracking origin |

## Why the full CTest suite is not green yet

The fork intentionally changes consensus and mainnet identity, so inherited tests that hard-code Bitcoin expectations need chain-aware fixtures. The initial full CTest run was a baseline only; the following source-level adaptations have since been compiled, but cannot be rerun on the Windows host because Application Control blocks the rebuilt test executable:

- `key_io_tests`: 18 mainnet address/WIF vectors in `key_io_valid.json` were re-encoded with Carlitos Base58 versions 28/50/156 and Bech32 HRP `crl`, preserving the underlying hashes and private keys.
- `script_standard_tests`: the deterministic Taproot address and seven BIP341 `bip350Address` vectors were re-encoded for `crl`; scriptPubKey and Taproot commitments were not changed.
- `key_tests`, `bloom_tests`, and `descriptor_tests`: valid mainnet WIF fixtures were re-encoded to Carlitos version 156 while retaining the same secret-key bytes (four key-test WIFs, one bloom WIF, and 31 descriptor WIFs). P2PKH expected addresses in key tests were also re-encoded to version 28.
- `rpc_tests` and `util_tests`: their hard-coded mainnet P2SH/P2PKH addresses and WIF fixtures were re-encoded to Carlitos prefixes; signature and private-key payloads remain the same.
- `miner_tests`: its fixed pre-mined block fixtures are now run on isolated Bitcoin regtest parameters, because Carlitos' changed coinbase subsidy changes the coinbase txid/Merkle root and invalidates the old precomputed nonces. This is test-only; it does not change Carlitos mainnet PoW.
- `transaction_tests`: two inherited `BADTX` fixtures had outputs above Bitcoin's 21-million limit but below Carlitos' 100-million limit. They were moved to Carlitos MAX_MONEY + 1 and MAX_MONEY plus a second positive output, respectively. CMake regenerated `tx_invalid.json.h` and rebuilt the native test binary.
- `util_tests/util_ParseMoney`: the maximum-money vector now accepts exactly 100,000,000 CRLTS and rejects one base unit above it; this focused test passed once before Windows began blocking the rebuilt executable.
- `net_peer_connection_tests`: fixed log strings expecting 8333 now use the active chain's configured port; the focused test passed once and observed 28444.
- `pow_tests`: historical Bitcoin retarget vectors use Bitcoin testnet parameters in a local copy with the min-difficulty exception disabled; follow-up compiled, runtime rerun pending Linux CI.
- `validation_chainstatemanager_tests`: when Carlitos minimum chainwork is zero, the test no longer subtracts one from unsigned zero (which wrapped to a huge work value); it omits the impossible below-zero-work fixture. The modified suite compiled.
- Mainnet BIP32 extended-key prefixes are custom (`043c524c` public, `043c5350` private); public testnet uses `043c544c` / `043c5550`; regtest uses `043c524d` / `043c5351`. Mainnet fixtures include 23 public/24 private BIP32 vectors, 3 MuSig synthetic xpub vectors, and 421 public/242 private descriptor key strings re-encoded without changing key payloads. Mainnet and testnet parameter tests now assert their serialized versions. These values are provisional and not registered in SLIP-0132; do not promise third-party wallet interoperability.
- `bip324_tests`: the original Windows run showed failures in cryptographic packet test vectors, unrelated to address prefixes; this still needs reproduction on supported Linux CI before attributing it to project code or toolchain.
- `univalue_object_test`: could not be started by Windows Application Control.
- `script_assets_tests`: skipped by CTest.

Do not infer from the 95% total that the entire upstream suite is correct for Carlitos. The targeted Carlitos native consensus suite passed, but fork-wide test adaptation and supported-platform reproduction are still required.

## Important runtime boundary

The node executables were successfully linked, but the Windows host blocked launching the newly built daemon binary. No attempt was made to bypass that local security policy. Consequently, the node has not yet been observed starting, opening RPC/P2P ports, creating a wallet, mining a block, or processing a live transaction.

## Current conclusion

The monetary parameters and genesis assertions compile and pass their targeted C++ validation tests. The code is an experimental native-node fork, not a public testnet or mainnet release. Do not use real funds or describe CRLTS as launched.
