#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 -B "$ROOT/scripts/check-direct-content-contract.py" "$1" "$ROOT"
python3 -B - "$ROOT" "$1" <<'PY'
import importlib.util,json,pathlib,re,sys,tempfile
root=pathlib.Path(sys.argv[1])
spec=importlib.util.spec_from_file_location('contract_check',root/'scripts/check-direct-content-contract.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
contract=json.loads(pathlib.Path(sys.argv[2]).read_text())
skill=(root/'SKILL.md').read_text()
reference=(root/'references/api-reference.md').read_text()
prose, embedded=reference.split('<!-- direct-content-contract -->',1)
cases=[
 ('workspace',skill.replace('workspace_id','workspace_omitted'),reference),
 ('request',skill.replace('request_id','request_omitted'),reference),
 ('receipt',skill,reference.replace('"request_state":"accepted"','"request_state":"completed"')),
 ('routing',skill.replace('**Explicit content → direct capabilities.**','Everything is done by sending the CMO'),reference),
 ('prose route',skill,prose.replace('### POST /api/content/operations\n','### POST /api/content/old_operations\n')+'<!-- direct-content-contract -->'+embedded),
 ('prose required fields',skill,prose.replace('Required: workspace_id, request_id, operation.','Required: workspace_id, request_id, operation, task_id.')+'<!-- direct-content-contract -->'+embedded),
 ('native adoption branch',skill,prose.replace('Native target requires: content_ref, expected_content_revision.','Native target requires: content_ref.')+'<!-- direct-content-contract -->'+embedded),
 ('missing read endpoint',skill,re.sub(r'### GET /api/content/items\n.*?(?=### )','',prose,flags=re.S)+'<!-- direct-content-contract -->'+embedded),
 ('missing recovery guidance',skill,prose.replace('`target_busy`','busy_target')+'<!-- direct-content-contract -->'+embedded),
]
for label,changed_skill,changed_reference in cases:
 assert (changed_skill,changed_reference)!=(skill,reference),f'{label} mutation did not change its target'
 with tempfile.TemporaryDirectory(prefix='autowhisper-skill-contract-') as directory:
  target=pathlib.Path(directory);(target/'references').mkdir()
  (target/'SKILL.md').write_text(changed_skill)
  (target/'references/api-reference.md').write_text(changed_reference)
  try: module.check(target,contract)
  except (AssertionError,KeyError): pass
  else: raise AssertionError(f'{label} mutation escaped detection')
print(f'{len(cases)} negative document mutations: rejected (including prose-only drift)')
PY
