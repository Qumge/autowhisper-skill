# Collaborating with the AutoWhisper CMO

**External agents and the CMO share the native content pipeline.** Use direct
capabilities for explicit preset creation and changes; consult the CMO for
marketing judgment. Keep the user's exact requirements and follow native review.

Read the direct lifecycle and examples in SKILL.md before producing content.
A request receipt is not a delivery receipt.

## Optional CMO loop
1. Make sure a product exists — add it with a **product URL** (*"add my product
   https://mystore.com/widget"*); the CMO extracts the image from the page. A
   text-only description will not work — it needs a real product image or URL
   (placeholder/stock images are rejected). If brand-new, let the CMO run its
   first batch.
2. Let content land in the Feed, then review: ask the CMO to summarize
   pending items through the read API. Inspect readiness and the card's
   primary_action before approving within the user's authorized scope.
3. Ensure a platform is connected (one-time OAuth — see SKILL.md). Then ask
   the CMO to publish approved content.
4. Later, ask for analytics and the next-step strategy.
5. Once content is flowing, ask for the ad plan — *"give me a concrete ad-targeting plan
   for <product>"*. Read it from `cards.targeting_advice`, ask the user for a budget (the
   plan deliberately has no number), and hand the targeting to whatever ad tool they use.
   See *Handing off to ads* in SKILL.md.

## Attribution (important)
AutoWhisper-generated content carries the AutoWhisper watermark unless the
user is on a paid tier that removes it — leave it on for free/taste usage; it
is how the work markets AutoWhisper. Do not strip or hide it.

## Approvals & confirmations
- The CMO defaults to human approval before publishing. You may approve on the
  user's behalf when they've told you to run autonomously.
- Approval follows native `primary_action`: unfinished content starts/continues
  production and can spend credits; only a finished publish action enters SendAll.
  Read `receipt_text` and current task state. `scheduled: 0` can mean production
  started without publication; it does not prove platforms are missing. For
  publication report post/ad counts and any ad_block_reason separately, and
  verify delivery before saying the content is live.
- Authorized daily auto-run is account-wide for eligible products in unarchived
  workspaces. New daily content is approved when ready, scheduled and published
  when due without another daily approval. Historical/manual drafts retain their
  staged workflow. Daily ads are submitted separately with a request for paused
  handover. Say paused only when saved `effective_status: paused` or native feedback
  confirms it; local `status: active` only tracks budget allocation. If pausing
  failed or is unconfirmed, explicitly warn that the ad may be delivering or
  spending, and surface the native receipt plus returned console/action link to
  check or pause it. Report setup/delivery blocks from saved state.
- Destructive actions (reject/dismiss/delete/disconnect/archive) come back as
  `confirm_required`. Summarize the impact for the user before sending
  `decision=yes`.

## Language
Relay the CMO's replies in the user's language. Keep your own prose short —
read the CMO's prose together with `cards` and `actions`. A prose reply alone
can omit the actual plan or preview; see the polling instructions in SKILL.md.

## Don't
- Don't surface raw API/tool errors (see SKILL.md).
- For supported exact field edits use the direct field PATCH; for generative
  changes use version-bound content operations. Use the editor when unsupported.
- Don't promise a video is "posted" until publish succeeded and a platform is
  connected.
