# AutoWhisper Skill

[English](README.md) · [简体中文](README.zh-CN.md)

**把产品交给你常用的 Agent，一起完成营销内容。**
AutoWhisper 根据产品事实与素材制作 UGC 视频、图片和社交文案。这个 Skill 教 Agent 按网页工作台相同的创作、预览、审核与发布流程协作，复用你的账号、任务和积分。

[连接 Agent，开始使用 AutoWhisper](https://autowhisper.xyz/zh/skill?utm_source=github&utm_medium=readme&utm_campaign=agent_integrations&utm_content=skill_intro) · [MCP 服务](https://github.com/Qumge/autowhisper-mcp/blob/main/README.zh-CN.md)

## 可以这样用

> “把这个产品网址加入工作区，先准备内容方案，不要渲染或发布。”
>
> “给这个产品做一条 UGC 视频，使用产品素材，先让我看预览和预计费用。”
>
> “修改这条草稿的开头，产品和语言都保持原样。”
>
> “看看这个工作区待审核的内容、发布失败的帖子，以及已发布内容的表现。”

明确且受支持的创作要求直接进入原生内容工具；查事实走读取接口；营销策略和不明确的创意才交给 CMO 咨询。不需要每次操作都多开一次 CMO 对话。

## 快速开始

### Claude Code：一起安装 Skill 和 MCP

```text
/plugin marketplace add Qumge/autowhisper-skill
/plugin install autowhisper@autowhisper
```

安装工作流说明和远程 MCP 连接后，打开 `/mcp`，选择 AutoWhisper，在 AutoWhisper 授权页面认证。需要有 AutoWhisper 账号，不必把 token 贴进聊天。

### 其他支持 Skill 的 Agent

```bash
npx skills add Qumge/autowhisper-skill
```

Agent 读取 [SKILL.md](SKILL.md)，需要认证时启动现有设备授权流程。你只需打开返回的链接并批准；token 保存在本机 `~/.config/autowhisper/credentials.json`，与本地 MCP 共用。HTTP 示例需要 `curl` 和 `jq`。

已经在用兼容的远程 MCP 客户端？在连接器设置中添加 `https://autowhisper.xyz/mcp`。本地 stdio 配置见 [AutoWhisper MCP](https://github.com/Qumge/autowhisper-mcp)。不必重复安装：MCP 提供工具，Skill 提供流程说明，可单用，也可配合使用。

## 第一次完成一条内容

1. 授权账号，选择工作区和产品。
2. 给产品网址，或使用已有的产品事实与素材。
3. 请求一条内容，检查脚本、图片或视频预览与费用。
4. 在你授权的范围内继续渲染或发布；发布需要已连接的兼容平台账号。
5. 查看已保存的任务和交付状态，再看帖子的实际表现。

具体内容能力以服务端和账号返回的可用范围为准，装好 Skill 不代表某个受开关控制的功能已经启用。连接授权本身也不等于允许今后所有扣费和发布。

## 使用前知道这些

- 生成和 CMO 咨询可能使用 AutoWhisper 积分；预计费用、实际扣费、退款和套餐用量分别查看，余额见[积分钱包](https://autowhisper.xyz/zh/wallet)。
- 收到请求、写好脚本、生成首帧都不等于视频完成，按保存的任务状态和 `delivery_complete` 判断。
- 批准按内容就绪状态执行：未完成内容开始／继续付费制作，成品的发布动作才进入帖子与广告发送流程。读取回执与各自结果；帖子排期为零不代表没有连接平台。
- 响应不确定时先按原请求／消息 ID 恢复，避免重复制作和重复扣费。
- 发布不保证流量或销售；竞品研究通过 CMO 咨询提供，只有任务返回来源证据才能说本次做过。

Starter 入门价为 **$30/月**。可选的每日自动运行取决于你的开关设置与可用积分，不要求 Pro；积分不足以覆盖所选整轮时，整轮暂停。入门价格不承诺包办完整每日产量，执行前按报价、套餐用量和钱包确认。

授权每日自动运行后，账号未归档工作区中合格产品的新每日内容会在就绪后自动批准、排期，并到时发布到已连接的社交渠道。历史内容和手工草稿仍按各自的审核、制作与发布步骤处理。每日广告独立提交到已连接的广告账号，并请求暂停交接；只有已保存的平台状态或原生反馈确认暂停后，才能说“已暂停，等你启动”。若暂停失败或未确认，必须明确提示广告可能正在投放或花费，并展示原生回执和返回的平台操作链接，便于检查或暂停。缺少设置或平台拒绝会继续显示。

这套 Skill 复用 AutoWhisper 现有服务，没有另建内容或计费系统。开源包的安装与托管生成服务的使用分别计算。

## 文档入口

| 用途 | 文档 |
| --- | --- |
| Agent 工作流和授权规则 | [SKILL.md](SKILL.md) |
| API、工作区范围和任务合同 | [API 参考](references/api-reference.md) |
| 完整创建、修改和渲染请求 | [成品查找、直接创作与素材批次示例](references/direct-content-examples.md) |
| 营销策略咨询 | [CMO 手册](references/cmo-playbook.md) |
| MCP 连接与工具 | [AutoWhisper MCP](https://github.com/Qumge/autowhisper-mcp/blob/main/README.zh-CN.md) |

[带上你的产品，开始使用 AutoWhisper](https://autowhisper.xyz/zh/skill?utm_source=github&utm_medium=readme&utm_campaign=agent_integrations&utm_content=skill_footer)

## 维护者检查

在仓库根目录，使用已从 Rails 导出的本地合同：

```bash
bash scripts/check-api-contract.sh /absolute/path/to/agent_content_contract.json
bash scripts/test-direct-content-contract.sh /absolute/path/to/agent_content_contract.json
python3 scripts/test-direct-content-examples.py /absolute/path/to/agent_content_contract.json
```

检查文档范围、请求合同，并使用本地 stub 验证示例；不会真实生成或发布。生产可用性需单独检查。

## 许可证

MIT，见 [LICENSE](LICENSE)。托管服务按 AutoWhisper 账号条款和积分计费。
