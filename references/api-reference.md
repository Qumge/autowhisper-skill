# AutoWhisper API Reference

Base: `https://autowhisper.xyz`  ·  Auth: `Authorization: Bearer <api_token>`

## Direct content capabilities

All endpoints below require explicit `workspace_id`; none default to the current workspace.
Schemas and format limits come from `GET /api/contract` → `content_capabilities`.
The rollout flag and user allowlist control new writes. Unavailable capability does not authorize a CMO fallback.

### GET /api/content/context
Required: workspace_id, product_id. Read-only facts, existing brand requirements,
material aliases/readiness, preset capabilities, active tasks and context_digest.
This does not create a chat, analyze media or spend credits.

### POST /api/content/tasks
Required: workspace_id, request_id, product_id, items. Optional brief contains
only public requirements. Each item has key, content_type and optional
template_code, direction, format. Use the exact supported preset, count and shape.
Returns `202 {"request_state":"accepted","request_id":"example_001","task_id":null,"next_poll_after_ms":3000}`.
No model routing, preflight download or waiting happens in this HTTP request.

### POST /api/content/tasks/:task_id/operations
Required: workspace_id, request_id, operation, item_ids, expected_task_revision,
expected_revisions. operation is revise/resume/render. revise takes an explicit
patch; resume/render cannot change requirements. unit_selector identifies one
image/card/frame/text unit. preview_approval must be the server-returned binding.
This returns the same asynchronous request receipt as creation.

### GET /api/content/requests/:request_id
Read the original request after timeouts. States below distinguish preparation,
confirmation and application. When a native task exists the response embeds task.
Reads never create messages/jobs, retry providers, or spend/refund credits.

### GET /api/content/tasks/:task_id
Returns task_revision, task_state, items, previews/artifacts, delivery_complete,
and next_actions. Only current native delivery evidence can count as complete.
Applied requests, queued jobs, scripts and first frames do not prove delivery.
The billing summary separates charged_credits, refunded_credits, net_credits,
wallet debits, included entitlement and remaining_quote_credits; charge identities
stay private and reused stages are counted once. prepared echoes the normalized
public request and selected preset. For partial slides, artifacts contains current
partial cards and next_actions supplies render with exact versions;
previous_previews contains historical displayed content.

Errors are `{error:{code,message,retryable,details},next_actions}`. For 409 refresh
versions and verify the target before a new confirmed request. For enqueue_failed
or timeout read the same request ID, then retry its identical payload if absent.
For submission_unknown inspect the saved task; never issue a new paid submission
blindly. requires_planning requires explaining unsupported requirements before
optional CMO consultation. Native generation credits and refunds are unchanged;
this path does not charge a CMO chat turn. It does not publish content.

<!-- direct-content-contract -->
```json
{
  "schema_version": 1,
  "workspace_required": true,
  "request_states": [
    "accepted",
    "preparing",
    "confirmation_required",
    "queued",
    "applied",
    "blocked",
    "failed",
    "canceled"
  ],
  "task_states": [
    "draft",
    "queued",
    "running",
    "waiting_review",
    "blocked",
    "failed",
    "completed",
    "paused",
    "canceled",
    "unknown"
  ],
  "error_codes": [
    "invalid_request",
    "workspace_not_found",
    "target_not_found",
    "stale_revision",
    "conflicting_request",
    "capability_unavailable",
    "requires_planning",
    "material_required",
    "insufficient_balance",
    "enqueue_failed",
    "generation_failed",
    "submission_unknown"
  ],
  "tools": [
    {
      "name": "autowhisper_context",
      "method": "GET",
      "path": "/api/content/context",
      "required": [
        "workspace_id",
        "product_id"
      ]
    },
    {
      "name": "autowhisper_create_content",
      "method": "POST",
      "path": "/api/content/tasks",
      "required": [
        "workspace_id",
        "request_id",
        "product_id",
        "items"
      ]
    },
    {
      "name": "autowhisper_update_task",
      "method": "POST",
      "path": "/api/content/tasks/:task_id/operations",
      "required": [
        "workspace_id",
        "request_id",
        "task_id",
        "operation",
        "item_ids",
        "expected_task_revision",
        "expected_revisions"
      ]
    },
    {
      "name": "autowhisper_task",
      "method": "GET",
      "path": "/api/content/requests/:request_id|/api/content/tasks/:task_id",
      "required": [
        "workspace_id"
      ]
    }
  ]
}
```

## Fast read-only endpoints

