# Agent 链上动作权限策略

> Week 2 | Wallet / Permission | 20 学分

---

## 1. Agent 发起链上动作的执行流程图

```
用户意图(自然语言)
    │
    ▼
┌─────────────────────┐
│  LLM 解析意图        │  ← Agent 自动
│  生成 calldata       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Guardrails 校验     │  ← Agent 自动
│  • 目标合约在白名单？ │
│  • 方法 selector 允许？│
│  • value ≤ 单笔限额？ │
│  • 日累计 ≤ 日限？    │
└─────────┬───────────┘
          │
     ┌────┴────┐
     │ 通过？   │
     └────┬────┘
    YES   │   NO → 拒绝执行，日志记录，通知用户
          ▼
┌─────────────────────┐
│  金额 > 人工阈值？    │
└─────────┬───────────┘
    YES   │   NO
    │     │
    ▼     ▼
┌────────┐ ┌──────────────────┐
│人工确认 │ │ 构造 UserOperation │ ← Agent 自动
│(展示完整│ └────────┬─────────┘
│calldata│          │
│+风险评估)│          ▼
└───┬────┘ ┌──────────────────┐
    │      │ Bundler 模拟执行   │ ← 链上自动
    │      │ (eth_estimateGas) │
    ▼      └────────┬─────────┘
  确认？            │
  YES → ─────┐     │
  NO → 取消  │     │
             ▼     ▼
      ┌──────────────────┐
      │ EntryPoint        │ ← 链上自动
      │ handleOps()       │
      │ • validateUserOp  │
      │ • validatePaymaster│
      │ • execute         │
      └────────┬─────────┘
               │
          ┌────┴────┐
          │ 成功？   │
          └────┬────┘
     SUCCESS  │   REVERT
         │    │      │
         ▼    │      ▼
   ┌─────────┐│ ┌──────────┐
   │状态变更  ││ │回滚，无状态│
   │链上确认  ││ │泄漏       │
   └─────────┘│ │日志记录    │
              │ │告警通知    │
              │ └──────────┘
              ▼
      ┌──────────────────┐
      │ 日志落盘           │ ← Agent 自动
      │ • tx hash         │
      │ • gas 消耗         │
      │ • 执行结果          │
      │ • 累计预算消耗       │
      └──────────────────┘
```

**自动化步骤**：意图解析、calldata 生成、guardrails 校验、UserOp 构造、Bundler 模拟、EntryPoint 验证执行、日志记录

**必须人工确认的步骤**：
- 超过人工确认阈值的写操作
- 首次调用未见过的合约
- 涉及 approve / permit 的签名
- 任何主网操作（测试网可自动）

---

## 2. Agent Wallet 权限策略设计

场景：一个 DeFi 再平衡 Agent，负责在用户授权范围内自动调整投资组合。

### 预算控制

| 维度 | 限制 | 说明 |
|---|---|---|
| 单笔上限 | 50 USDC | 超过需人工确认 |
| 日累计上限 | 200 USDC | 含所有 swap + transfer |
| 月累计上限 | 3000 USDC | 硬上限，到达后 Session Key 自动失效 |
| Gas 预算 | Paymaster 代付，月上限 0.1 ETH | Agent 钱包零余额 |

### 可调用合约白名单

| 合约 | 允许方法 | 说明 |
|---|---|---|
| Uniswap V3 Router | `exactInputSingle`, `exactInput` | 仅 swap，不允许添加流动性 |
| USDC (ERC-20) | `transfer` (仅限指定接收地址) | 转账仅限用户主钱包 |
| WETH | `deposit`, `withdraw` | wrap/unwrap |
| **禁止** | 任何 `approve`, `permit`, `setApprovalForAll` | 防止授权攻击 |

### 可执行动作

- **允许**：查询价格、swap 白名单 token pair、wrap/unwrap ETH、转账到用户主钱包
- **需确认**：swap 金额 > 50 USDC、首次交互的 token、滑点 > 2%
- **禁止**：approve、跨链操作、与未验证合约交互、任何主网写操作（未升级前）

### 人工确认阈值

