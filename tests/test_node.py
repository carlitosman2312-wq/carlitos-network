import json
from threading import Thread
from urllib.request import Request, urlopen

from carlitos.chain import Chain
from carlitos.crypto import address_from_public_key, generate_private_key, public_key_bytes
from carlitos.node import NodeServer


def test_loopback_node_api_mines_and_persists(tmp_path):
    key = generate_private_key()
    address = address_from_public_key(public_key_bytes(key))
    database = tmp_path / "chain.json"
    chain = Chain(difficulty=1)
    server = NodeServer(("127.0.0.1", 0), chain, str(database))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base + "/health") as response:
            assert json.loads(response.read())["ok"] is True

        payload = json.dumps({"address": address}).encode()
        request = Request(base + "/mine", data=payload, method="POST", headers={"Content-Type": "application/json"})
        with urlopen(request) as response:
            result = json.loads(response.read())
        assert result["mined"] is True
        assert chain.height == 1
        assert database.exists()

        with urlopen(base + "/info") as response:
            info = json.loads(response.read())
        assert info["height"] == 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
