# 行业观察 · AI × Web3 项目拆解(Week 1)

> 拆 2 个项目:**Virtuals Protocol**(链上 AI Agent 商业基础设施) + **Bittensor / TAO**(去中心化 AI 商品市场)。
> 选取标准:有官方文档、有公开代码、有真实用户。剔除"纯叙事 token"。

---

## 一、Virtuals Protocol — 链上 AI Agent 的发行、商业与结算协议

### 1. 它解决什么问题
当一个 AI agent 想要"自己赚钱"、"自己付费雇佣别的 agent"、"自己拥有钱包",它需要的不是再一个 LLM,而是一套法律+金融+身份基础设施。Virtuals 做的就是这层:让每个 agent 有非托管钱包、有可被定价的代币、有可结算的合约接口。结果是 agent 之间能直接互相下单、付款、验收,不再依赖人类作为中间人。

### 2. 技术栈与关键设计
- **链 / 执行层**:主要部署在 Base(EVM L2),也支持 Solana 上的 agent 发射;ACP v2.0 已扩展为多链 EVM
- **AI 侧**:开源 SDK 有 `virtuals-python`、`acp-node`、`acp-python`,以及社区 fork 的 `openclaw-acp`(GitHub 上 stars 最多的库);agent 内部可自带任意模型与工具链
- **Web3 侧**:核心合约 `ACP Core` 部署在 Base Mainnet(`0x238E…32E0`),配套 `FundTransferHook`;每个 agent token 走 bonding curve 启动,达到 42,000 VIRTUAL 阈值后自动迁移到 Uniswap V2,LP 锁仓 10 年
- **账户模型**:每个 agent 持有非托管钱包 + 可选支付卡 + 邮箱,默认 restricted-mode 签名;消费侧 Butler 网关为每个用户钱包做地址聚合
- **数据 / 存储**:链上只存"协议事件"(Proof of Agreement、escrow、评估结果),具体推理与中间产物在链下,链上仅 commit 签名摘要

### 3. AI 与 Web3 怎么"真"结合
真正用 Web3 的点是 **agent-to-agent 商业的结算与争议解决**,而不是 token 本身。ACP 设计了 Request → Negotiation → Transaction → Evaluation 四阶段:Client agent 把钱打进合约 escrow,Provider agent 干完活,**Evaluator agent**(第三方,角色与 oracle 类似)对照签名过的 Proof of Agreement 判断是否达标,达标才放款。三方都是 agent,没有人类裁判 — 这只有用链上 escrow + 不可篡改协议历史才成立。如果换成中心化 API,evaluator 的判断本身没有公信力。Agent 代币化(bonding curve)那部分坦白说更像 launchpad,Web3 必要性弱一些,但 escrow + evaluator 是真需要链的。

### 4. 我能学到什么
- **escrow + evaluator 三角设计**:做 Week 2+ 的"AI 输出可验证"时,可以借用这个三角(委托方 / 执行方 / 验证方),把 LLM 不确定性问题转化为可仲裁的合约状态机
- **agent 身份 = 钱包 + 支付能力 + 合约调用权限**,不是 ENS 名字。要给 agent 设计身份就要把这三件事捆在一起,而且默认 restricted-mode 签名以限制 blast radius
- **Hook 化合约架构(ACP v2.0)**:从 memo-based 改成 hook-based,意味着合约把"业务规则"抽象成可插拔模块,这是给 agent 自主组合工作流留接口的关键

### 5. 风险与开放问题
- **Evaluator 本身怎么去信任?** 如果 evaluator 也是 agent,谁来评估 evaluator?目前看是声誉 + 经济激励,但没有 slashing,长期对抗性场景下未必稳
- **代币化 + 美国证券法**:bonding curve 启动 + 25% 团队随 FDV 解锁,这种结构在合规上仍然是模糊地带,可能影响 ACP 商业层能否被大型机构采用

### 6. 来源链接
- 官网 / 文档:https://whitepaper.virtuals.io/ ; LLM 全文:https://whitepaper.virtuals.io/llms-full.txt
- GitHub:https://github.com/Virtual-Protocol (含 `protocol-contracts` Solidity 仓,`acp-node` / `acp-python` SDK)
- ACP 标准提案:ERC-8183(协议在 v2.0 实现)

---

## 二、Bittensor (TAO) — 用代币激励竞争产出 AI 商品的去中心化网络

### 1. 它解决什么问题
训练和推理 AI 模型现在被几家公司垄断算力与数据。Bittensor 的赌注是:把"产出某种 AI 商品(文本补全、嵌入向量、语音、预测)"做成一个**有竞争性、有评分、有按质付费**的市场,谁的模型评分高谁拿更多 TAO。它不是托管模型的云,而是把"产出 AI 输出"这件事市场化、可结算化。

