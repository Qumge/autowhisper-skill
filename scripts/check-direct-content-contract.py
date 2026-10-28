#!/usr/bin/env python3
"""Validate the skill's actual routing and reference contract offline."""
import json
import pathlib
import re
import sys


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
    assert "**Explicit content → direct capabilities.**" in skill, "explicit content must use direct capabilities"
    assert "Everything is done by sending the CMO" not in skill, "legacy all-content CMO routing returned"
    assert '"request_state":"accepted"' in reference, "submission receipt must say accepted"
    assert "applied does not mean delivered" in skill, "request acceptance must not imply delivery"
    for field in ("charged_credits", "refunded_credits", "previous_previews"):
        assert field in skill, f"missing truthful result guidance: {field}"
    for tool in capabilities["tools"]:
        assert tool["name"] in skill, f"missing tool {tool['name']}"
    for field in ("workspace_id", "request_id", "expected_task_revision", "expected_revisions", "preview_approval", "submission_unknown", "requires_planning"):
        assert field in skill, f"missing operational guidance: {field}"


if __name__ == "__main__":
    root = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else pathlib.Path(__file__).resolve().parent.parent)
    check(root, json.loads(pathlib.Path(sys.argv[1]).read_text()))
    print("Direct content skill contract: passed")
