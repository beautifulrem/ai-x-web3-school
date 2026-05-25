# 治理协作流程草图

> Week 2 | Governance / Coordination | 多 Agent 协作的治理设计

---

## 1. 场景定义：多 Agent DeFi 组合策略

一个用户想实现"跨协议的 yield 优化"：在 Aave、Compound、Uniswap LP 之间动态调配资金，追求最优收益率。单个 Agent 做不好（需要多个协议的专业知识），所以拆成多个 Agent 协作。

### 参与方

```
┌──────────────────────────────────────────────┐
│  用户 (Owner)                                  │
│  • 资金所有者                                   │
│  • 设定总策略 + 预算                             │
│  • 拥有最终否决权                                │
└───────────────────┬──────────────────────────┘
                    │ 委托
                    ▼
┌──────────────────────────────────────────────┐
│  Orchestrator Agent                            │
│  • 接收用户策略意图                              │
│  • 分解任务并分配给子 Agent                       │
│  • 汇总结果并决定最终执行方案                      │
│  • 拥有 Session Key: 可调用子 Agent              │
│  • 不直接操作 DeFi 协议                          │
└───────────────────┬──────────────────────────┘
                    │ 分配任务
       ┌────────────┼────────────┐
       ▼            ▼            ▼
┌────────────┐ ┌────────────┐ ┌────────────┐
│ Aave Agent │ │ Compound   │ │ Uniswap LP │
│            │ │ Agent      │ │ Agent      │
│ • 查询 APY │ │ • 查询 APY │ │ • 查询 pool│
│ • 供应/赎回│ │ • 供应/赎回│ │ • 添加/移除│
│ • 仅限 Aave│ │ • 仅限 Comp│ │   流动性   │
│   合约交互 │ │   合约交互 │ │ • 仅限 Uni │
└────────────┘ └────────────┘ └────────────┘
```

---

## 2. 协作流程

### Phase 1: 任务分配

```
用户下发策略:
  "将 1000 USDC 分配到最优收益协议，单协议最多 40%，
   每日检查一次，收益率差 > 1% 时触发再平衡"
         │
         ▼
Orchestrator Agent 解析意图:
  ├─ 总金额: 1000 USDC
  ├─ 单协议上限: 400 USDC (40%)
  ├─ 检查频率: 每日
  ├─ 再平衡阈值: 1% APY 差异
  └─ 范围: Aave, Compound, Uniswap LP
         │
         ▼
Orchestrator 生成子任务:
  ┌──────────────────────────────────────────────┐
  │ Task 1 (→ Aave Agent)                        │
  │   action: query_apy                          │
  │   params: { asset: "USDC", market: "v3" }    │
  │   deadline: 5 min                            │
  │   reward: 0.01 USDC                          │
  └──────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────┐
  │ Task 2 (→ Compound Agent)                    │
  │   action: query_apy                          │
  │   params: { asset: "USDC", market: "v3" }    │
  │   deadline: 5 min                            │
  │   reward: 0.01 USDC                          │
  └──────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────┐
  │ Task 3 (→ Uniswap LP Agent)                  │
  │   action: query_pool_apy                     │
  │   params: { pair: "USDC/WETH", fee: 500 }   │
  │   deadline: 5 min                            │
  │   reward: 0.01 USDC                          │
  └──────────────────────────────────────────────┘
```

### Phase 2: 并行执行 + 结果汇总

```
并行执行 (A2A protocol):

Aave Agent ────────→ 查询链上 APY ────→ 返回: 3.2% APY
                                              │
Compound Agent ────→ 查询链上 APY ────→ 返回: 2.8% APY
                                              │
Uniswap LP Agent ──→ 查询 pool 状态 ──→ 返回: 5.1% APY (含 IL 风险)
                                              │
                                              ▼
                                     Orchestrator 汇总:
                                     ├─ Aave: 3.2% (低风险)
                                     ├─ Compound: 2.8% (低风险)
                                     └─ Uniswap: 5.1% (中风险, IL)
```

### Phase 3: 决策 + 权限委托

