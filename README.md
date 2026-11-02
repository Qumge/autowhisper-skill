# AutoWhisper Skill

[English](README.md) · [简体中文](README.zh-CN.md)

**Give your agent a product. Work together on its marketing.**
AutoWhisper helps you turn product facts and materials into UGC videos, images and social posts. This Skill teaches your agent the same creative, preview, review and publishing workflow used in the AutoWhisper dashboard, with your existing account, tasks and credits.

[Connect your agent to AutoWhisper](https://autowhisper.xyz/en/skill?utm_source=github&utm_medium=readme&utm_campaign=agent_integrations&utm_content=skill_intro) · [MCP server](https://github.com/Qumge/autowhisper-mcp)

## What you can ask

> “Add this product URL to my workspace and prepare a content proposal. Don’t render or publish yet.”
>
> “Make one UGC video for this product. Use its materials and show me the preview and cost.”
>
> “Revise this draft’s opening line. Keep the product and language unchanged.”
>
> “Show pending reviews, failed posts and the results for this workspace.”

For supported explicit requests the agent uses direct native content tools; for facts it uses read endpoints; for marketing judgment it can consult the CMO. It does not need a CMO chat turn for every action.

## Quick start

### Claude Code: Skill + MCP together

```text
/plugin marketplace add Qumge/autowhisper-skill
/plugin install autowhisper@autowhisper
```

This adds the workflow instructions and the remote MCP connection. Open `/mcp`, select AutoWhisper and authenticate on the AutoWhisper approval page. You need an AutoWhisper account; no token needs to pass through chat.

### Other skill-capable agents

```bash
npx skills add Qumge/autowhisper-skill
```

The agent reads [SKILL.md](SKILL.md) and starts the existing device authorization flow when needed. Open the returned link and approve. The token is saved locally in `~/.config/autowhisper/credentials.json`, shared with the local MCP server. The HTTP examples require `curl` and `jq`.

Already use a compatible remote MCP client? Add `https://autowhisper.xyz/mcp` in that client’s connector settings. For a local stdio configuration, see [AutoWhisper MCP](https://github.com/Qumge/autowhisper-mcp). Installing both is optional: MCP provides tools, while the Skill provides workflow guidance.

## The first useful result

1. Connect your account and choose the workspace and product.
2. Give a product URL or use existing product facts and materials.
3. Ask for one creative. Review its script, images or video preview and cost.
4. Continue rendering or publish only within the scope you authorize. Publishing requires a compatible connected account.
5. Inspect saved task and delivery state, then check post results.

Content availability depends on the server-returned capabilities and your account. An installed Skill is not proof that a gated capability is enabled. Connection authorization does not by itself authorize all future spending or publishing.

## Before you start

- Generation and CMO consultation can use AutoWhisper credits. Quotes, actual charges, refunds and included usage are separate; see [your wallet](https://autowhisper.xyz/en/wallet).
- A request acknowledgment, script or first frame is not a finished video. Report completion only from saved task state and `delivery_complete`.
- Approving a feed card can trigger paid rendering and publishing. Read the returned actions and confirmation; don’t treat approval as a bookmark.
- An uncertain response must be recovered by its original request/message ID before retrying, avoiding duplicate work and charges.
- Publishing does not guarantee traffic or sales. Competitor research is available through CMO consultation and is only claimed when that task returns source evidence.

The Skill uses AutoWhisper’s existing service, not a separate content or billing system. Installing this open-source package is distinct from using hosted generation.

## Documentation

| Reader | Document |
| --- | --- |
| Agent workflow and authorization | [SKILL.md](SKILL.md) |
| API endpoints, workspace scope and task contract | [API reference](references/api-reference.md) |
| Complete direct-content examples | [Create, revise and render examples](references/direct-content-examples.md) |
| Marketing consultation | [CMO playbook](references/cmo-playbook.md) |
| MCP connection and tools | [AutoWhisper MCP](https://github.com/Qumge/autowhisper-mcp) |

[Start with your product on AutoWhisper](https://autowhisper.xyz/en/skill?utm_source=github&utm_medium=readme&utm_campaign=agent_integrations&utm_content=skill_footer)

## Maintainer checks

From the repository root, using a locally exported Rails contract:

```bash
bash scripts/check-api-contract.sh /absolute/path/to/agent_content_contract.json
bash scripts/test-direct-content-contract.sh /absolute/path/to/agent_content_contract.json
python3 scripts/test-direct-content-examples.py /absolute/path/to/agent_content_contract.json
```

These validate documentation scope, request contracts and examples against a local stub; they do not generate content or publish posts. Live availability is a separate check.

## License

MIT — see [LICENSE](LICENSE). Hosted service usage follows AutoWhisper’s account terms and credits.
