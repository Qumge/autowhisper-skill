# Direct content examples

Use real IDs discovered from status, products and task/content reads. The IDs and
preview bindings below illustrate request shapes. Set AUTOWHISPER_BASE_URL and
AUTOWHISPER_API_TOKEN for the intended environment. Generation uses native credits
after confirmation; these examples do not publish. Do not execute example IDs or
placeholder preview bindings in production. Execute each section only when the
user has authorized its stated work.

## Find the most recently finished video and its share page

Resolve the workspace with status and, if needed, the product with products.
This read uses the latest completion ordering, not creation time:

```bash
BASE_URL="${AUTOWHISPER_BASE_URL:?set the intended API base}"
TOKEN="${AUTOWHISPER_API_TOKEN:?connect first}"
curl -fsS "$BASE_URL/api/content/items?workspace_id=12&content_type=video&completed=true&limit=1" -H "Authorization: Bearer $TOKEN"
```

Read the returned share_url/video_url. For an exact record, use its returned
content_type and content_id with get content; do not pass the list-only type video
to the detail endpoint. These reads do not generate, publish or charge credits.

## One UGC, from submission to final video

Read context, select its supported preset, then submit the exact request. The
sample asks for 15 seconds; if that preset cannot preserve 15 seconds, explain
requires_planning rather than silently choosing a different length.

```bash
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
curl -fsS -X POST "$BASE_URL/api/content/operations" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"workspace_id":12,"request_id":"example_render_001","task_id":56,"operation":"resume","item_ids":[78],"expected_task_revision":2,"expected_revisions":{"78":2},"preview_approval":{"operation_id":9,"revision":2,"preview_digest":"replace_with_server_binding","credits":20}}'
curl -fsS "$BASE_URL/api/content/tasks/56?workspace_id=12" -H "Authorization: Bearer $TOKEN"
```

Confirm the returned request first, then query autowhisper_task with workspace_id
and task_id=56. Poll at next_poll_after_ms within the SKILL's bound. Report the
final video only when delivery_complete=true and artifacts contain the delivered
current video. No elapsed-time guess or first frame proves it.

## Change part of one existing image

Read task 90 to obtain current task/item revisions. Select the exact image, keep
the same task and item, and submit the user's change; do not create a replacement
batch. Here the user explicitly requested the second image's warmer background:

```bash
curl -fsS -X POST "$BASE_URL/api/content/operations" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"workspace_id":12,"request_id":"example_image_001","task_id":90,"operation":"revise","item_ids":[91],"expected_task_revision":3,"expected_revisions":{"91":4},"patch":{"direction":"Use a warmer background; keep the product unchanged"},"unit_selector":{"kind":"image","position":2}}'
```

Follow its confirmation and native review steps. A 409 requires a fresh read and
target check; it does not authorize changing expected revisions blindly.

## Revise an existing native New draft without a task ID

Read its exact detail first. Continue only if available_operations contains the
requested operation and blocked_reason is empty. Use the returned content_ref and
content_revision; the native branch does not take task/item target fields:

```bash
NATIVE=$(curl -fsS "$BASE_URL/api/content/items/ugc/123?workspace_id=12" -H "Authorization: Bearer $TOKEN")
jq -e '(.available_operations | index("revise")) != null and (.blocked_reason == null)' <<<"$NATIVE" >/dev/null
ADOPT_PAYLOAD=$(jq -c '{workspace_id:12,request_id:"example_adopt_001",operation:"revise",content_ref:.content_ref,expected_content_revision:.content_revision,patch:{direction:"Use a warmer background; keep the product unchanged"}}' <<<"$NATIVE")
curl -fsS -X POST "$BASE_URL/api/content/operations" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d "$ADOPT_PAYLOAD"
```

Native adoption preserves this existing content. Follow the returned request's
quote, confirmation, native task and preview review. Busy or published content is
protected; do not bypass that by creating a replacement with a new request ID.

## Stage, reorder and confirm a numbered media batch

Use owned attachment IDs or persistent owned URLs returned by import (maximum
5 imports per call, 10 materials per batch). The illustrative IDs below are
existing owned attachments, in the user's chosen order. For dynamic Fashion use
the native outfit option; do not replace it with a static montage.

```bash
curl -fsS -X POST "$BASE_URL/api/content/media_batches" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"workspace_id":12,"request_id":"example_media_001","attachments":[{"attachment_id":301},{"attachment_id":302}],"options":{"kind":"montage","timing":"original"}}'
BATCH=$(curl -fsS "$BASE_URL/api/content/media_batches?workspace_id=12&batch_id=7" -H "Authorization: Bearer $TOKEN")
REORDER_PAYLOAD=$(jq -c '{workspace_id:12,request_id:"example_reorder_001",batch_id:.batch_id,expected_revision:.revision,action:"reorder",numbers:[2,1]}' <<<"$BATCH")
curl -fsS -X PATCH "$BASE_URL/api/content/media_batches/7" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d "$REORDER_PAYLOAD"
BATCH=$(curl -fsS "$BASE_URL/api/content/media_batches?workspace_id=12&batch_id=7" -H "Authorization: Bearer $TOKEN")
```

Material numbers remain stable after reordering. Show the current native quote,
order and options. If pending_question is present or confirmation_token is null,
resolve the question/wait for material readiness and reread; never invent a token.
The following separate confirmation spends credits and requires the user's
authorization for the displayed quote and scope:

```bash
jq -e '.confirmation_token != null' <<<"$BATCH" >/dev/null
CONFIRM_PAYLOAD=$(jq -c '{workspace_id:12,request_id:"example_confirm_001",batch_id:.batch_id,expected_revision:.revision,action:"confirm",confirmation_token:.confirmation_token}' <<<"$BATCH")
curl -fsS -X PATCH "$BASE_URL/api/content/media_batches/7" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d "$CONFIRM_PAYLOAD"
curl -fsS "$BASE_URL/api/content/media_batches?workspace_id=12&batch_id=7" -H "Authorization: Bearer $TOKEN"
```

Use the batch_id returned by creation instead of illustrative 7 in actual calls.
Retry each write with its original request_id and identical payload. Read the
batch's status/result_url for completion; confirmation is generation, not
publication. Publishing a ready batch later requires a separate publish_content
action with the exact owner-approved caption and destination scope. Filmstrip
cannot publish.

## Accepted batch still unfinished

```bash
curl -fsS "$BASE_URL/api/content/requests/example_batch_001?workspace_id=12" -H "Authorization: Bearer $TOKEN"
```

If request_state=applied, task_state=waiting_review and delivery_complete=false,
say: “The batch was accepted and is waiting for review; the final deliverables
are not ready.” Show previews and the returned next action. Never create a new
request_id to make an uncertain or unfinished batch appear to start faster.
