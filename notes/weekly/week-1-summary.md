# Week 1 学习总结 · AI × Web3 共学营

> 学号 3553 · beautifulremi · 2026-05-19
> 公开版,可作为 Mirror / X / Medium 发布的草稿

---

## TL;DR

这周把 AI 和 Web3 两边的"最小可用心智模型"建立起来,然后把它们摆在同一条任务链上。最大的收获不是某个具体技术,而是:**两边都把"不确定性"和"权限边界"放在第一位**,只是切入角度不同 —— AI 是从模型输出的不可信切入,Web3 是从私钥与合约不可逆切入。把两条边界放在一起设计,就是 AI × Web3 真正的工程问题。

---

## 一、AI 侧:从 LLM 走到 Agent

**LLM 是函数,不是数据库**。这个心智一旦立起来,后面的设计都会朝可控方向走:
- Prompt 是上下文的"全部参数",不是命令
- Workflow 把路径写死,Agent 让模型动态决策 — 大多数生产系统其实是 Workflow
- Tool Use 让模型"说话变做事",但执行权永远在程序
- Context Window 不等于记忆,信息越塞越容易迷路 (lost in the middle)
- MCP 把工具暴露标准化,让"一次写、多客户端用"成为可能

**最有破坏力的常见误区**(我自己也踩过):
- 把 LLM 当查询接口 → 它给的是"最可能的下一句",不是检索
- 把所有 LLM 应用叫 Agent → 90% 是 Workflow,更稳更便宜
- 以为大窗口越大越好 → 信息越多,中间衰减越明显
- 把"加一句别幻觉"当 prompt engineering → 只有结构、示例、工具有用

## 二、Web3 侧:从私钥走到合约

Web3 的核心是把"信任"从中介搬到协议。**钱包不是账号,账户不是地址,签名不是登录**:
- 钱包是密钥管理 + 签名工具,资产记录在链上
- EOA 由私钥控制,合约账户由部署字节码控制
- 助记词 → 私钥 → 公钥 → 地址 是单向链路,永远不能反推
- 签消息(EIP-712)同样能掏空账户 — 盲签是最大攻击面
- 失败的交易也消耗 gas,L2 gas 结构与 L1 完全不同
- 合约一旦部署不可热更新,bug 上线即资产风险
- 测试网"跑通" ≠ 主网可上线,后者还要面对 MEV、流动性、攻击者动机

**让我对设计更谨慎的点**:私钥不是"账号密码",它是直接控制权;签消息不是"点个确认",它可能授权 Permit、转账、approve;合约 owner 不是后台管理员,它是单点失败。

## 三、AI Agent + Web3 写动作的真正难点

把两条认知合在一起,AI × Web3 的工程核心问题是:**让 AI 主导计划,让人 + 协议主导执行**。

我画的[最小交叉流程图](../../diagrams/png/ai-x-web3-min-cross-flow.png)分五层:
1. **计划层 (AI 主导)** — 解析意图、生成 step + 风险标签
2. **复核层 (人 + Guardrails)** — 高风险写入强制人工 review
3. **执行层 (智能账户 + 链)** — Session Key + 限额 + 白名单合约
4. **验证层 (链上 + 链下)** — tx hash / events / state 与预期比对
5. **可观测层 (横切)** — Trace 日志、告警、成功率/gas/延迟

**关键设计原则**:
- 读链可以自动 → AI 自主完成
- 写链不能自动 → AI 只生成 calldata,广播由人
- 签名必须人工 → 私钥绝不进 Agent 进程内存
- 每一步都留痕 → 失败比成功更重要,设计时不要假设成功路径

**账户分层心智模型**:
- **Safe** 当"金库与策略层"
- **ERC-4337 智能账户** 当"Agent 执行账户"
- **Session Key** 当"具体任务的钥匙串"
- **EOA** 退化为签名工具
- 这套分层让"AI 自动上链"既敢用、也可控

## 四、本周我做的具体事(可验证)

| # | 类别 | 产物 | 链接 |
|---|---|---|---|
| 1 | 仓库 | 公开 GitHub repo,8 个子目录,标准结构 | [github.com/beautifulrem/ai-x-web3-school](https://github.com/beautifulrem/ai-x-web3-school) |
| 2 | AI 卡片 | 8 张概念卡片(LLM → MCP) | `notes/concepts/ai-concept-cards.md` |
| 3 | Web3 卡片 | 8 张概念卡片(钱包 → 测试网) | `notes/concepts/web3-concept-cards.md` |
| 4 | 账户对比 | EOA / ERC-4337 / Safe 对照表 + AI Agent 视角总结 | `notes/concepts/account-comparison-...md` |
| 5 | 合约 | `HelloWeek1.sol` 最小合约 + 5 个单测全过 | `contracts/src/HelloWeek1.sol` |
| 6 | 流程图 | AI × Web3 五层交叉流程图(Mermaid → PNG) | `diagrams/png/ai-x-web3-min-cross-flow.png` |
| 7 | 可交互产物 | 单文件 HTML Concept Quiz,10 题 | `demos/concept-quiz/index.html` |
| 8 | 受限助手 | guardrails + 演示 helper,绝不广播 | `demos/restricted-web3-helper/` |
| 9 | 项目拆解 | Virtuals Protocol + Bittensor 深拆 | `notes/industry/project-teardown-week1.md` |
| 10 | 行业流 | 三层关注清单 + 信息卫生 | `resources/follow-list.md` |

## 五、坦诚的边界与"没做到"

- **Sepolia 部署 / 测试网交易**:写好了 forge 脚本和测试钱包,但 Sepolia faucet 域名要 Claude 浏览器权限,且大多 faucet 要 Google/Alchemy 登录,**这一步要在 Week 2 前手动跑完一次**。代码全部就绪,缺的只是 0.05 SepoliaETH
- **AI 微调实验**:Week 1 没碰,目前更想先把"工具链 + 权限边界"立稳,微调留到能讲清楚"为什么不只 prompt"那一刻
- **直播参与**:5/17 开营和 5/18 两场直播错过了实时窗口,后续走"看回放 + 笔记"路径
- **X 发起点 / 加入社群**:平台账号操作需要在课程指定的 Discord/X 上做,这部分要离开 Claude 的自动化范围,人手做

## 六、给自己的 Week 2 三个问题

1. **当 AI Agent 真的拿到 Session Key 之后,什么样的限额 / 白名单组合既不过紧也不过松?** —— 想找个真实场景做 spec
2. **"AI 输出 → 链上验证"的 Evaluator Agent 怎么自己被信任?** —— Virtuals 用声誉 + 经济,Bittensor 用 Yuma 共识,我想搞清楚两者本质差异
3. **能不能把 `restricted-web3-helper` 接成 MCP server,让 Claude Code 直接调用?** —— Week 2 第一个动手任务

## 致谢与立场

- 课程方 ETHPanda × LXDAO,把 AI × Web3 学起来的门槛压到了"两边各 1 周共学营"
- Claude Code (Opus 4.7) 作为本周主工具,凡是它代我做的事,我在 `logs/learning-agent-setup.md` 记录了**它做了什么**、**我精修了什么**、**哪些输出我没采纳**
- 所有概念解释优先官方文档(Anthropic Docs / Ethereum.org / EIP),二手解读不入仓库
- 私钥、助记词、API Key 永远不写进 git
