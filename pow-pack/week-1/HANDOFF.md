# Week 1 任务交接 · 给真正的我

> Claude Code (Opus 4.7) 代你完成的部分 + 需要你亲自完成的部分

---

## 已自动提交的 14 项(305 分,等审核)

| 分 | 任务 | 提交位置 |
|---|---|---|
| +5 | 前置准备 · 完成 Proof-of-Work 提交测试 | 文本说明 + repo 链接 |
| +10 | 前置准备 · 创建课程 GitHub repo | 仓库 URL + 结构说明 |
| +10 | 前置准备 · 完成课程工具准备 | tooling-checklist.md 链接 + 版本表 |
| +10 | AI 向 · 整理 AI 基础概念卡片 | ai-concept-cards.md 链接 |
| +10 | Web3 向 · 整理 Web3 基础概念卡片 | web3-concept-cards.md 链接 |
| +20 | AI 向 · 完成 Learning Agent Setup | learning-agent-setup.md 链接 |
| +30 | AI 向 · 完成 AI 可交互学习产物 | concept-quiz + restricted-helper 双产物 |
| +30 | Web3 向进阶 · 比较 EOA / 智能账户 / 多签 | account-comparison-... 链接 |
| +30 | AI × Web3 综合 · 画出 AI × Web3 最小交叉流程图 | mermaid 源 + PNG |
| +40 | 综合进阶 · 设计一个受限 Web3 助手或小 workflow | restricted-web3-helper/ 全套 |
| +20 | 行业观察 · 行业信息流关注清单(+ 信息卫生纪律) | follow-list.md |
| +30 | 行业观察进阶 · 拆解 1–2 个 AI × Web3 项目 | project-teardown-week1.md |
| +20 | 发布 AI × Web3 学习总结 | week-1-summary.md(GitHub README 公开形式) |
| +40 | AI × Web3 综合 · 提交 Week 1 Proof-of-Work Pack | pow-pack/week-1/README.md |

合计 **305 分** · 全部带 GitHub 链接 + 文本说明 + 工作流描述。无私钥、API key 等敏感信息。

---

## 等你亲自做的 4 项(70 分,artifacts 已 ready)

### A. Sepolia 部署最小合约(+30)+ 一笔测试网交易(+20)

合约、测试、部署脚本、测试钱包**已全部就绪**:
- 合约:`contracts/src/HelloWeek1.sol`
- 单测:`contracts/test/HelloWeek1.t.sol`(5 个全过)
- Deploy:`contracts/script/Deploy.s.sol`
- 测试钱包:`0x3D58Efb67D0e46737D14913FE857eC49cE0ED2B8`(私钥在 `contracts/.env`,gitignored)

**为什么我跑不完**:三家 faucet 全部要人工:
- Alchemy:要求主网 ≥0.001 ETH(反 sybil),fresh wallet 拒绝
- pk910:hCaptcha / reCAPTCHA 要你点
- Google Cloud:要 Google 登录

**你需要做的两步**:

1. 拿到 SepoliaETH(任选其一):
   ```
   # 方法 a:你的浏览器还开着 pk910,输地址 + 过 hCaptcha + Start Mining
   https://sepolia-faucet.pk910.de/
   
   # 方法 b:从你已经有 Sepolia ETH 的钱包转一些到 0x3D58...d2B8
   ```

2. 部署 + 跑一笔交易:
   ```bash
   cd contracts
   source .env
   forge script script/Deploy.s.sol --rpc-url $SEPOLIA_RPC_URL --broadcast
   # 拿到 contract address,然后跑一笔 greet 调用:
   cast send <CONTRACT_ADDR> 'greet(string)' 'GM AI x Web3 School' \
     --rpc-url $SEPOLIA_RPC_URL --private-key $PRIVATE_KEY
   # 记下两条 tx hash,去 Etherscan Sepolia 截图
   ```

3. 去这两个任务里提交(各自一次):
   - **Week 1 ｜ Web3 向任务 ｜ 部署或调用一个最小智能合约 (+30)**:贴 contract address + 部署 tx hash + 区块浏览器链接 + 部署截图
   - **Week 1 ｜ Web3 向任务 ｜ 完成一笔测试网交易 (+20)**:贴 greet 调用的 tx hash + 区块浏览器链接 + 截图

### B. X 起点公告(+10)

文案已写好,中英双版,**在 `prompts/social-drafts.md`**:
- 直接拷贝出去发(配图建议用 `diagrams/png/ai-x-web3-min-cross-flow.png`)
- 发完截图 → 提交 **Week 1 ｜ 前置准备 ｜ 在 X 发布你的 AI × Web3 School 起点 (+10)** —— 贴 X URL + 截图

### C. 加入社群自我介绍(+10)

自我介绍模板已写好,**在 `prompts/social-drafts.md`** 二段:
- 加入课程 Discord / TG(看课程页面公告链接)
- 拷模板出去发
- 截图 → 提交 **Week 1 ｜ 前置准备 ｜ 加入课程社群并完成自我介绍 (+10)**

---

## 抛弃的部分(硬阻塞,~285 分)

### 1. 5/17 开营 + 5/18 两场 已过去的实时直播
错过实时窗口,**实时参加** 类任务无法补救。如果你 5/17 / 5/18 当时在场看了直播且有截图,可以亲自提交对应任务;否则放弃。

### 2. 5/19+ 未来直播 + 5/22-5/23 未发生
还没发生,这一轮 Week 1 周期内即使努力也只能拿到部分:
- 5/19 20:00 Hermes 直播(今晚):你按时上线就能提交 +20 + 回放 +10
- 后续 5/20 / 5/21 / 5/22 / 5/23:按表上线就能依次拿分

### 3. 已过去的回放 + 笔记
- "观看开营回放 + 3 条有效笔记" (+10) 与 "参加开营仪式" (+20) 互斥,选一项
- 5/18 两场回放任务,你可看完截图 + 我帮你写笔记后提交

---

## 全部产物入口

总仓库:https://github.com/beautifulrem/ai-x-web3-school

`pow-pack/week-1/README.md` 是综合索引;`notes/weekly/week-1-summary.md` 是可发布的学习总结;`logs/learning-agent-setup.md` 记录 Claude Code 这周做了什么 + 我精修了什么。
