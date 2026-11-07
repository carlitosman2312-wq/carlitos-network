#!/usr/bin/env python3
"""Two-node Carlitos regtest P2P, wallet, mining, maturity, and spend smoke test."""
import hashlib
import json
import struct
import subprocess
import tempfile
import time
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "build" / "bin"
DAEMON, CLI = BIN / "bitcoind", BIN / "bitcoin-cli"
assert DAEMON.is_file() and CLI.is_file(), "Build bitcoind and bitcoin-cli first"

P2P_A, P2P_B = 38444, 38445
RPC_A, RPC_B = 38446, 38447


with tempfile.TemporaryDirectory(prefix="carlitos-smoke-") as tmp:
    base = Path(tmp)
    nodes = {}
    log_handles = {}

    def rpc(name, *args, check=True, wallet=None, timeout=45, return_process=False):
        node = nodes[name]
        command = [
            str(CLI),
            "-chain=carlitosregtest",
            f"-datadir={node['datadir']}",
            f"-rpcport={node['rpcport']}",
            "-rpcconnect=127.0.0.1",
        ]
        if wallet:
            command.append(f"-rpcwallet={wallet}")
        command.extend(str(arg) for arg in args)
        result = subprocess.run(command, text=True, capture_output=True, timeout=timeout)
        if check and result.returncode:
            raise RuntimeError(
                f"bitcoin-cli {name} {' '.join(map(str, args))} failed: {result.stderr.strip()}"
            )
        return result if return_process else result.stdout.strip()

    def compact_target(bits):
        size = bits >> 24
        word = bits & 0x007FFFFF
        if bits & 0x00800000:
            raise ValueError(f"Negative compact target: {bits:08x}")
        if size <= 3:
            return word >> (8 * (3 - size))
        return word << (8 * (size - 3))

    def wait_for(predicate, description, timeout=60):
        deadline = time.monotonic() + timeout
        last_error = None
        while time.monotonic() < deadline:
            try:
                value = predicate()
                if value:
                    return value
            except Exception as exc:  # Retry transient RPC/startup/sync errors.
                last_error = exc
            time.sleep(0.25)
        raise RuntimeError(f"Timed out waiting for {description}; last error: {last_error}")

    def start_node(name, p2p_port, rpc_port, connect_to=None):
        datadir = base / name
        datadir.mkdir()
        log_path = base / f"{name}.log"
        log_handle = log_path.open("w+", encoding="utf-8")
        log_handles[name] = log_handle
        command = [
            str(DAEMON),
            "-chain=carlitosregtest",
            f"-datadir={datadir}",
            f"-port={p2p_port}",
            f"-rpcport={rpc_port}",
            "-server=1",
            "-daemon=0",
            "-discover=0",
            "-dnsseed=0",
            "-fixedseeds=0",
            "-natpmp=0",
            "-fallbackfee=0.0001",
            "-printtoconsole=1",
        ]
        if connect_to is None:
            command.extend(["-listen=1", "-bind=127.0.0.1"])
        else:
            # Node B is outbound-only and explicitly connects to Node A.
            command.extend(["-listen=0", f"-connect=127.0.0.1:{connect_to}"])

        process = subprocess.Popen(command, stdout=log_handle, stderr=subprocess.STDOUT)
        nodes[name] = {"datadir": datadir, "rpcport": rpc_port, "process": process, "log": log_path}

        def rpc_ready():
            if process.poll() is not None:
                raise RuntimeError(f"{name} exited early with code {process.returncode}")
            # Treat non-JSON CLI error output as "not ready" rather than a successful probe.
            response = rpc(name, "getblockchaininfo", check=False, timeout=3)
            return isinstance(json.loads(response), dict) if response else False

        wait_for(rpc_ready, f"{name} RPC startup", timeout=45)

    try:
        start_node("node-a", P2P_A, RPC_A)
        rpc("node-a", "createwallet", "miner-wallet")
        mining_address = rpc("node-a", "getnewaddress", "", "bech32", wallet="miner-wallet")
        assert mining_address.startswith("rcrl1"), mining_address

        start_node("node-b", P2P_B, RPC_B, connect_to=P2P_A)
        rpc("node-b", "createwallet", "receiver-wallet")
        receiver_address = rpc("node-b", "getnewaddress", "", "bech32", wallet="receiver-wallet")
        assert receiver_address.startswith("rcrl1"), receiver_address

        wait_for(
            lambda: int(rpc("node-b", "getconnectioncount", check=False, timeout=3) or "0") >= 1,
            "outbound P2P connection from node B to node A",
        )
        wait_for(
            lambda: int(rpc("node-a", "getconnectioncount", check=False, timeout=3) or "0") >= 1,
            "inbound P2P connection on node A",
        )
        assert rpc("node-a", "getblockhash", "0") == rpc("node-b", "getblockhash", "0")

        # Check coinbase maturity on the mining wallet while node B follows the chain.
        rpc("node-a", "generatetoaddress", "100", mining_address)
        wait_for(
            lambda: json.loads(rpc("node-b", "getblockchaininfo", check=False, timeout=3)).get("blocks", 0) >= 100,
            "node B to sync the first 100 blocks",
        )
        balance_100 = Decimal(rpc("node-a", "getbalance", wallet="miner-wallet"))
        assert balance_100 == Decimal("0"), (
            f"coinbase must remain immature at height 100, got {balance_100}"
        )

        rpc("node-a", "generatetoaddress", "1", mining_address)
        wait_for(
            lambda: json.loads(rpc("node-b", "getblockchaininfo", check=False, timeout=3)).get("blocks", 0) >= 101,
            "node B to sync block 101",
        )
        balance_101 = Decimal(rpc("node-a", "getbalance", wallet="miner-wallet"))
        assert balance_101 == Decimal("100"), (
            f"expected first 100 CRLTS reward to mature at height 101, got {balance_101}"
        )

        rpc("node-a", "generatetoaddress", "1", mining_address)
        wait_for(
            lambda: json.loads(rpc("node-b", "getblockchaininfo", check=False, timeout=3)).get("blocks", 0) >= 102,
            "node B to sync block 102",
        )
        balance_102 = Decimal(rpc("node-a", "getbalance", wallet="miner-wallet"))
        assert balance_102 == Decimal("200"), (
            f"expected second 100 CRLTS reward to mature at height 102, got {balance_102}"
        )

        # The transaction must enter node B's mempool before it is mined.
        txid = rpc(
            "node-a", "sendtoaddress", receiver_address, "1.0", wallet="miner-wallet"
        ).strip('"')
        wait_for(
            lambda: txid in json.loads(rpc("node-b", "getrawmempool", check=False, timeout=3)),
            "transaction propagation to node B's mempool",
        )

        rpc("node-a", "generatetoaddress", "1", mining_address)
        wait_for(
            lambda: json.loads(rpc("node-b", "getblockchaininfo", check=False, timeout=3)).get("blocks", 0) >= 103,
            "node B to sync block 103",
        )

        def receiver_has_confirmed_tx():
            transaction = json.loads(
                rpc("node-b", "gettransaction", txid, wallet="receiver-wallet", timeout=3)
            )
            return transaction if transaction.get("confirmations", 0) >= 1 else None

        transaction = wait_for(receiver_has_confirmed_tx, "confirmed transaction in node B's wallet")
        assert Decimal(str(transaction["amount"])) == Decimal("1.0"), transaction
        receiver_balance = Decimal(rpc("node-b", "getbalance", wallet="receiver-wallet"))
        assert receiver_balance == Decimal("1.0"), (
            f"expected receiver wallet balance 1.0 CRLTS, got {receiver_balance}"
        )
        # Exercise the BIP94 timestamp rule at the first block of difficulty period 2.
        # Stop the receiver so it does not need to download the extra boundary-test blocks.
        rpc("node-b", "stop", check=False, timeout=5)
        nodes["node-b"]["process"].wait(timeout=20)

        current_height = int(rpc("node-a", "getblockcount"))
        if current_height > 2014:
            raise AssertionError(f"Expected pre-boundary height <= 2014, got {current_height}")
        blocks_to_boundary = 2014 - current_height
        if blocks_to_boundary:
            rpc(
                "node-a", "generatetoaddress", str(blocks_to_boundary), mining_address,
                timeout=180,
            )
        assert int(rpc("node-a", "getblockcount")) == 2014

        # Give the final block before the period boundary a timestamp well ahead
        # of its median-time-past. The candidate at height 2016 must not go back
        # more than MAX_TIMEWARP (600 seconds) from this predecessor.
        previous_hash = rpc("node-a", "getbestblockhash")
        previous_header = json.loads(rpc("node-a", "getblockheader", previous_hash))
        high_time = int(previous_header["time"]) + 3600
        rpc("node-a", "setmocktime", str(high_time))
        rpc("node-a", "generatetoaddress", "1", mining_address)
        rpc("node-a", "setmocktime", "0")
        boundary_previous_hash = rpc("node-a", "getbestblockhash")
        boundary_previous = json.loads(
            rpc("node-a", "getblockheader", boundary_previous_hash)
        )
        assert boundary_previous["height"] == 2015

        # This timestamp is valid under median-time-past, but more than 600 seconds
        # behind the previous block. BIP94 must reject it at height 2016.
        candidate_time = int(boundary_previous["mediantime"]) + 1
        assert candidate_time > int(boundary_previous["mediantime"])
        assert (
            int(boundary_previous["time"]) - candidate_time > 600
        ), "BIP94 test setup did not create a 600-second timewarp"
        bits = int(boundary_previous["bits"], 16)
        version = int(boundary_previous["version"]) & 0xFFFFFFFF
        header_prefix = (
            struct.pack("<I", version)
            + bytes.fromhex(boundary_previous_hash)[::-1]
            + bytes.fromhex(boundary_previous["merkleroot"])[::-1]
            + struct.pack("<II", candidate_time, bits)
        )
        target = compact_target(bits)
        candidate_header = None
        for nonce in range(100_000):
            raw_header = header_prefix + struct.pack("<I", nonce)
            digest = hashlib.sha256(hashlib.sha256(raw_header).digest()).digest()
            if int.from_bytes(digest, "little") <= target:
                candidate_header = raw_header
                break
        assert candidate_header is not None, "Could not find a regtest-valid header nonce"

        rejection = rpc(
            "node-a", "submitheader", candidate_header.hex(),
            check=False, return_process=True,
        )
        rejection_text = (rejection.stdout + "\n" + rejection.stderr).lower()
        assert rejection.returncode != 0, (
            "BIP94 accepted a block at the period boundary with a timestamp "
            "more than 600 seconds behind its predecessor"
        )
        assert "time-timewarp-attack" in rejection_text, rejection_text
        assert int(rpc("node-a", "getblockcount")) == 2015

        print(
            "PASS: two Carlitos regtest nodes connected; blocks and mempool transaction propagated; "
            "wallets, rcrl addresses, 100-block maturity, mining, confirmed spend, and BIP94 "
            "timestamp rejection verified"
        )
    except Exception:
        for handle in log_handles.values():
            handle.flush()
        for name, node in nodes.items():
            print(f"--- {name} log (tail) ---")
            try:
                print(node["log"].read_text(encoding="utf-8", errors="replace")[-12000:])
            except OSError as exc:
                print(f"Could not read log: {exc}")
        raise
    finally:
        for name in reversed(list(nodes)):
            node = nodes[name]
            process = node["process"]
            if process.poll() is None:
                rpc(name, "stop", check=False, timeout=5)
                try:
                    process.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    process.terminate()
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
        for handle in log_handles.values():
            handle.close()
