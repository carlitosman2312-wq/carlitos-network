# Carlitos public testnet operator guide

> **Experimental network notice:** Carlitos public testnet is not deployed. This guide is for coordinated private testing only. Do not use real funds, expose RPC to the internet, or assume there are independent seed nodes.

## What an operator needs

Each operator needs a reachable host with a stable public IP address, the same validated Carlitos node build, and TCP port **48444** open for inbound/outbound peer traffic. RPC uses **48446** and should remain bound to localhost. The current chain has no DNS seeds or fixed seeds, so peers must be added manually until seed operators are provisioned.

## Build and start a node

From the repository root:

```sh
cmake -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_GUI=OFF -DBUILD_TESTS=ON
cmake --build build --parallel 2
./build/bin/bitcoind -chain=carlitostestnet -daemon=1
```

The configuration file is named `carlitos.conf`. On Linux, the main data directory is under `~/.carlitos`; public-testnet data is stored in its `carlitostestnet` network subdirectory. Keep each operator's data directory separate.

## Connect operators

Add at least one independently operated peer in `carlitos.conf`:

```ini
[carlitostestnet]
server=1
listen=1
port=48444
rpcport=48446
rpcbind=127.0.0.1
addnode=<peer-public-ip>:48444
```

Replace the placeholder with an operator's actual public IP and repeat `addnode` for additional peers. Do not configure a public `rpcbind`, forward TCP 48446, or publish RPC credentials. Open only the P2P port to the internet.

To make a one-time connection without editing the config:

```sh
./build/bin/bitcoin-cli -chain=carlitostestnet addnode <peer-public-ip>:48444 onetry
```

Check the result:

```sh
./build/bin/bitcoin-cli -chain=carlitostestnet getnetworkinfo
./build/bin/bitcoin-cli -chain=carlitostestnet getpeerinfo
./build/bin/bitcoin-cli -chain=carlitostestnet getblockchaininfo
```

An operator should verify that the peer's reported network and genesis agree with this repository before accepting it as a Carlitos peer. Never connect a node to an unknown network solely because it uses the expected port.

## Wallet testing

For disposable testnet funds only:

```sh
./build/bin/bitcoin-cli -chain=carlitostestnet createwallet testnet-operator
./build/bin/bitcoin-cli -chain=carlitostestnet -rpcwallet=testnet-operator getnewaddress
```

Testnet addresses should use the `tcrl` HRP. The current wallet descriptor generator still uses Bitcoin's BIP44 coin type `1'` on test chains and the Bitcoin purposes `44'`, `49'`, `84'`, and `86'`; Carlitos-specific derivation is not implemented. Extended-key prefixes are provisional and are not registered for third-party wallet interoperability. Use only disposable seeds and test coins. Do not reuse these seeds on Bitcoin or other networks.

## Before calling it a public testnet

A public testnet needs multiple independent operators, persistent seed infrastructure, monitoring, a block explorer, a documented miner setup, a tested wallet derivation profile, and an independent consensus/security review. This repository currently provides none of the deployed infrastructure. Manual `addnode` connections are a bootstrap workaround for controlled tests, not a substitute for public seed nodes.
