# Agent Profile 与能力声明草图

> Week 2 | Agent Identity | 身份、能力、信誉的设计空间

---

## 1. 为什么 Agent 需要 Profile

Web2 的 API 有 OpenAPI spec，告诉调用方"我能做什么、入参是什么、出参是什么"。但 AI Agent 比 API 复杂得多：

- Agent 的行为是概率性的，不是确定性的
- Agent 会失败，且失败模式不可枚举
- Agent 需要付费和被付费
- Agent 的可信度随执行历史变化

所以需要一个标准化的 Profile 结构，让人、其他 Agent、协议能快速判断："这个 Agent 是谁、能干什么、干得怎么样、出事了谁负责"。

---

## 2. Agent Profile 草图

```
┌─────────────────────────────────────────────────────────┐
│                    Agent Profile v0.1                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─── Identity ────────────────────────────────────┐    │
│  │  did:           did:ethr:sepolia:0xABC...DEF    │    │
│  │  name:          "DCA Rebalancer"                │    │
│  │  version:       "0.2.1"                         │    │
│  │  operator:      0x3D58...d2B8 (EOA)             │    │
│  │  smart_account: 0x7F2A...9E31 (ERC-4337)        │    │
│  │  created_at:    2026-05-18T00:00:00Z            │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─── Capabilities ───────────────────────────────┐    │
│  │  actions:                                       │    │
│  │    - type: "swap"                               │    │
│  │      protocols: [uniswap-v3]                    │    │
│  │      pairs: [USDC/WETH, USDC/DAI]              │    │
│  │      max_per_tx: 50 USDC                        │    │
│  │      max_daily: 200 USDC                        │    │
│  │    - type: "query"                              │    │
│  │      sources: [on-chain, coingecko-api]         │    │
│  │  tools:                                         │    │
│  │    - mcp://price-oracle/getPrice                │    │
│  │    - mcp://uniswap/swap                         │    │
│  │  chains: [ethereum-sepolia]                     │    │
│  │  session_key_policy: ipfs://Qm...policy.json    │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─── Interface ──────────────────────────────────┐    │
│  │  input:                                         │    │
│  │    protocol: A2A (Agent-to-Agent)               │    │
│  │    format: JSON-RPC 2.0                         │    │
│  │    schema: ipfs://Qm...input-schema.json        │    │
│  │  output:                                        │    │
│  │    format: JSON-RPC 2.0                         │    │
│  │    includes: [tx_hash, execution_proof, logs]   │    │
│  │  mcp_server:                                    │    │
│  │    endpoint: https://agent.example/mcp          │    │
│  │    tools_manifest: /.well-known/mcp.json        │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─── Pricing ────────────────────────────────────┐    │
│  │  model: per_execution                           │    │
│  │  fee: 0.1 USDC per swap execution               │    │
│  │  gas: paymaster_sponsored (operator pays)       │    │
│  │  payment_methods:                               │    │
│  │    - x402 (HTTP 402 + USDC on Base)             │    │
│  │    - direct USDC transfer                       │    │
│  │  free_tier: query operations (unlimited)        │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─── Liability ──────────────────────────────────┐    │
│  │  failure_policy:                                │    │
│  │    - revert: no fee charged                     │    │
│  │    - wrong_execution: operator liable up to     │    │
│  │      max_per_tx (50 USDC)                       │    │
│  │    - unavailable: SLA 99% uptime, no penalty    │    │
│  │  dispute_resolution:                            │    │
│  │    method: on-chain arbitration (Kleros)         │    │
│  │    evidence: execution logs + chain state        │    │
│  │  insurance: none (testnet phase)                │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─── Reputation ─────────────────────────────────┐    │
│  │  source: on-chain execution history             │    │
│  │  metrics:                                       │    │
│  │    total_executions: 142                        │    │
│  │    success_rate: 97.2%                          │    │
│  │    avg_slippage_deviation: 0.3%                 │    │
│  │    total_volume: 12,400 USDC                    │    │
│  │    uptime_30d: 99.1%                            │    │
│  │    attestations: 3 (from known operators)       │    │
│  │  registry: EAS attestation UIDs                 │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Identity vs Capability vs Reputation

这三个概念经常被混在一起，但它们回答的问题完全不同：

| 维度 | 回答的问题 | 数据来源 | 可伪造性 | 变化频率 |
|---|---|---|---|---|
| **Identity** | "你是谁？" | DID、链上地址、operator 签名 | 低（密码学绑定） | 几乎不变 |
| **Capability** | "你能做什么？" | Profile 声明 + Session Key Policy | 中（声明可夸大） | 随版本更新 |
| **Reputation** | "你做得怎么样？" | 链上执行记录、第三方 attestation | 低（链上不可篡改） | 持续累积 |

**关键区别**：

- **Identity 是前提，不是信任**。知道一个 Agent 的 DID 不等于信任它。就像知道一个人的身份证号不代表你愿意借钱给他。
- **Capability 是声明，不是保证**。Agent 声明自己能做 swap，但做得好不好、会不会出错，需要 Reputation 来验证。Capability 可以被 Session Key Policy 在链上强制限定（声明了 swap 但 Session Key 只允许 query → 实际 capability 被链上约束）。
- **Reputation 是后验的，不可提前获得**。新 Agent 没有 Reputation，只能通过小额试错积累。这就是为什么需要渐进式信任——先在 testnet 跑，再小额 mainnet，最后才能获得大额委托。

### 三者的信任推导链

```
Identity (密码学证明 "你是 0xABC")
    │
    ▼