```
if (value > 50 USDC)           → 必须人工确认
if (slippage > 2%)             → 必须人工确认
if (contract not in whitelist) → 拒绝
if (method == approve/permit)  → 拒绝
if (daily_spent + value > 200) → 必须人工确认
if (network == mainnet)        → 必须人工确认
```

### 撤销方式

- **即时撤销**：用户从主账户（Safe 或 EOA owner）调用 `disableSessionKey(keyHash)` 即时废止
- **自动过期**：Session Key 有效期 7 天，到期自动失效，需用户重新签发
- **紧急冻结**：Guardian 地址可调用 `freezeAccount()` 冻结所有 Session Key

### 日志记录

每笔操作记录：
- timestamp、tx hash、target contract、method selector
- value (USDC 计价)、gas consumed、Paymaster sponsor amount
- 执行结果 (success / revert + reason)
- 累计日消耗 / 月消耗
- Session Key 剩余额度

日志存储：链上（EntryPoint UserOperationEvent）+ 链下（Agent 本地 SQLite + 可选 IPFS 归档）

### 失败处理

| 失败类型 | 处理 |
|---|---|
| Bundler 模拟失败 | 不提交链上，日志记录失败原因，3 次重试后通知用户 |
| EntryPoint revert | 状态不变（原子性保证），记录 revert reason，若连续 3 次 revert 自动暂停 Session Key |
| Paymaster 拒绝代付 | 降级：通知用户手动执行或补充 Paymaster deposit |
| Gas 价格异常高 | 等待 gas 回落，超过 24h 未执行则通知用户 |
| 目标合约升级 | 检测到 implementation 地址变更 → 自动暂停该合约交互，等用户确认新实现 |

---

## 3. ERC-4337、Safe、Guard / Policy 机制解析

### ERC-4337 (Account Abstraction)

**解决的风险**：EOA 的全有全无权限问题。

EOA 只有一把私钥，拿到私钥就等于拿到整个账户。ERC-4337 通过 UserOperation + EntryPoint 架构，让账户逻辑变成可编程的：
- **validateUserOp**：每笔操作都经过链上原子验证，签名错误或权限不足直接 revert，不会留下半执行状态
- **Paymaster**：gas 支付与操作权限解耦，Agent 不需要持有 ETH
- **Session Key**：临时密钥可绑定特定合约、方法、限额、有效期，实现最小权限原则

**关键价值**：把 Agent 的爆炸半径从"整个账户"缩小到"Session Key 允许的范围"。

### Safe (Multisig)

**解决的风险**：单点失败和缺乏审计。

Safe 作为多签钱包，适合做 Agent 的上级管控层：
- **阈值签名**：重要操作（如提高 Agent 限额、更换 Session Key）需要 M-of-N 签名
- **Module 系统**：Agent 通过 Safe Module 获得受限执行权限，Module 本身可被 Safe owner 随时禁用
- **Transaction Guard**：在交易执行前/后插入自定义校验逻辑

**架构角色**：Safe 当金库和策略层，ERC-4337 智能账户当 Agent 执行账户。

### Guard / Policy 机制

**解决的风险**：合约层面的越权和异常行为。

- **Transaction Guard (Safe)**：在 `execTransaction` 前调用 `checkTransaction`，可实现限额检查、黑名单过滤、时间锁
- **Policy Engine (Session Key Module)**：在 `validateUserOp` 内部，对每个 UserOp 检查 target、selector、value、calldata 参数是否符合 Session Key 的 policy 定义
- **Spending Limit Module**：链上维护消费记录，强制执行日/周/月限额

**三者的协同关系**：

```
Safe (金库层)
 └─ Transaction Guard: 控制哪些 Module 可以执行什么
     └─ Session Key Module (执行层)
         └─ Policy Engine: 控制每把 Session Key 的具体权限
             └─ ERC-4337 EntryPoint (验证层)
                 └─ validateUserOp: 原子性最终校验
```

每一层解决不同粒度的风险：Safe 解决"谁有权管理策略"，Policy 解决"Agent 能做什么"，EntryPoint 解决"每笔操作是否合法"。三层叠加后，即使 Agent 被 prompt injection 攻击，损失上限 = Session Key 允许的最大金额，而不是整个账户。