```
Orchestrator 生成分配方案:
  ├─ Aave:     400 USDC (40%) — 触及上限，收益率最优的低风险选项
  ├─ Uniswap:  400 USDC (40%) — 触及上限，收益率最高但有 IL
  └─ Compound: 200 USDC (20%) — 剩余资金
         │
         ▼
┌────────────────────────────────────────┐
│ 风险检查 (Orchestrator 内部)             │
│                                        │
│ ✓ 单协议 ≤ 40%                          │
│ ✓ 总额 = 1000 USDC                     │
│ ✓ 所有协议在白名单内                      │
│ ✗ Uniswap LP 有 IL 风险                 │
│   → 标记为"需用户确认"                    │
└────────────────────────────────────────┘
         │
         ▼
通知用户确认:
  "建议分配: Aave 400 / Uniswap LP 400 / Compound 200
   注意: Uniswap LP 有 impermanent loss 风险
   确认执行？ [Y/N]"
         │
    用户确认 Y
         │
         ▼
Orchestrator 向子 Agent 委托执行权限:
  ┌───────────────────────────────────────────┐
  │ Delegation (链上 Session Key 二级委托)       │
  │                                           │
  │ Orchestrator 的 Session Key               │
  │   └─ 子委托给 Aave Agent:                  │
  │       target: Aave V3 Pool                │
  │       method: supply(USDC, 400e6)         │
  │       one-time: true                      │
  │       deadline: 1 hour                    │
  │                                           │
  │   └─ 子委托给 Compound Agent:              │
  │       target: Compound V3 Comet           │
  │       method: supply(USDC, 200e6)         │
  │       one-time: true                      │
  │       deadline: 1 hour                    │
  │                                           │
  │   └─ 子委托给 Uniswap LP Agent:            │
  │       target: NonfungiblePositionManager   │
  │       method: mint(...)                   │
  │       max_value: 400 USDC                 │
  │       one-time: true                      │
  │       deadline: 1 hour                    │
  └───────────────────────────────────────────┘
```

### Phase 4: 结果验证

```
各子 Agent 执行完成后:

Aave Agent ────→ tx_hash_1: supply 400 USDC ✓
                 proof: aToken balance += 400
                      │
Compound Agent ─→ tx_hash_2: supply 200 USDC ✓
                 proof: cToken balance += 200
                      │
Uniswap LP Agent → tx_hash_3: mint LP position ✓
                 proof: NFT tokenId = 12345
                 actual_amounts: 400 USDC + 0.14 WETH
                      │
                      ▼
Orchestrator 验证:
  ┌────────────────────────────────────────┐
  │ Verification Checklist                  │
  │                                        │
  │ ✓ tx_hash_1 on-chain confirmed         │
  │ ✓ aToken balance matches expected      │
  │ ✓ tx_hash_2 on-chain confirmed         │
  │ ✓ cToken balance matches expected      │
  │ ✓ tx_hash_3 on-chain confirmed         │
  │ ✓ LP NFT owned by Smart Account        │
  │ ✓ total deployed = 1000 USDC           │
  │ ✓ no unexpected approvals granted      │
  │                                        │
  │ Result: ALL PASS                       │
  │ 写入执行日志                              │
  │ 子 Agent 的 one-time Session Key 自动失效 │
  └────────────────────────────────────────┘
```

---

## 3. 争议处理流程

多 Agent 协作必然会有执行失败、结果偏差、责任不清的情况。

### 争议类型与处理

```
争议触发
    │
    ▼
┌─────────────────────────────────┐
│ 类型判定                          │
└────────┬────────────────────────┘
         │
    ┌────┴────────┬──────────────┬──────────────┐
    ▼             ▼              ▼              ▼
执行失败       结果偏差        超时未完成      权限越界
(tx revert)   (滑点过大)     (deadline 过期)  (调用非白名单)
    │             │              │              │
    ▼             ▼              ▼              ▼
自动处理:      阈值判定:       自动处理:       紧急处理:
• 链上 revert   • 偏差<2%:      • 任务标记      • 立即撤销
  无状态变更     记录但接受      failed          Session Key
• 不收取        • 偏差 2-5%:    • 通知          • 冻结相关
  Agent fee     降低 Agent      Orchestrator    Agent
• 重试 or       信誉分          重新分配        • 全面审计
  降级人工      • 偏差>5%:      • 不收取         所有操作
                触发争议        Agent fee       • 通知用户
                仲裁
                    │
                    ▼
         ┌──────────────────┐
         │  链上争议仲裁       │
         │  (Kleros / UMA)   │
         │                   │
         │  证据:             │
         │  • 原始任务定义     │
         │  • Agent 的执行 tx │
         │  • 链上状态变化     │
         │  • 预期 vs 实际    │
         │                   │
         │  仲裁结果:         │
         │  • 退款 / 扣罚     │
         │  • 信誉扣分        │
         │  • 黑名单          │
         └──────────────────┘
```