Capability (声明 "我能做 swap，限额 50 USDC")
    │
    ├──→ 链上验证: Session Key Policy 确认声明与链上权限一致 ✓
    │
    ▼
Reputation (链上记录 "142 次执行，97.2% 成功率")
    │
    ▼
Trust Decision (调用方判断 "我愿意委托这个 Agent 执行 30 USDC 的 swap")
```

---

## 4. 相关协议映射

### MCP (Model Context Protocol)

MCP 定义了 Agent 与 Tool 之间的交互标准。在 Profile 中：
- `tools` 字段列出 Agent 暴露的 MCP tool（Agent 作为 MCP server）
- `mcp_server.endpoint` 是其他 Agent 或客户端调用的入口
- MCP 解决的是 **interface 层** 的标准化——怎么调用，不管信任不信任

### A2A (Agent-to-Agent Protocol)

Google 提出的 A2A 协议关注 Agent 之间的发现和协作：
- Agent Card（类似 Profile）：描述 Agent 的能力、endpoint、认证方式
- Task 生命周期：submitted → working → completed / failed
- A2A 解决的是 **coordination 层** 的标准化——Agent 之间怎么分工

**Profile 中的对应**：A2A 的 Agent Card 可以看作 Profile 的子集。Profile 额外加了 Pricing、Liability、Reputation 这些链上经济相关的字段。

### ERC-8004 (Agent ENS Name)

ERC-8004 提案为 Agent 定义了 ENS 子域名标准，解决"怎么找到一个 Agent"的问题：
- `dca-rebalancer.agent.eth` → 解析到 Profile 的链上 / IPFS 存储地址
- Profile 的 `did` 字段可以与 ENS name 关联
- 但 ERC-8004 本身不定义 capability 或 reputation，只定义 identity 的命名层

### EAS (Ethereum Attestation Service)

EAS 可以用来构建 Reputation：
- Operator 为自己的 Agent 发 attestation："这个 Agent 由我运营，Profile 内容属实"
- 第三方（如 Paymaster 运营商）为 Agent 发 attestation："这个 Agent 在我的 Paymaster 下执行了 100 次零 revert"
- Attestation 的链上不可篡改性让 Reputation 可信

---

## 5. 从链上执行记录构建信誉

这是 5/24 check-in 的核心洞察：链上执行记录本身就是最好的信誉来源，因为它不可伪造、不可删除、公开可验证。

### 可用的链上信号

```
EntryPoint UserOperationEvent
    │
    ├── success: bool          → 成功率
    ├── actualGasCost: uint256 → gas 效率
    ├── sender: address        → Agent 的 Smart Account
    └── paymaster: address     → 谁为这个 Agent 付 gas

