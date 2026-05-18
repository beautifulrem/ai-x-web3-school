# Week 1 · Proof-of-Work Pack

> 学号 3553 · beautifulremi · 2026-05-19
> 一份 Week 1 综合 Proof-of-Work 索引,作为课程任务"Week 1 Proof-of-Work Pack (+40)"的提交。

---

## Quick Links

| 凭证 | 入口 |
|---|---|
| GitHub Repo | https://github.com/beautifulrem/ai-x-web3-school |
| 学习总结(可发布) | [`notes/weekly/week-1-summary.md`](../../notes/weekly/week-1-summary.md) |
| AI × Web3 流程图 | [`diagrams/png/ai-x-web3-min-cross-flow.png`](../../diagrams/png/ai-x-web3-min-cross-flow.png) |
| 可交互 Quiz | [`demos/concept-quiz/index.html`](../../demos/concept-quiz/index.html)(本地跑 `python3 -m http.server`) |
| Restricted Web3 Helper | [`demos/restricted-web3-helper/`](../../demos/restricted-web3-helper/) |

---

## 一、AI 向产物

| 项 | 路径 | 说明 |
|---|---|---|
| AI 概念卡片 × 8 | [`notes/concepts/ai-concept-cards.md`](../../notes/concepts/ai-concept-cards.md) | LLM / Prompt / Workflow / Agent / Tool Use / AI Coding / Context Window / MCP |
| Learning Agent Setup | [`logs/learning-agent-setup.md`](../../logs/learning-agent-setup.md) | Claude Code 选型、MCP 接入、SubAgent 使用记录 |
| Concept Quiz (HTML) | [`demos/concept-quiz/index.html`](../../demos/concept-quiz/index.html) | 单文件 vanilla JS,10 题(5 AI + 5 Web3),答错有解释 |

## 二、Web3 向产物

| 项 | 路径 | 说明 |
|---|---|---|
| Web3 概念卡片 × 8 | [`notes/concepts/web3-concept-cards.md`](../../notes/concepts/web3-concept-cards.md) | 钱包 / 账户 / 助记词链 / 签名 / 交易 / Gas / 智能合约 / 测试网 |
| EOA vs 智能账户 vs 多签 | [`notes/concepts/account-comparison-eoa-smart-multisig.md`](../../notes/concepts/account-comparison-eoa-smart-multisig.md) | 6 维度对比 + AI Agent 视角的分层心智模型 |
| HelloWeek1 合约 + 5 单测 | [`contracts/src/HelloWeek1.sol`](../../contracts/src/HelloWeek1.sol) + [`contracts/test/HelloWeek1.t.sol`](../../contracts/test/HelloWeek1.t.sol) | Foundry,本地 `forge test` 全过 |
| Deploy 脚本 | [`contracts/script/Deploy.s.sol`](../../contracts/script/Deploy.s.sol) | 接 SEPOLIA_RPC_URL 即可一键部署 |
| Sepolia 测试钱包 | `0x3D58Efb67D0e46737D14913FE857eC49cE0ED2B8` | 仅测试网,私钥在 `.env`(gitignored) |

### Foundry 测试输出(本地验证)
```
Ran 5 tests for test/HelloWeek1.t.sol:HelloWeek1Test
[PASS] testAnyoneCanGreet() (gas: 47340)
[PASS] testEmptyGreetingReverts() (gas: 11029)
[PASS] testFuzz_GreetIncrementsCount(string,string) (runs: 256, μ: 79718, ~: 74440)
[PASS] testInitialState() (gas: 17883)
[PASS] testOnlyDeployerCanReset() (gas: 22044)
Suite result: ok. 5 passed; 0 failed; 0 skipped
```

### Sepolia 部署 / 交易 — 待 faucet 完成

钱包余额为 0 SepoliaETH,faucet 步骤被 CAPTCHA / 反 sybil 规则阻塞:
- Alchemy:要求主网 ≥ 0.001 ETH,fresh wallet 被拒
- pk910 PoW:reCAPTCHA 必须人工完成
- Google Cloud Sepolia:需 Google 登录

