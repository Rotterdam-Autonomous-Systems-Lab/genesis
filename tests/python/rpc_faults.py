"""Temporary literal-loopback RPC fault proxy; forwards only to its own Anvil."""

import http.client
import json
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


class FaultProxy:
    def __init__(self, upstream, mode):
        self.upstream = urlsplit(upstream)
        assert self.upstream.hostname == "127.0.0.1"
        self.mode = mode
        self.calls = []
        self.paths = []
        self.error_payload = None

    def __enter__(self):
        proxy = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                proxy.paths.append(self.path)
                if self.path == "/forbidden":
                    self.send_error(400)
                    return
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 2**20:
                    self.send_error(413)
                    return
                raw = self.rfile.read(length)
                request = json.loads(raw)
                method = request["method"]
                proxy.calls.append(method)
                if method == "eth_sendRawTransaction" and proxy.mode == "before_send":
                    self.connection.shutdown(socket.SHUT_RDWR)
                    self.connection.close()
                    return
                conn = http.client.HTTPConnection(
                    "127.0.0.1", proxy.upstream.port, timeout=2
                )
                try:
                    conn.request("POST", "/", raw, {"Content-Type": "application/json"})
                    result = json.loads(conn.getresponse().read(2**20))
                finally:
                    conn.close()
                if method == "eth_sendRawTransaction" and proxy.mode == "after_send":
                    self.connection.shutdown(socket.SHUT_RDWR)
                    self.connection.close()
                    return
                if (
                    method == "eth_call"
                    and proxy.mode == "offchain"
                    and proxy.error_payload is not None
                ):
                    result = {
                        "jsonrpc": "2.0",
                        "id": request["id"],
                        "error": {
                            "code": 3,
                            "message": "execution reverted",
                            "data": proxy.error_payload,
                        },
                    }
                if method == "eth_sendRawTransaction" and proxy.mode == "wrong_hash":
                    result["result"] = "0x" + "ab" * 32
                receipt = result.get("result")
                if method == "eth_getTransactionReceipt" and isinstance(receipt, dict):
                    if proxy.mode == "receipt_hash":
                        receipt["transactionHash"] = "0x" + "ab" * 32
                    if proxy.mode == "receipt_status":
                        receipt["status"] = "0x2"
                    if proxy.mode == "event_price" and receipt.get("logs"):
                        data = receipt["logs"][0]["data"]
                        receipt["logs"][0]["data"] = data[:-64] + format(1, "064x")
                    if proxy.mode == "event_emitter" and receipt.get("logs"):
                        receipt["logs"][0]["address"] = "0x" + "ab" * 20
                encoded = json.dumps(result).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_port}"
        return self

    def __exit__(self, *args):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        assert not self.thread.is_alive()
