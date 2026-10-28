#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/scripts/check-direct-content-contract.py" "$1" "$ROOT"
python3 - "$ROOT" "$1" <<'PY'
import importlib.util,json,pathlib,shutil,sys,tempfile
root=pathlib.Path(sys.argv[1])
spec=importlib.util.spec_from_file_location('contract_check',root/'scripts/check-direct-content-contract.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
contract=json.loads(pathlib.Path(sys.argv[2]).read_text())
for label, old, new in [('workspace','workspace_id','workspace_omitted'),('request','request_id','request_omitted'),('receipt','"request_state":"accepted"','"request_state":"completed"'),('routing','**Explicit content → direct capabilities.**','Everything is done by sending the CMO')]:
 with tempfile.TemporaryDirectory(prefix='autowhisper-skill-contract-') as directory:
  target=pathlib.Path(directory);(target/'references').mkdir()
  for name in ['SKILL.md','references/api-reference.md']:
   (target/name).write_text((root/name).read_text().replace(old,new))
  try: module.check(target,contract)
  except (AssertionError,KeyError): pass
  else: raise AssertionError(f'{label} mutation escaped detection')
print('Four negative document mutations: rejected')
PY
