#!/usr/bin/env python3
"""Replay the documented curl requests through a local contract-validating stub."""
import http.server
import json
import os
import pathlib
import re
import subprocess
import sys
import threading
import urllib.parse

root = pathlib.Path(__file__).resolve().parent.parent
tools = {tool["name"]: tool for tool in json.loads(pathlib.Path(sys.argv[1]).read_text())["content_capabilities"]["tools"]}
requests = []
errors = []


def validate(value, schema):
    kind = schema.get("type")
    if isinstance(kind, list):
        if value is None and "null" in kind: return
        kind = next(part for part in kind if part != "null")
    if kind == "object":
        assert isinstance(value, dict)
        assert all(key in value for key in schema.get("required", []))
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False: assert not (value.keys() - properties.keys())
        for key, item in value.items(): validate(item, properties.get(key, schema.get("additionalProperties", {})) if isinstance(schema.get("additionalProperties", {}), dict) else properties.get(key, {}))
    elif kind == "array":
        assert isinstance(value, list) and len(value) >= schema.get("minItems", 0) and len(value) <= schema.get("maxItems", 10000)
        for item in value: validate(item, schema.get("items", {}))
    elif kind == "integer": assert isinstance(value, int) and value >= schema.get("minimum", -1)
    elif kind == "string":
        assert isinstance(value, str) and len(value) >= schema.get("minLength", 0) and len(value) <= schema.get("maxLength", 100000)
        if "pattern" in schema: assert re.fullmatch(schema["pattern"], value)
    if "enum" in schema: assert value in schema["enum"]


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *_): pass
    def do_GET(self): self.answer("GET")
    def do_POST(self): self.answer("POST")
    def answer(self, method):
        try:
            parsed = urllib.parse.urlparse(self.path)
            payload = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0)))) if method == "POST" else {key: int(values[0]) if key.endswith("_id") else values[0] for key, values in urllib.parse.parse_qs(parsed.query).items()}
            path = parsed.path
            if path == "/api/content/context": name = "autowhisper_context"
            elif path == "/api/content/tasks": name = "autowhisper_create_content"
            elif path.endswith("/operations"):
                name = "autowhisper_update_task"; payload["task_id"] = int(path.split("/")[-2])
            else:
                name = "autowhisper_task"; payload["request_id"] = path.split("/")[-1]
            validate(payload, tools[name]["inputSchema"])
            assert self.headers.get("Authorization") == "Bearer offline-example-token"
            requests.append((method, path, payload))
            response = {"request_state": "accepted", "delivery_complete": False} if method == "POST" else {"request_state": "applied", "task_state": "waiting_review", "delivery_complete": False, "previews": [{"role": "first_frame"}]}
            self.send_response(202 if method == "POST" else 200)
        except Exception as error:
            errors.append(repr(error)); response = {"error": str(error)}; self.send_response(422)
        self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(json.dumps(response).encode())


server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
worker = threading.Thread(target=server.serve_forever, daemon=True); worker.start()
try:
    document = (root / "references/direct-content-examples.md").read_text()
    commands = "\n".join(re.findall(r"```bash\n(.*?)\n```", document, re.S))
    environment = os.environ | {"AUTOWHISPER_BASE_URL": f"http://127.0.0.1:{server.server_port}", "AUTOWHISPER_API_TOKEN": "offline-example-token"}
    result = subprocess.run(["bash", "-eu"], input=commands, text=True, env=environment, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert not errors, errors
    assert len(requests) == 6, f"expected all six documented requests, got {len(requests)}"
    assert any(payload.get("unit_selector", {}).get("position") == 2 for _, _, payload in requests)
    print("Three documented flows / six curl requests: passed against local stub; no providers called")
finally:
    server.shutdown(); server.server_close(); worker.join()