### 责任分层

| 层级 | 责任方 | 承担内容 |
|---|---|---|
| 策略错误 | 用户 + Orchestrator | 方案本身不合理（如全仓 LP 导致 IL 巨大） |
| 执行错误 | 子 Agent | 正确策略但执行有误（如参数填错、调用失败） |
| 基础设施故障 | 无人直接承担 | Bundler 宕机、RPC 不可用、gas spike |
| 协议风险 | 无人直接承担 | Aave 合约被 exploit、Uniswap pool 被操纵 |

关键原则：**Agent 只对自己的执行质量负责，不对底层协议的安全性负责**。但 Agent 有义务在检测到异常时停止操作并报告。

---

## 4. 权限委托的链上实现

多 Agent 协作的核心技术挑战是"权限的安全委托"——Orchestrator 怎么把受限的执行权交给子 Agent，且子 Agent 无法越权。

### 二级 Session Key 委托模型

```
用户 (Safe Owner)
    │
    │ 签发 Session Key A (给 Orchestrator)
    │   scope: 可调用子 Agent 注册合约
    │   budget: 1000 USDC/day
    │   duration: 7 days
    │
    ▼
Orchestrator Agent (持有 Session Key A)
    │
    │ 通过链上 Delegation Registry 注册子委托
    │
    ├─ Sub-Session Key B1 (给 Aave Agent)
    │   scope: 仅 Aave V3 Pool.supply()
    │   budget: 400 USDC
    │   duration: 1 hour
    │   one-time: true
    │
    ├─ Sub-Session Key B2 (给 Compound Agent)
    │   scope: 仅 Compound Comet.supply()
    │   budget: 200 USDC
    │   duration: 1 hour
    │   one-time: true
    │
    └─ Sub-Session Key B3 (给 Uniswap LP Agent)
        scope: 仅 PositionManager.mint()
        budget: 400 USDC
        duration: 1 hour
        one-time: true
```

**链上约束保证**：
- 子 Session Key 的权限范围 ⊆ 父 Session Key 的权限范围（不能越权委托）
- 子 Session Key 的预算 ≤ 父 Session Key 的剩余预算
- 子 Session Key 的有效期 ≤ 父 Session Key 的剩余有效期
- one-time 标记确保子 Agent 用完即废，不能重复执行

### Delegation Registry 合约（伪代码）

```solidity
// 简化示意，非完整实现
contract DelegationRegistry {
    struct Delegation {
        address parent;      // 父 Session Key 持有者
        address child;       // 子 Agent 地址
        address target;      // 允许调用的合约
        bytes4 selector;     // 允许调用的方法
        uint256 maxValue;    // 最大金额
        uint256 deadline;    // 过期时间
        bool oneTime;        // 是否一次性
        bool used;           // 是否已使用
    }

    // validateUserOp 时检查:
    // 1. child 是否有 parent 签发的有效 delegation
    // 2. delegation 的 scope 是否覆盖当前操作
    // 3. parent 的 Session Key 本身是否仍然有效
}
```

---

## 5. DAO 治理工具与 Agent 协作的结合点

### 5.1 现有 DAO 工具的局限

| 工具 | 设计假设 | Agent 协作的不适配 |
|---|---|---|
| Snapshot | 人类投票，每次提案间隔数天 | Agent 决策频率是分钟级，不可能每次投票 |
| Tally / Governor | Token 加权，链上执行 | Agent 没有治理 token，无投票权 |
| Gnosis Safe | M-of-N 签名 | 签名者是人，确认时间不适配 Agent 速度 |
| Aragon | 组织管理框架 | 为人类组织设计，权限模型不支持 Session Key |

