"""Loopback-only JSON API for a local CRLTS development node."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import re
from urllib.parse import urlparse

from .chain import Chain, ConsensusError
from .consensus import format_amount, subsidy
from .models import Transaction


class NodeServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address: tuple[str, int], chain: Chain, database: str):
        if address[0] not in {"127.0.0.1", "::1", "localhost"}:
            raise ValueError("the prototype RPC must bind to loopback; public RPC is not safe")
        self.chain = chain
        self.database = database
        super().__init__(address, RequestHandler)


class RequestHandler(BaseHTTPRequestHandler):
    server: NodeServer

    def log_message(self, fmt: str, *args: object) -> None:
        print("[crlts-node] " + fmt % args)

    def _send(self, status: int, payload: object) -> None:
        data = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _body(self) -> dict:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 1_000_000:
                raise ValueError("request body must be between 1 byte and 1 MB")
            value = json.loads(self.rfile.read(length))
            if not isinstance(value, dict):
                raise ValueError("JSON body must be an object")
            return value
        except (ValueError, json.JSONDecodeError) as exc:
            raise ValueError(f"invalid JSON request: {exc}") from exc

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        chain = self.server.chain
        if path == "/health":
            return self._send(200, {"ok": True, "network": "carlitos-devnet"})
        if path == "/info":
            return self._send(200, {
                "network": "carlitos-devnet",
                "height": chain.height,
                "tip_hash": chain.tip.block_hash,
                "chainwork": str(chain.chainwork),
                "mempool_size": len(chain.mempool),
                "difficulty_leading_zeroes": chain.difficulty,
                "next_subsidy_base_units": subsidy(chain.height + 1),
                "next_subsidy": format_amount(subsidy(chain.height + 1)),
                "warning": "experimental local devnet; not mainnet or production secure",
            })
        if path == "/blocks/latest":
            return self._send(200, chain.tip.to_dict())
        match = re.fullmatch(r"/blocks/(\d+)", path)
        if match:
            height = int(match.group(1))
            if height >= len(chain.blocks):
                return self._send(404, {"error": "block not found"})
            return self._send(200, chain.blocks[height].to_dict())
        match = re.fullmatch(r"/address/(crltsd[0-9a-f]{40})", path)
        if match:
            address = match.group(1)
            utxos = chain.get_utxos(address)
            mature = chain.get_utxos(address, mature_only=True)
            return self._send(200, {
                "address": address,
                "balance": format_amount(sum(item.amount for item in utxos)),
                "balance_base_units": sum(item.amount for item in utxos),
                "spendable_balance": format_amount(sum(item.amount for item in mature)),
                "utxos": [item.to_dict() for item in mature],
            })
        if path == "/chain":
            return self._send(200, chain.export())
        return self._send(404, {"error": "endpoint not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            body = self._body()
            if path == "/transactions":
                tx = Transaction.from_dict(body)
                txid = self.server.chain.add_transaction(tx)
                return self._send(202, {"accepted": True, "txid": txid})
            if path == "/mine":
                address = str(body.get("address", ""))
                block = self.server.chain.mine_block(address)
                self.server.chain.save(self.server.database)
                return self._send(200, {"mined": True, "height": block.height, "hash": block.block_hash, "nonce": block.nonce})
            return self._send(404, {"error": "endpoint not found"})
        except (ValueError, ConsensusError, KeyError, TypeError) as exc:
            return self._send(400, {"error": str(exc)})


def serve(chain: Chain, database: str, host: str = "127.0.0.1", port: int = 8338) -> None:
    server = NodeServer((host, port), chain, database)
    print(f"CRLTS devnet node listening at http://{host}:{port}")
    print("RPC is loopback-only. Do not expose this prototype node to the public internet.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping node...")
    finally:
        chain.save(database)
        server.server_close()