### 2. 技术栈与关键设计
- **链 / 执行层**:基于 Substrate 的自定义链 `subtensor`(Rust),独立链非 EVM;SDK 仓 `opentensor/bittensor` 99.8% 是 Python
- **AI 侧**:没有统一框架,每个 **subnet** 自己定义"什么是有用的工作"和"怎么评分"。Miner 跑模型产出,Validator 评分。模型本身完全自由(可以是 Llama 微调、Whisper、自训练的检索模型,任何东西)
- **Web3 侧**:核心是 **Yuma Consensus(及改进版 YC3)**,基于 validator 给 miner 的打分矩阵,在链上计算最终 TAO 释放分配。每个 subnet 是一个 AMM,有自己的 **alpha token** 与 TAO 储备,价格 = TAO_reserve / alpha_reserve(dTAO 机制)
- **账户模型**:链上账户为 SS58 格式(Substrate 标准),Miner / Validator 用 hotkey/coldkey 双密钥(coldkey 持有资金,hotkey 做日常签名)
- **数据 / 存储**:模型权重和推理流量完全在链下,链上只存评分、stake、emission 分配

### 3. AI 与 Web3 怎么"真"结合
真正用 Web3 的点是 **AI 商品的定价与激励分配**。在没有链的世界,你怎么决定"subnet 13 的嵌入模型比 subnet 19 好,应该多分配 23% 的算力补贴"?Bittensor 把这一步变成了链上算法 — validator 的评分上链,Yuma 共识聚合并自动产出 emission,无人能单方面修改。dTAO 又让用户**用质押 TAO 来"投票"哪个 subnet 值得更多 emission**,把市场对 AI 商品的需求和代币激励耦合起来。这是经典的"链 = 可信中立的协调层"用法,不是套个 token 的叙事。

### 4. 我能学到什么
- **subnet = 可插拔市场模板**:任何"可评分的 AI 任务"都能注册成 subnet,然后让市场决定它的价值。做 Week 2+ 时如果要设计 AI 任务的激励系统,这个"任务定义 + 评分函数 + 经济出口"的三段式可以直接借鉴
- **hotkey / coldkey 分离**:对 agent 类系统是非常实用的安全模型 — 长期资金的私钥永远不上线,短期操作密钥可以热在 GPU 上签名,被打也最多丢 stake
- **dTAO 把"用户偏好"喂给"算力市场"**:用户用钱包投票 subnet,emission 跟着流,**这是把链上流动性当反馈信号给到 AI 训练分配**,很值得搬到小场景里(比如让用户用质押决定 fine-tune 哪个细分任务)

### 5. 风险与开放问题
- **评分游戏化(metagame collusion)**:validator 与 miner 串通刷分是已知的攻击面,YC3 在尝试缓解但远未解决。任何想抄 Bittensor 评分机制的项目都要先想清楚 evaluator 自身的诚实假设
- **真实需求 vs. 内部经济**:有多少 TAO 收入来自"外部用户为推理付费",有多少来自"内部投机循环"?dTAO 上线后这个数字才刚开始变得可观测,长期可持续性还要看

### 6. 来源链接
- 官方文档:https://docs.learnbittensor.org/ (旧 docs.bittensor.com 已 308 跳转到这里)
- 主要 GitHub:https://github.com/opentensor/bittensor (Python SDK)、subtensor 链代码独立仓
- 关键概念:Yuma Consensus、dTAO、subnet incentive mechanism(文档 `learn/` 与 `subnets/` 章节)

---

## 横向对照与个人判断

| | Virtuals Protocol | Bittensor |
|---|---|---|
| 主要解决 | Agent 之间的商业结算 | AI 商品的定价与算力补贴分配 |
| 链选择 | Base (EVM L2) | Substrate 独立链 |
| Web3 必要性 | escrow + evaluator 仲裁 = 真需要 | 评分与 emission 算法上链 = 真需要 |
| 弱链上的部分 | 代币 bonding curve(更像 launchpad) | 模型推理本身不上链(性能与隐私要求) |
| 给我的最大启发 | 三角(委托/执行/验证)合约状态机 | hotkey/coldkey 双密钥安全模型 |

**判断**:这两个项目代表了 AI × Web3 的两条主线 ——
- **Virtuals 走"协调层"**:把 agent 之间的交互标准化、可结算化,有点像给 AI 装上"合同与法庭"
- **Bittensor 走"激励层"**:把"什么样的 AI 输出值钱"这件事市场化,把奖励分配交给链上算法

**Week 2+ 跟踪问题**:
1. ACP 的 evaluator agent 在真实对抗下能撑住吗?声誉 + 经济激励够不够 slashing 替代?
2. dTAO 后,subnet 的活跃用户数 / 外部付费收入是否真的上升?如果不是,内部循环就是泡沫
3. ERC-8004 / ERC-8183 这类提案能不能让两套设计变成可互操作的标准?
