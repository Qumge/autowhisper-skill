#!/usr/bin/env python3
"""Replay documented curl commands through a contract-validating local server."""
import http.server
import json
import os
import pathlib
import re
import subprocess
import sys
import threading
import urllib.parse


def validate(value, schema):
    kind = schema.get("type")
    kinds = kind if isinstance(kind, list) else [kind]
    if kind is not None:
        types = {"object": dict, "array": list, "integer": int, "boolean": bool, "string": str, "null": type(None)}
        assert any(type(value) is types[item] for item in kinds), f"wrong type: expected {kind}"
    if isinstance(value, dict):
        assert all(key in value for key in schema.get("required", [])), f"missing fields: {schema.get('required')}"
        properties = schema.get("properties", {})
        extra_schema = schema.get("additionalProperties", {})
        if extra_schema is False:
            assert not (value.keys() - properties.keys()), f"unknown fields: {value.keys() - properties.keys()}"
        for key, item in value.items():
            validate(item, properties.get(key, extra_schema if isinstance(extra_schema, dict) else {}))
    elif isinstance(value, list):
        assert len(value) >= schema.get("minItems", 0) and len(value) <= schema.get("maxItems", 10000), "array bounds"
        if schema.get("uniqueItems"):
            assert len({json.dumps(item, sort_keys=True) for item in value}) == len(value), "duplicate array entries"
        for item in value:
            validate(item, schema.get("items", {}))
    elif type(value) is int:
        assert value >= schema.get("minimum", value) and value <= schema.get("maximum", value), "integer bounds"
    elif isinstance(value, str):
        assert schema.get("minLength", 0) <= len(value) <= schema.get("maxLength", 100000), "string bounds"
        if "pattern" in schema:
            assert re.fullmatch(schema["pattern"], value), "string pattern"
    if "enum" in schema:
        assert value in schema["enum"], "unsupported enum"
    if "oneOf" in schema:
        matches = 0
        for branch in schema["oneOf"]:
            try:
                validate(value, branch)
            except AssertionError:
                pass
            else:
                matches += 1
        assert matches == 1, f"expected exactly one target branch, got {matches}"


def replay(root, contract):
    tools = {tool["name"]: tool for tool in contract["content_capabilities"]["tools"]}
    routes = []
    for tool in tools.values():
        for path in tool["path"].split("|"):
            parts = path.split("/")
            pattern = "/".join(f"(?P<{part[1:]}>[^/]+)" if part.startswith(":") else re.escape(part) for part in parts)
            routes.append((tool["method"], re.compile(pattern), tool))
    requests, errors = [], []
    native_revision = "a" * 64
    batch = {"batch_id": 7, "workspace_id": 12, "revision": 3, "status": "draft", "kind": "montage",
             "items": [{"number": 1, "attachment_id": 301}, {"number": 2, "attachment_id": 302}],
             "quote": {"credits_now": 0, "credits_render": 20, "credits_total": 20},
             "confirmation_token": "7-3", "next_actions": ["reorder", "confirm"]}

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass
        def do_GET(self):
            self.answer("GET")
        def do_POST(self):
            self.answer("POST")
        def do_PATCH(self):
            self.answer("PATCH")
        def answer(self, method):
            try:
                parsed = urllib.parse.urlparse(self.path)
                matches = [(tool, match) for verb, pattern, tool in routes if verb == method and (match := pattern.fullmatch(parsed.path))]
                assert len(matches) == 1, f"undocumented route: {method} {parsed.path}"
                tool, match = matches[0]
                schema = tool["inputSchema"]
                payload = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0)))) if method != "GET" else {}
                for key, values in urllib.parse.parse_qs(parsed.query).items():
                    assert len(values) == 1, f"duplicate query field: {key}"
                    kind = schema["properties"].get(key, {}).get("type")
                    raw = values[0]
                    payload[key] = int(raw) if kind == "integer" else json.loads(raw) if kind == "boolean" else raw
                for key, raw in match.groupdict().items():
                    bound = int(raw) if schema["properties"][key].get("type") == "integer" else raw
                    assert key not in payload or payload[key] == bound, f"conflicting path field: {key}"
                    payload[key] = bound
                validate(payload, schema)
                assert self.headers.get("Authorization") == "Bearer offline-example-token"
                name = tool["name"]
                requests.append((name, payload))
                if name == "autowhisper_get_content":
                    response = {"content_ref": {"content_type": "ugc", "content_id": 123}, "content_revision": native_revision,
                                "available_operations": ["revise"], "blocked_reason": None}
                elif "media_batch" in name:
                    if payload.get("action") == "confirm":
                        assert payload["expected_revision"] == batch["revision"]
                        assert payload["confirmation_token"] == batch["confirmation_token"], "confirmation must use returned token"
                        batch.update(status="queued", confirmation_token=None, next_actions=[])
                    elif payload.get("action") == "reorder":
                        assert payload["expected_revision"] == batch["revision"]
                        assert payload["numbers"] == [2, 1]
                        batch.update(revision=4, confirmation_token="7-4")
                    response = batch.copy()
                elif name == "autowhisper_update_task" and "content_ref" in payload:
                    assert payload["expected_content_revision"] == native_revision, "adoption must use returned revision"
                    response = {"request_state": "accepted", "delivery_complete": False}
                elif method == "POST":
                    response = {"request_state": "accepted", "delivery_complete": False}
                else:
                    response = {"request_state": "applied", "task_state": "waiting_review", "delivery_complete": False,
                                "previews": [{"role": "first_frame"}]}
                self.send_response(202 if method != "GET" else 200)
            except Exception as error:
                errors.append(f"{method} {self.path}: {error!r}")
                response = {"error": str(error)}
                self.send_response(422)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        document = (root / "references/direct-content-examples.md").read_text()
        commands = "\n".join(re.findall(r"```bash\n(.*?)\n```", document, re.S))
        environment = os.environ | {"AUTOWHISPER_BASE_URL": f"http://127.0.0.1:{server.server_port}", "AUTOWHISPER_API_TOKEN": "offline-example-token"}
        result = subprocess.run(["bash", "-eu"], input=commands, text=True, env=environment, capture_output=True, timeout=20)
        assert result.returncode == 0, errors or result.stderr
        assert not errors, errors
        assert set(tools) <= {name for name, _ in requests}, "examples must exercise all published direct tools"
        operations = [payload for name, payload in requests if name == "autowhisper_update_task"]
        assert any("content_ref" in payload for payload in operations), "native adoption flow missing"
        assert any(payload.get("unit_selector", {}).get("position") == 2 for payload in operations), "single-image revision missing"
        assert any(payload.get("preview_approval") for payload in operations), "version-bound preview continuation missing"
        assert any(name == "autowhisper_list_content" and payload.get("completed") is True and payload.get("content_type") == "video" and payload.get("limit") == 1 for name, payload in requests), "latest finished video lookup missing"
        print(f"All {len(tools)} direct tools / {len(requests)} documented curl requests: passed against local stub; no providers called")
    finally:
        server.shutdown()
        server.server_close()
        worker.join()