### 5.2 需要的适配

**核心洞察**：Agent 协作不是"DAO 投票"，而是"受约束的自动执行 + 异常时人工介入"。治理的角色从"每次决策都参与"变成"设定规则 + 监督 + 争议处理"。

```
传统 DAO 治理:
  提案 → 投票 → 执行
  (每次决策都走全流程)

Agent 协作治理:
  规则设定 → 自动执行 → 异常触发人工
  (常态自动，异常才治理)
```

### 5.3 结合点

| 结合点 | DAO 工具提供 | Agent 协作需要 |
|---|---|---|
| **规则设定** | Governor 提案 + 投票修改参数 | Session Key Policy 的参数（限额、白名单）通过 DAO 投票更新 |
| **Agent 注册** | Registry 合约（类似 ENS） | 新 Agent 加入协作需要 DAO 审批（投票 + 质押） |
| **预算分配** | Treasury 管理（Safe） | DAO Treasury 向 Paymaster deposit 注资，控制总 gas 预算 |
| **异常仲裁** | 争议解决（Kleros / UMA） | Agent 执行偏差超过阈值时，提交争议给链上仲裁 |
| **升级治理** | Proxy 升级投票 | Orchestrator 的策略逻辑升级需要 DAO 投票批准 |
| **信誉管理** | Attestation（EAS） | DAO 成员为 Agent 发 attestation，建立链上信誉 |

### 5.4 一个具体结合示例

```
场景: DAO Treasury 管理的多 Agent yield 策略

┌─────────────────────────────────────────────────┐
│  DAO (Governor + Safe)                            │
│                                                   │
│  提案类型:                                         │
│  ├─ "增加 Aave Agent 的单日限额到 500 USDC"        │
│  │   → 投票通过 → 更新链上 Session Key Policy      │
│  │                                                │
│  ├─ "注册新的 Morpho Agent 到协作网络"              │
│  │   → 投票通过 → Agent Registry 添加新条目         │
│  │   → 签发 Session Key 给新 Agent                 │
│  │                                                │
│  ├─ "向 Paymaster 补充 0.5 ETH deposit"            │
│  │   → 投票通过 → Safe 执行 ETH 转账到 Paymaster   │
│  │                                                │
│  └─ "暂停 Uniswap LP Agent（IL 损失过大）"          │
│      → 投票通过 → 撤销 Session Key                  │
│      → 触发 Orchestrator 重新分配资金               │
│                                                   │
│  日常运行: Agent 自动执行，无需投票                    │
│  异常触发: 偏差 > 5% → 自动暂停 → 提案讨论           │
│                                                   │
└─────────────────────────────────────────────────┘
```

---

## 6. 完整协作流程图

