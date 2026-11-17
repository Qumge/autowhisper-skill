#!/usr/bin/env python3
"""Validate embedded and readable direct-content contracts against Rails."""
import json
import pathlib
import re
import sys


def fields(section, label):
    match = re.search(rf"^{re.escape(label)}: ([a-z_, ]+)\.", section, re.M)
    assert match, f"missing {label} declaration in readable endpoint"
    return set(re.findall(r"[a-z_]+", match[1]))


def check(root, contract):
    skill = (root / "SKILL.md").read_text()
    reference = (root / "references/api-reference.md").read_text()
    capabilities = contract["content_capabilities"]
    match = re.search(r"<!-- direct-content-contract -->\s*```json\s*(.*?)\s*```", reference, re.S)
    assert match, "missing direct capability reference contract"
    documented = json.loads(match[1])
    expected = {key: capabilities[key] for key in ("schema_version", "workspace_required", "request_states", "task_states", "error_codes")}
    expected["tools"] = [{key: tool[key] for key in ("name", "method", "path")} | {"required": tool["inputSchema"]["required"]} for tool in capabilities["tools"]]
    assert documented == expected, "documented routes, required fields or states drifted from Rails"

    # A matching JSON snapshot cannot compensate for stale prose that agents follow.
    readable = reference[:match.start()]
    sections = {
        (method, path): body
        for method, path, body in re.findall(
            r"^### (GET|POST|PATCH) (\S+)\n(.*?)(?=^### |\Z)", readable, re.M | re.S
        )
    }
    for tool in capabilities["tools"]:
        for path in tool["path"].split("|"):
            section = sections.get((tool["method"], path))
            assert section, f"missing readable endpoint for {tool['name']}: {tool['method']} {path}"
            assert f"`{tool['name']}`" in section, f"readable endpoint does not identify {tool['name']}"
            assert fields(section, "Required") == set(tool["inputSchema"]["required"]), f"readable required fields drifted for {tool['name']}"
        if tool["name"] == "autowhisper_update_task":
            section = sections[(tool["method"], tool["path"])]
            assert fields(section, "Task target requires") == set(tool["inputSchema"]["oneOf"][0]["required"]), "task revision branch drifted"
            assert fields(section, "Native target requires") == set(tool["inputSchema"]["oneOf"][1]["required"]), "native adoption branch drifted"
    for code in capabilities["error_codes"]:
        assert f"`{code}`" in readable, f"missing readable error recovery for {code}"

    assert "**Explicit content → direct capabilities.**" in skill, "explicit content must use direct capabilities"
    assert "Everything is done by sending the CMO" not in skill, "legacy all-content CMO routing returned"
    assert '"request_state":"accepted"' in readable, "submission receipt must say accepted"
    assert "applied does not mean delivered" in skill, "request acceptance must not imply delivery"
    for field in ("charged_credits", "refunded_credits", "previous_previews"):
        assert field in skill, f"missing truthful result guidance: {field}"
    for tool in capabilities["tools"]:
        assert tool["name"] in skill, f"missing tool {tool['name']}"
    for field in ("workspace_id", "request_id", "expected_task_revision", "expected_revisions", "preview_approval", "submission_unknown", "requires_planning", "content_ref", "expected_content_revision"):
        assert field in skill, f"missing operational guidance: {field}"


if __name__ == "__main__":
    root = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else pathlib.Path(__file__).resolve().parent.parent)
    check(root, json.loads(pathlib.Path(sys.argv[1]).read_text()))
    print("Direct content embedded and readable contracts: passed")