Use these for simple facts instead of `/api/cmo/message`; they are synchronous
and do not spend an LLM turn.

### GET /api/products/summary
Returns account-level product counts plus counts by active workspace.
- `200 {"account":{"workspaces_count":2,"active_products_count":12,"archived_products_count":1,"total_products_count":13},"current_workspace":{...},"workspaces":[...]}`
- `401` invalid/missing token

### GET /api/products
Lists products in **ONE workspace** — the user's current one unless
`workspace_id` says otherwise. It does **not** span the account; for
account-wide totals and the list of workspace ids use `/api/products/summary`.
Query params: `workspace_id` (optional int), `include_archived` (optional
bool), `limit` (optional int).
- `200 {"scope":"workspace","count":12,"returned":12,"products":[{"id":1,"name":"...","product_type":"digital","workspace_name":"...","archived":false,"has_main_image":true}]}`
- `401` invalid/missing token · `404` inaccessible workspace

### GET /api/cmo/status
Returns a compact status snapshot for the user's **current workspace**: product
counts, feed status counts, platform connection counts, automation settings —
plus the account-level wallet and a `workspaces` directory listing every active
workspace with its id and a `current` flag.
**Call this first.** Every other read endpoint defaults to the current workspace
and does not span the others, so the directory is how you learn what else exists
and which id to pass.
- `200 {"products":{"active_count":12,"archived_count":1,"total_count":13},"feed":{"pending":2},"platforms":{"connected_count":4},"wallet":{"formatted_balance":"9 tokens"},"settings":{...}}`
- `401` invalid/missing token

### GET /api/cmo/feed
Lists CMO Feed items without a chat turn.
Query params: `status` (`pending` default, or `approved`/`rejected`/
`dismissed`/`executed`/`all`), `workspace_id` (optional int), `limit`
(optional int).
- `200 {"status":"pending","counts":{"pending":2,"approved":1},"feed_items":[{"id":1,"status":"pending","feedable":{"type":"SocialCopy","id":4,"title":"...","product_name":"..."},"available_actions":[{"tool":"approve_feed_item","args":{"feed_item_id":1},"confirmation_required":true},{"tool":"regenerate_content","args":{"content_type":"social_copy","content_id":4},"confirmation_required":true}]}]}`
- `401` invalid/missing token · `404` inaccessible workspace · `422` invalid status

Scoped to the user's **current workspace** unless `workspace_id` names another
one — it never spans the account. Note the two ids on each row:
`id` is the feed item (for the `actions` endpoint), `feedable.id` is the content
(for the content `PATCH`). See the warning under that endpoint.

### GET /api/posts
Lists the delivery queue for **ONE workspace** — the user's current one unless
`workspace_id` says otherwise (same scope rule as `/api/cmo/feed`).
Query params: `status` (optional `draft`/`scheduled`/`publishing`/`published`/
`failed`), `workspace_id` (optional int), `limit` (optional int).
- `200 {"scope":"workspace","workspace":{"id":1,"name":"..."},"posts":[{"id":9,"status":"scheduled","scheduled_at":"...","workspace":{"id":1,"name":"..."},"platform":{"type":"linkedin"},"content":{"type":"SocialCopy","id":4,"title":"..."},"failure":null}]}`
- `404` inaccessible workspace · `422` invalid status

**Failed posts** carry a `failure` block — read it before deciding what to do:
- `{"reason":"<platform's real message>","needs_reconnect":false,"retry_count":1}`
- `needs_reconnect: true` → only the human can fix it (re-run OAuth);
  `retry_post` will keep failing. Otherwise `retry_post` is worth one attempt; if
  `reason` points at the content itself, edit it first, then retry.

### GET /api/wallet
Returns the token owner's available credits.
- `200 {"balance":9.0,"formatted_balance":"9 credits","currency":"credits"}`

### GET /api/platforms
Lists connected destinations and connection health for **ONE workspace** — the
user's current one unless `workspace_id` says otherwise. It agrees with
`/api/cmo/status`'s platform counts because both are now scoped the same way.
(Before 2026-08-09 this endpoint spanned every workspace while `status` reported
a single `current_workspace` — same response, two scopes.) Each row still names
its workspace so the caller can see which one it got.
Query params: `workspace_id` (optional int).
- `200 {"scope":"workspace","workspace":{"id":1,"name":"..."},"platforms":[{"id":2,"workspace":{"id":1,"name":"..."},"type":"linkedin","connected":true,"needs_reconnect":false,"auto_publishable":true}]}`
- `404` inaccessible workspace