**下一步**:在浏览器里完成 pk910 reCAPTCHA → 等矿成 → `forge script script/Deploy.s.sol --rpc-url $SEPOLIA_RPC_URL --broadcast`。脚本 / wallet / 测试全部就绪,只差 ETH。

## 三、AI × Web3 综合产物

| 项 | 路径 | 说明 |
|---|---|---|
| 最小交叉流程图 | [`diagrams/png/ai-x-web3-min-cross-flow.png`](../../diagrams/png/ai-x-web3-min-cross-flow.png) | 五层 + 横切可观测;源在 [`diagrams/mermaid/...mmd`](../../diagrams/mermaid/ai-x-web3-min-cross-flow.mmd) |
| Restricted Web3 Helper | [`demos/restricted-web3-helper/`](../../demos/restricted-web3-helper/) | 设计文档 + `guardrails.py`(8 条 deny 规则,全部自检通过)+ `helper.py` 主循环 |
| 项目拆解 | [`notes/industry/project-teardown-week1.md`](../../notes/industry/project-teardown-week1.md) | Virtuals Protocol + Bittensor,各按 6 维度拆解,带官方源 |
| 行业关注清单 | [`resources/follow-list.md`](../../resources/follow-list.md) | 官方源 / X / 中文圈三层,加上信息卫生纪律 |
| Week 1 学习总结 | [`notes/weekly/week-1-summary.md`](../../notes/weekly/week-1-summary.md) | 可发 Mirror / X 长帖的版本 |

## 四、过程证据(可追溯)

| 凭证类型 | 位置 |
|---|---|
| Git 提交历史 | `git log --oneline` 在 [GitHub](https://github.com/beautifulrem/ai-x-web3-school/commits/main) |
| 工具版本 | [`notes/tooling-checklist.md`](../../notes/tooling-checklist.md)(forge 1.5.1 / cast / gh / Claude Code / RTK 0.39.0) |
| Agent 协作日志 | [`logs/learning-agent-setup.md`](../../logs/learning-agent-setup.md) |
| 截图证据 | `pow-pack/week-1/screenshots/` |

## 五、信息卫生 / 安全声明

- 私钥、助记词、API Key 永不入 git;`.gitignore` 覆盖 `.env`、keystore、mnemonic
- Sepolia 测试钱包 `0x3D58...d2B8` 独立于个人主钱包
- 笔记全部公开,但敏感信息(邮箱、生日、地理坐标)按需脱敏
- AI 生成内容均经人工精修,关键事实(EIP 编号、合约接口、版本号)经官方文档双校验

---

## 六、自评:这周达成 vs. 未达成

### ✅ 达成
- 仓库与工具链全部就绪
- AI / Web3 两侧概念体系建好,8 + 8 = 16 张卡片
- 合约写好、测试全过、部署脚本可一键跑
- 最小交叉流程图把"AI 输出 → 人工复核 → 链上执行 → 验证"显式画出来
- Restricted Helper 把"绝不自动广播"的约束写成可跑代码
- 两个真项目拆解(Virtuals / Bittensor)带源验证

### ⏸️ 待用户辅助
- Sepolia 部署 + 一笔测试网交易 → 阻塞在 faucet CAPTCHA / 反 sybil
- X 起点公告 → 文案已写,需用户自己账号发布
- 社群自我介绍 → 文案已写,需用户加群发布
- 实时直播参与 / 回放观看 → 截图证据需用户提供

### 🚫 抛弃(硬阻塞)
- 5/17 / 5/18 已过的实时直播:无法回到过去
- 5/19+ 未来的实时直播:还没发生

---

## 给课程的话

这个 PoW Pack 想强调一件事:**我的产出里既有"我做的",也有"AI 帮我做的我审核过的"**,两者都在 commit history 里可追溯。具体到这周,Claude Code (Opus 4.7) 协助产出了三份原始素材(AI 卡片 / Web3 卡片 / 项目拆解),然后我精修、加自己的判断、对接到具体上下文(账户分层、最小交叉流程图、受限 helper 设计)。这种"AI 起稿 + 人精修"的工作流是我对 Week 1 主题"AI Coding 与 Agent 协作"的真实回应。