```
┌──────────────────────────────────────────────────────────────────┐
│                        治理层 (DAO)                                │
│   ┌─────────┐   ┌────────────┐   ┌────────────┐                 │
│   │规则设定   │   │Agent 注册   │   │预算分配     │                 │
│   │(Governor)│   │(Registry)  │   │(Treasury)  │                 │
│   └────┬────┘   └─────┬──────┘   └─────┬──────┘                 │
│        └──────────────┼────────────────┘                         │
│                       │                                          │
├───────────────────────┼──────────────────────────────────────────┤
│                       ▼         策略层 (Orchestrator)             │
│             ┌─────────────────────┐                              │
│             │  Orchestrator Agent  │                              │
│             │  ├─ 解析用户意图      │                              │
│             │  ├─ 分解任务         │                              │
│             │  ├─ 分配子 Agent     │                              │
│             │  ├─ 汇总 + 验证     │                              │
│             │  └─ 异常上报        │                              │
│             └───────┬─────────────┘                              │
│                     │                                            │
├─────────────────────┼────────────────────────────────────────────┤
│                     ▼         执行层 (Sub-Agents)                 │
│    ┌──────────┐ ┌──────────┐ ┌──────────┐                       │
│    │Aave Agent│ │Comp Agent│ │Uni Agent │  ← 各持有限定 Session Key│
│    └────┬─────┘ └────┬─────┘ └────┬─────┘                       │
│         │            │            │                              │
├─────────┼────────────┼────────────┼──────────────────────────────┤
│         ▼            ▼            ▼     链上执行层                 │
│    ┌──────────────────────────────────────────┐                  │
│    │  EntryPoint                               │                  │
│    │  ├─ validateUserOp (Session Key 验证)      │                  │
│    │  ├─ validatePaymaster                     │                  │
│    │  └─ execute (supply / swap / mint)        │                  │
│    └──────────────────────────────────────────┘                  │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                        监控层 (横切)                               │
│    ┌──────────────────────────────────────────┐                  │
│    │  • 执行日志记录                             │                  │
│    │  • 偏差检测 (实际 vs 预期)                   │                  │
│    │  • 异常告警 → 用户 / DAO                    │                  │
│    │  • 信誉更新 (per Agent)                    │                  │
│    └──────────────────────────────────────────┘                  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 7. 5/23 Check-in 的回应：表达力 vs 约束

5/23 讨论了"Expressiveness vs Containment"的张力——Agent 能做的事越多越有用，但风险也越大。多 Agent 协作放大了这个张力：

### Rule-driven vs Intent-driven

| 维度 | Rule-driven (当前阶段) | Intent-driven (未来方向) |
|---|---|---|
| 任务定义 | "在 Aave V3 上 supply 400 USDC" | "把 40% 资金放到最优借贷协议" |
| Orchestrator 角色 | 路由器（把预定义任务分给预定义 Agent） | 规划器（理解意图后自主拆解任务） |
| 子 Agent 自由度 | 只执行特定合约+方法 | 可在协议范围内自主选择最优路径 |
| Session Key Policy | 精确到 method selector | 精确到协议级别，方法由 Agent 决定 |
| 风险 | 低（路径固定） | 中（Agent 有策略自由度） |
| 上限 | 低（不能适应市场变化） | 高（可以动态优化） |

### 产品演进路径

```
Phase 1 (现在): Conservative / Rule-driven
  ├─ Orchestrator 是固定逻辑，不用 LLM
  ├─ 子 Agent 只执行预定义操作
  ├─ Session Key 精确到 method + params
  └─ 任何偏差 → 暂停 + 人工

Phase 2 (3-6个月): Gradual Opening
  ├─ Orchestrator 用 LLM 做策略建议，但需人工确认
  ├─ 子 Agent 可在协议级白名单内自选方法
  ├─ Session Key 放宽到协议级别
  └─ 小额偏差自动处理，大额偏差 → 人工

Phase 3 (6-12个月): Intent-driven
  ├─ Orchestrator 自主拆解意图为任务
  ├─ 子 Agent 在预算范围内自主决策
  ├─ Session Key 基于信誉动态调整
  └─ 人工只在异常时介入
```

每个 Phase 的过渡条件：上一个 Phase 积累了足够的链上执行记录 + 信誉数据，证明 Agent 在受限范围内是可靠的。这就是 5/24 的"自增强信任循环"在协作场景中的应用。

---

## 8. 开放问题

- **Orchestrator 的单点风险**：所有协作都经过 Orchestrator，它被攻破 = 整个系统被攻破。去中心化的 Orchestrator 怎么做？多个 Orchestrator 的共识机制？
- **子 Agent 之间的利益冲突**：Aave Agent 和 Compound Agent 可能各自"推销"自己的协议（因为操作越多 fee 越多）。如何保证 Orchestrator 的决策不被子 Agent 的"偏见"影响？
- **跨时区/跨链的协作**：Aave 在 Ethereum，Compound 在 Arbitrum，Uniswap 在 Optimism。跨链操作的原子性如何保证？失败时如何回滚已成功的链？
- **治理速度与 Agent 速度的失配**：DAO 投票需要 3-7 天，Agent 操作是分钟级。紧急情况（如协议被 exploit）如何快速治理响应？Guardian 机制 vs Optimistic Governance 的权衡。
