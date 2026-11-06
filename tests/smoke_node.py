#!/usr/bin/env python3
"""Local Carlitos regtest node, wallet, mining, maturity, and spend smoke test."""
import json
import subprocess
import tempfile
import time
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "build" / "bin"
DAEMON, CLI = BIN / "bitcoind", BIN / "bitcoin-cli"
assert DAEMON.is_file() and CLI.is_file(), "Build bitcoind and bitcoin-cli first"

with tempfile.TemporaryDirectory(prefix="carlitos-smoke-") as tmp:
    data = Path(tmp)
    log_path = data / "daemon.log"
    cli_base = [str(CLI), "-chain=carlitosregtest", f"-datadir={data}"]

    def rpc(*args, check=True, wallet=False):
        command = cli_base + (["-rpcwallet=smoke-wallet"] if wallet else []) + list(args)
        result = subprocess.run(command, text=True, capture_output=True, timeout=45)
        if check and result.returncode:
            raise RuntimeError(f"bitcoin-cli {' '.join(args)} failed: {result.stderr.strip()}")
        return result.stdout.strip()

    with log_path.open("w+") as log:
        node = subprocess.Popen([
            str(DAEMON), "-chain=carlitosregtest", f"-datadir={data}", "-server=1",
            "-daemon=0", "-listen=0", "-discover=0", "-dnsseed=0", "-fixedseeds=0",
            "-upnp=0", "-natpmp=0", "-fallbackfee=0.0001", "-printtoconsole=1",
        ], stdout=log, stderr=subprocess.STDOUT)
        try:
            for _ in range(90):
                if node.poll() is not None:
                    raise RuntimeError(f"bitcoind exited early with code {node.returncode}")
                probe = rpc("getblockchaininfo", check=False)
                if probe:
                    break
                time.sleep(0.5)
            else:
                raise RuntimeError("Carlitos RPC did not become ready within 45 seconds")

            info = json.loads(rpc("getblockchaininfo"))
            assert info["blocks"] == 0, info
            rpc("createwallet", "smoke-wallet")
            mining_address = rpc("getnewaddress", "", "bech32", wallet=True)
            assert mining_address.startswith("rcrl1"), mining_address

            rpc("generatetoaddress", "100", mining_address)
            balance_100 = Decimal(rpc("getbalance", wallet=True))
            assert balance_100 == Decimal("0"), f"coinbase must remain immature at height 100, got {balance_100}"
            rpc("generatetoaddress", "1", mining_address)
            balance_101 = Decimal(rpc("getbalance", wallet=True))
            assert balance_101 == Decimal("100"), f"expected first 100 CRLTS reward to mature at height 101, got {balance_101}"
            rpc("generatetoaddress", "1", mining_address)
            balance_102 = Decimal(rpc("getbalance", wallet=True))
            assert balance_102 == Decimal("200"), f"expected second 100 CRLTS reward to mature at height 102, got {balance_102}"

            destination = rpc("getnewaddress", "", "bech32", wallet=True)
            txid = rpc("sendtoaddress", destination, "1.0", wallet=True).strip('"')
            rpc("generatetoaddress", "1", mining_address)
            transaction = json.loads(rpc("gettransaction", txid, wallet=True))
            assert transaction["confirmations"] >= 1, transaction
            assert json.loads(rpc("getblockchaininfo"))["blocks"] == 103
            print("PASS: Carlitos regtest node, RPC, wallet, tcrl address, 100-block maturity, mining, and confirmed spend")
        except Exception:
            log.flush()
            log.seek(0)
            print("--- bitcoind log (tail) ---")
            print(log.read()[-12000:])
            raise
        finally:
            if node.poll() is None:
                rpc("stop", check=False)
                try:
                    node.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    node.terminate()
                    node.wait(timeout=10)