### GET /api/performance
Cross-channel results for ONE workspace — the only endpoint that answers "did any
of this work?" rather than "what did we make?". Shipped 2026-09-01; add it to any
answer about which creative to fund, scale or stop.

Params: optional `workspace_id` (omit = current workspace, others NOT included),
optional `window_days` (server clamps to its supported range; has a default).

Returns `{scope, workspace_id, period:{from,to}, layers, layer_sources,
by_channel, ad_spend_cents}`.
- `layers` is the four-layer funnel; `layer_sources` says where each number came
  from, so you can tell a measured figure from a derived one.
- `by_channel` breaks the same window down per platform.
- ⚠️ `ad_spend_cents` is **`null`, not `0`, when the account has no active
  workspace**. `null` means we cannot answer; `0` asserts nothing was spent.
  Never render one as the other — that invents a fact about the owner's budget.

## Direct deterministic actions

### POST /api/cmo/actions/:tool
Run an explicit action without an LLM chat turn. Supported `:tool` values:
- `select_content_menu` — select a native draft menu; no generation or charge. Explicit production requests use direct content capabilities above.
`approve_feed_item`, `reject_feed_item`, `dismiss_feed_item`,
`publish_content`, `regenerate_content`, `reschedule_post`, `retry_post`,
`mark_as_published`, `boost_post`.

> **The live list is `direct_action_tools` in `GET /api/contract`, with each
> tool's `confirmation_required`.** This section is a copy for reading, and a
> copy drifts: `boost_post` shipped on the server 2026-08-28 and was missing
> here until 2026-09-21, so agents were told about eight tools when there were
> nine. Read the contract when it matters; trust this list only for orientation.

Form params are the corresponding ids (`feed_item_id` or `post_id`), plus
`scheduled_at` for rescheduling and optional `reason` for rejection.

`regenerate_content` is the exception: it addresses the CONTENT, not the card,
so it takes `content_type` (snake_case: `social_copy` / `lookbook` /
`feature_poster` / `idea`) and `content_id` — optionally `reference_url` and
`template_code`. It rewrites the draft in place, keeping the same record id,
and is the same action as the Revise button on the web feed card. Do not reach
for `PATCH /api/cmo/content/...` for this: that endpoint overwrites the fields
you give it verbatim and regenerates nothing.

It spends credits, so it always returns `202 confirmation_required` on this
endpoint — confirm it like any other. That is deliberate and unconditional: the
owner should see what a rewrite costs before it runs, and it must not depend on
what they last happened to type in the web chat.

High-impact actions still obey CMO policy and return a confirmation instead of
executing immediately:
- `202 {"confirmation_required":true,"message_id":123}` → call
  `POST /api/cmo/confirm` with that id.
- `200 {"success":true,"message":"...","receipt_text":"..."}` → action completed.

**When both are present, tell the owner `receipt_text`, not `message`.** The
server computes `receipt_text` from what actually happened and writes it for a
human to read; `message` is written for the model and may be the generic one.
Server-side since 2026-09-13, after a fixed lookup table was found overwriting
the computed receipt — "queued for sending" was reported even when zero ad
channels accepted the piece. Fixed wording is not evidence of a result. The
field name is published as `receipt_field` in `GET /api/contract`.

⚠️ `receipt_text` is in the OWNER's language. It does not replace checking
`scheduled` — `scheduled: 0` means the piece went nowhere, and that is the one
fact you must state plainly whatever language the receipt is in.

### PATCH /api/cmo/content/:content_type/:content_id
Edits exact fields without a generation run or credit charge. `content_type` is
one of `social_copy`, `lookbook`, `feature_poster`, `idea`.

⚠️ `:content_id` is `feed_items[].feedable.id`, **not** `feed_items[].id`, and
`:content_type` is the snake_case form of `feedable.type` (`SocialCopy` →
`social_copy`). Passing the feed item id is the usual cause of a `422`
"not found". Works on content in any of the token owner's active workspaces.

Form params: any of `title`, `body`, `hook`, `cta`, `tone`, `keywords[]`, and
optional `workspace_id`.
- `200 {"success":true,"updated_fields":["title","content"],"message":"..."}`
- `422` invalid or inaccessible content/fields

## POST /api/cmo/message
Send the CMO an instruction. Async — returns immediately.
Form params: `message` (required), `product_id` (optional int),
`workspace_id` (optional int).
- `202 {"status":"accepted","message_id":123}`
- `401` invalid/missing token · `422` blank message

