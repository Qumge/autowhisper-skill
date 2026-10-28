# Direct content examples

Use real IDs discovered from status, products and task reads. The IDs and bindings
below are examples. Set AUTOWHISPER_BASE_URL and AUTOWHISPER_API_TOKEN for the
intended environment. Generation uses native credits after confirmation; these
examples do not publish anything. Do not execute placeholder bindings in production.

## One UGC, from submission to final video

Read context, select its supported preset, then submit the exact request. The
sample asks for 15 seconds; if that preset cannot preserve 15 seconds, explain
requires_planning rather than silently choosing a different length.

```bash
BASE_URL="${AUTOWHISPER_BASE_URL:?set the intended API base}"
TOKEN="${AUTOWHISPER_API_TOKEN:?connect first}"
curl -fsS "$BASE_URL/api/content/context?workspace_id=12&product_id=34" -H "Authorization: Bearer $TOKEN"
curl -fsS -X POST "$BASE_URL/api/content/tasks" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"workspace_id":12,"request_id":"example_ugc_001","product_id":34,"brief":{"content_language":"en"},"items":[{"key":"ugc_one","content_type":"ugc","format":{"duration_sec":15}}]}'
curl -fsS "$BASE_URL/api/content/requests/example_ugc_001?workspace_id=12" -H "Authorization: Bearer $TOKEN"
```

Follow its returned confirmation action using autowhisper_confirm (or the
existing POST /api/cmo/confirm). Query the same request until it has a task ID.
If waiting_review exposes a first-frame preview, show it as a preview and follow
its exact server next_action. Example of the shape only:

```bash
curl -fsS -X POST "$BASE_URL/api/content/tasks/56/operations" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"workspace_id":12,"request_id":"example_render_001","operation":"resume","item_ids":[78],"expected_task_revision":2,"expected_revisions":{"78":2},"preview_approval":{"operation_id":9,"revision":2,"preview_digest":"replace_with_server_binding","credits":20}}'
```

Confirm the returned request, then query autowhisper_task with workspace_id and
task_id=56. Report the final video only when delivery_complete=true and artifacts
contain the delivered current video. No elapsed-time guess or first frame proves it.

## Change part of one existing image

Read task 90 to obtain current task/item revisions. Select the exact image, keep
the same task and item, and submit the user's change; do not create a replacement
batch. Here the user explicitly requested the second image's warmer background:

```bash
curl -fsS -X POST "$BASE_URL/api/content/tasks/90/operations" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"workspace_id":12,"request_id":"example_image_001","operation":"revise","item_ids":[91],"expected_task_revision":3,"expected_revisions":{"91":4},"patch":{"direction":"Use a warmer background; keep the product unchanged"},"unit_selector":{"kind":"image","position":2}}'
```

Follow its confirmation and native review steps. A 409 requires a fresh read and
target check; it does not authorize changing expected revisions blindly.

## Accepted batch still unfinished

```bash
curl -fsS "$BASE_URL/api/content/requests/example_batch_001?workspace_id=12" -H "Authorization: Bearer $TOKEN"
```

If request_state=applied, task_state=waiting_review and delivery_complete=false,
say: “The batch was accepted and is waiting for review; the final deliverables
are not ready.” Show previews and the returned next action. Never create a new
request_id to make an uncertain or unfinished batch appear to start faster.