def negative_schema_checks(contract):
    tools = {tool["name"]: tool for tool in contract["content_capabilities"]["tools"]}
    task = {"workspace_id": 12, "request_id": "example_change_001", "operation": "revise", "task_id": 90,
            "item_ids": [91], "expected_task_revision": 3, "expected_revisions": {"91": 4}}
    native = {"workspace_id": 12, "request_id": "example_adopt_001", "operation": "revise",
              "content_ref": {"content_type": "ugc", "content_id": 123}, "expected_content_revision": "a" * 64}
    validate(task, tools["autowhisper_update_task"]["inputSchema"])
    validate(native, tools["autowhisper_update_task"]["inputSchema"])
    cases = [
        ("missing target", "autowhisper_update_task", {k: v for k, v in task.items() if k not in ("task_id", "item_ids", "expected_task_revision", "expected_revisions")}),
        ("mixed targets", "autowhisper_update_task", task | native),
        ("missing task revisions", "autowhisper_update_task", {k: v for k, v in task.items() if k != "expected_revisions"}),
        ("bad native revision", "autowhisper_update_task", native | {"expected_content_revision": "made_up"}),
        ("invalid bool", "autowhisper_list_content", {"workspace_id": 12, "completed": "true"}),
        ("unsupported batch action", "autowhisper_update_media_batch", {"workspace_id": 12, "request_id": "example_media_001", "batch_id": 7, "expected_revision": 3, "action": "publish"}),
        ("ambiguous attachment", "autowhisper_create_media_batch", {"workspace_id": 12, "request_id": "example_media_001", "attachments": [{"attachment_id": 1, "url": "https://owned.example/image.jpg", "type": "image"}]}),
    ]
    for label, name, payload in cases:
        try:
            validate(payload, tools[name]["inputSchema"])
        except AssertionError:
            pass
        else:
            raise AssertionError(f"{label} escaped contract validation")
    print(f"{len(cases)} invalid request mutations: rejected")


if __name__ == "__main__":
    contract = json.loads(pathlib.Path(sys.argv[1]).read_text())
    root = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else pathlib.Path(__file__).resolve().parent.parent
    negative_schema_checks(contract)
    replay(root, contract)