ERC-20 Transfer events
    │
    ├── from / to              → 交易对手方
    ├── value                  → 交易金额
    └── token address          → 交易 token

Uniswap Swap events
    │
    ├── amount0 / amount1      → 实际成交量
    ├── sqrtPriceX96           → 成交价格
    └── 与预期滑点的偏差         → 执行质量
```

### 信誉指标计算

| 指标 | 计算方式 | 含义 |
|---|---|---|
| 成功率 | success_count / total_count | 基本可靠性 |
| 执行质量 | avg(actual_slippage - declared_max_slippage) | 声明是否保守/准确 |
| 活跃度 | operations_last_30d | 持续运行而非间歇性 |
| 资金规模 | total_volume_usd | 被信任处理的资金量级 |
| Paymaster 关系 | 是否有知名 Paymaster 持续代付 | 第三方信任背书 |
| 账户年龄 | block.timestamp - first_operation_timestamp | 长期存活 |

### 自增强信任循环

这就是 5/24 check-in 提到的"self-reinforcing trust loop"：

```
Agent 启动（零信誉）
    │
    ▼
小额 testnet 操作 ──→ 积累执行记录
    │
    ▼
执行记录可验证 ──→ 信誉指标上升
    │
    ▼
Paymaster 愿意代付更多 gas ──→ Agent 可执行更多操作
    │
    ▼
更多操作 ──→ 更多记录 ──→ 更高信誉
    │
    ▼
用户/其他 Agent 愿意委托更大金额
    │
    ▼
Session Key Policy 限额可上调
    │
    ▼
Agent 的"经济能力"增长 ──→ 继续积累
    │
    ▼
(循环继续)
```

**关键设计约束**：这个循环必须是 **渐进的**。如果允许"突然跳到高限额"，就破坏了循环的安全属性。每次限额上调都应该基于足够的历史数据，而不是单次大额成功。

---

## 6. Profile 的存储与发现

| 层 | 存储内容 | 原因 |
|---|---|---|
| 链上 (ENS + EAS) | Identity (DID → ENS name)、Reputation attestations | 不可篡改、公开可验证 |
| IPFS | 完整 Profile JSON、Session Key Policy | 内容寻址、不可变、低成本 |
| 链下 (API endpoint) | 实时状态（当前剩余限额、在线状态） | 需要实时性，链上存储成本过高 |

**发现流程**：

```
调用方想找一个 DCA Agent
    │
    ▼
查询 ENS: *.agent.eth (或 Agent Registry 合约)
    │
    ▼
解析到 IPFS hash → 读取完整 Profile JSON
    │
    ▼
检查 Capability 是否匹配需求
    │
    ▼
查询 EAS attestation → 验证 Reputation
    │
    ▼
调用 Agent 的 MCP/A2A endpoint → 开始交互
```

---

## 7. 开放问题

- **Capability 声明的链上强制**：Profile 里声明"max 50 USDC"，但链上 Session Key Policy 设的是 100 USDC。以谁为准？应该有一个校验层确保声明与链上状态一致。
- **负面信誉**：Agent 执行失败或造成损失，如何在链上记录"扣分"？EAS attestation 目前没有"撤销"语义，只有"revoke"。
- **Agent Profile 的可组合性**：一个 Orchestrator Agent 调用多个 Sub-Agent，Orchestrator 的 Reputation 是否应该继承 Sub-Agent 的指标？
- **隐私与信誉的矛盾**：链上执行记录公开，意味着 Agent 的策略可被逆向工程。ZK proof 能否在不暴露具体操作的前提下证明"成功率 > 95%"？
