"""Command-line tools for the Carlitos Network local devnet."""

import argparse
import getpass
import json
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .chain import Chain
from .consensus import format_amount, parse_amount
from .crypto import address_from_public_key, generate_private_key, load_wallet, public_key_bytes, save_wallet
from .models import Transaction, TxOutput
from .node import serve

DEFAULT_DIR = Path.home() / ".carlitos"


def _rpc(url: str, method: str = "GET", body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=10) as response:
            value = json.loads(response.read())
    except HTTPError as exc:
        try:
            detail = json.loads(exc.read()).get("error", str(exc))
        except Exception:
            detail = str(exc)
        raise RuntimeError(f"node RPC failed: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"cannot connect to node: {exc.reason}") from exc
    if not isinstance(value, dict):
        raise RuntimeError("node returned an invalid response")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="crlts", description="Carlitos Network local development-chain tools")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DIR, help=f"node data directory (default: {DEFAULT_DIR})")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="create the local genesis database")
    wallet = sub.add_parser("wallet", help="wallet tools")
    wallet_sub = wallet.add_subparsers(dest="wallet_command", required=True)
    wallet_new = wallet_sub.add_parser("new", help="create an encrypted devnet wallet")
    wallet_new.add_argument("--file", type=Path, default=Path("crlts-wallet.json"))
    wallet_info = wallet_sub.add_parser("address", help="show the public address stored in a wallet")
    wallet_info.add_argument("--file", type=Path, required=True)

    node = sub.add_parser("node", help="run the local JSON-RPC node")
    node.add_argument("--host", default="127.0.0.1")
    node.add_argument("--port", type=int, default=8338)

    mine = sub.add_parser("mine", help="mine one block using the local database")
    mine.add_argument("--address", required=True)

    status = sub.add_parser("status", help="show local chain status")
    balance = sub.add_parser("balance", help="query an address balance from a running node")
    balance.add_argument("--address", required=True)
    balance.add_argument("--node-url", default="http://127.0.0.1:8338")

    send = sub.add_parser("send", help="send CRLTS from a wallet via a running node")
    send.add_argument("--wallet", type=Path, required=True)
    send.add_argument("--to", required=True)
    send.add_argument("--amount", required=True)
    send.add_argument("--fee", default="0.00010000")
    send.add_argument("--node-url", default="http://127.0.0.1:8338")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    database = args.data_dir.expanduser() / "chain.json"
    try:
        if args.command == "init":
            chain = Chain.load(database)
            chain.save(database)
            print(f"Initialized CRLTS devnet database: {database}")
            print(f"Genesis hash: {chain.blocks[0].block_hash}")
            return 0

        if args.command == "wallet" and args.wallet_command == "new":
            password = getpass.getpass("Set wallet password: ")
            confirm = getpass.getpass("Confirm password: ")
            if password != confirm:
                raise ValueError("passwords do not match")
            private_key = generate_private_key()
            address = save_wallet(args.file, private_key, password)
            print(f"Created encrypted CRLTS devnet wallet: {args.file.expanduser()}")
            print(f"Address: {address}")
            print("Keep the wallet file and password safe. This is a development-only address format.")
            return 0

        if args.command == "wallet" and args.wallet_command == "address":
            wallet = json.loads(args.file.expanduser().read_text(encoding="utf-8"))
            print(wallet["address"])
            return 0

        if args.command == "node":
            chain = Chain.load(database)
            chain.save(database)
            serve(chain, str(database), args.host, args.port)
            return 0

        if args.command == "mine":
            chain = Chain.load(database)
            block = chain.mine_block(args.address)
            chain.save(database)
            print(f"Mined block {block.height}")
            print(f"Hash: {block.block_hash}")
            print(f"Nonce: {block.nonce}")
            return 0

        if args.command == "status":
            chain = Chain.load(database)
            print(json.dumps({"network": "carlitos-devnet", "height": chain.height, "tip_hash": chain.tip.block_hash, "chainwork": str(chain.chainwork), "difficulty_leading_zeroes": chain.difficulty, "database": str(database)}, indent=2))
            return 0

        if args.command == "balance":
            info = _rpc(f"{args.node_url.rstrip('/')}/address/{args.address}")
            print(json.dumps(info, indent=2))
            return 0

        if args.command == "send":
            amount = parse_amount(args.amount)
            fee = parse_amount(args.fee)
            password = getpass.getpass("Wallet password: ")
            private_key = load_wallet(args.wallet, password)
            address = address_from_public_key(public_key_bytes(private_key))
            data = _rpc(f"{args.node_url.rstrip('/')}/address/{address}")
            if not args.to.startswith("crltsd") or len(args.to) != 46:
                raise ValueError("recipient must be a CRLTS devnet address")
            coins = []
            available = 0
            for item in data.get("utxos", []):
                coins.append((item["txid"], int(item["vout"]), int(item["amount"])))
                available += int(item["amount"])
                if available >= amount + fee:
                    break
            if available < amount + fee:
                raise ValueError("insufficient spendable balance (coinbase outputs require 100 confirmations)")
            outputs = [TxOutput(amount, args.to)]
            change = available - amount - fee
            if change:
                outputs.append(TxOutput(change, address))
            tx = Transaction.signed(private_key, coins, outputs)
            response = _rpc(f"{args.node_url.rstrip('/')}/transactions", method="POST", body=tx.to_dict())
            print(json.dumps(response, indent=2))
            print(f"Fee: {format_amount(fee)} CRLTS")
            return 0

        raise RuntimeError("unsupported command")
    except (ValueError, RuntimeError, OSError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