## GET /api/cmo/messages/:id
Poll the turn started by the given user `message_id`.
Query params: `workspace_id` — **pass the same one you sent the message with.**
This endpoint is workspace-scoped; omitting it falls back to your first active
workspace and 404s on a turn that is running fine in another one.

- `200 {"done":false,"messages":[]}` — still working
- `200 {"done":true,"messages":[{"message_id":9,"role":"assistant","content":"...","message_kind":null,"pending_action":null,"actions":[...],"tool_calls":[...],"cards":{...}}]}`
- `404 {"error":"not found","hint":"This message may live in another workspace…"}` —
  **most often a missing `workspace_id`**, not a bad id.
- A message with `"message_kind":"confirm_required"` and a `pending_action`
  `{ "tool":"...", "args":{...} }` requires a confirm — see `POST /api/cmo/confirm` below.

Poll every ~3s. Most turns complete in a few seconds, but grounded ad advice
(`recommend_targeting`, which runs a live web search) has been measured at
**over two minutes** in production — poll for up to **3 minutes** before
giving up, and never re-send (that starts a second, separately charged turn
instead of resuming the first one). (Generation of media runs in the
background and lands in the user's Feed — `done:true` means the CMO's reply
is ready, not that a video finished rendering.)

### `actions[]` — clickable cards only
`actions[]` holds **clickable cards**, one shape only:
`{"label":"…","url":"https://cdn.autowhisper.xyz/…","style":"secondary"}` — media
links and connect links. The reply text never inlines raw URLs, so this is where
you read `actions[].url` for a piece of content's image/video URL.

`actions[]` used to also carry the tool-call log, and the two collided: they were
stored under two metadata keys that serialised to the same jsonb column (a symbol
key for the log, a string key for the cards), so the card write silently discarded
the log on any turn that also produced cards. As of the 2026-08-23 fix the log has
its own field — see `tool_calls[]` below — so `actions[]` no longer collides with
anything and can be trusted to hold cards only. **Messages sent before this fix may
still show the old mixed shape**: some `actions[]` entries on those older rows are
tool-log rows with no `label`/`url`/`style`, and those rows have no `tool_calls[]`
at all.

### `tool_calls[]` — the tool-call log
`tool_calls[]` holds what the CMO actually ran this turn:
`{"tool":"recommend_targeting","args":{…},"result":{…}}` per hop, in call order.
This is the reliable place to read a tool's raw return value — e.g.
`approve_feed_item`'s `result.scheduled` (how many platforms a piece actually went
to; `0` means nowhere). Only present on messages sent after the 2026-08-23 fix;
absent on older rows (see the note above).

### `cards` — the substance the prose deliberately omits, and unaffected by the above
The CMO lifts certain tool results into finished cards and is instructed **not to repeat
them in its prose**. `cards` uses its own separate metadata keys, so it does not
collide with anything and is the reliable place to read a lifted payload from.
Present keys (any may be absent):
- `targeting_advice` → `{"advice": "<full ad plan, markdown>", "heading": "…"}`
- `activation_guidance` → `{"guidance": "<next-steps funnel>", "heading": "…", "ad_plan_cta": {"label": "…", "message": "…"}}` —
  `ad_plan_cta` is present only once the user has a social platform connected. It's a
  one-click "get your ad plan" affordance: show `ad_plan_cta.label` as a button, and
  if clicked, send `ad_plan_cta.message` verbatim as the next `POST /api/cmo/message`.
- `inquiry_opener` → `{"message": "…", "paste_hint": "…", "share_url": "…"}`

`cards` is `null` when the turn lifted none. **If you relay only `content`, these are lost.**

## POST /api/cmo/confirm
Resolve a `confirm_required` bubble.
Form params: `message_id`, `decision` (`yes`|`no`), **`workspace_id`** (same as the turn —
omitting it 404s, as with polling).
- `200 {"ok":true,"decision":"yes","result":{…}}` — `result` is the tool's own return value;
  for `approve_feed_item` it carries `scheduled` (how many platforms it went to; `0` = nowhere),
  and `receipt_text` when the tool wrote one — prefer it over `message` exactly as on the
  direct-action path above, so the two paths never say different things about the same result
- `200 {"ok":true,"decision":"no"}` — declined, no `result`
- `404 {"error":"not found","hint":"…"}` unknown, **or a missing `workspace_id`**
- `422` not a confirm bubble / bad decision · `410` already resolved

## Notes
- Rate limited; back off on `429`.
- New accounts get free credits; generation consumes credits.
- Publishing requires at least one connected platform (one-time OAuth).
