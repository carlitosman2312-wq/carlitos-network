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
| Native validation suite | Passed, 8/8 |
| Carlitos mainnet parameter/genesis test | Passed |
| Carlitos dev-network parameter/genesis test | Passed |
| Carlitos total issuance test | Passed |
| Full upstream CTest | 95% passed; 14 failed; 1 skipped |
| Daemon runtime smoke test | Blocked by Windows Application Control |
| GitHub push | Pending Git Credential Manager authentication |

## Why the full CTest suite is not green yet

The fork intentionally changes consensus and mainnet identity, so inherited tests that hard-code Bitcoin expectations must be revised before the full suite can pass. Observed failures include:

- key_io_tests, script_standard_tests, and util_tests: old Bitcoin address prefixes and message-verification vectors.
- net_peer_connection_tests: expected Bitcoin's 8333 port instead of Carlitos' 28444.
- pow_tests and miner_tests: old Bitcoin mainnet proof-of-work target assumptions.
- util_tests, transaction_tests, and related money tests: old 21-million-coin MAX_MONEY assumption.
- rpc_tests and validation_chainstatemanager_tests: require separate review of old chain-specific assumptions.
- bip324_tests, bloom_tests, key_tests, and some other tests: failures/crashes observed under this Windows/MSYS2/GCC toolchain and require reproduction on supported Linux CI.
- univalue_object_test: could not be started by Windows Application Control.
- script_assets_tests: skipped by CTest.

Do not infer from the 95% total that the entire upstream suite is correct for Carlitos. The targeted Carlitos native consensus suite passed, but fork-wide test adaptation and supported-platform reproduction are still required.

## Important runtime boundary

The node executables were successfully linked, but the Windows host blocked launching the newly built daemon binary. No attempt was made to bypass that local security policy. Consequently, the node has not yet been observed starting, opening RPC/P2P ports, creating a wallet, mining a block, or processing a live transaction.

## Current conclusion

The monetary parameters and genesis assertions compile and pass their targeted C++ validation tests. The code is an experimental native-node fork, not a public testnet or mainnet release. Do not use real funds or describe CRLTS as launched.
