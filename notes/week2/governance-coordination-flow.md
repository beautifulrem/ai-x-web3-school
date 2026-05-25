# 治理协作流程草图

> Week 2 | Governance / Coordination | 多 Agent 协作的治理设计

---

## 1. 场景定义：多 Agent DeFi 组合策略

一个用户想实现"跨协议的 yield 优化"：在 Aave、Compound、Uniswap LP 之间动态调配资金，追求最优收益率。单个 Agent 做不好（需要多个协议的专业知识），所以拆成多个 Agent 协作。

### 参与方

```mermaid
flowchart TD
    User["用户 (Owner)\n• 资金所有者\n• 设定总策略 + 预算\n• 拥有最终否决权"]
    User -- "委托" --> Orch["Orchestrator Agent\n• 接收用户策略意图\n• 分解任务并分配给子 Agent\n• 汇总结果并决定最终执行方案\n• 拥有 Session Key: 可调用子 Agent\n• 不直接操作 DeFi 协议"]
    Orch -- "分配任务" --> Aave["Aave Agent\n• 查询 APY\n• 供应/赎回\n• 仅限 Aave 合约交互"]
    Orch -- "分配任务" --> Comp["Compound Agent\n• 查询 APY\n• 供应/赎回\n• 仅限 Comp 合约交互"]
    Orch -- "分配任务" --> Uni["Uniswap LP Agent\n• 查询 pool\n• 添加/移除流动性\n• 仅限 Uni 合约交互"]
```

---

## 2. 协作流程

### Phase 1: 任务分配

```mermaid
flowchart TD
    A["用户下发策略:\n将 1000 USDC 分配到最优收益协议\n单协议最多 40%，每日检查一次\n收益率差 > 1% 时触发再平衡"]
    A --> B["Orchestrator Agent 解析意图:\n总金额: 1000 USDC\n单协议上限: 400 USDC (40%)\n检查频率: 每日\n再平衡阈值: 1% APY 差异\n范围: Aave, Compound, Uniswap LP"]
    B --> T1["Task 1 → Aave Agent\naction: query_apy\nparams: USDC, v3\ndeadline: 5 min\nreward: 0.01 USDC"]
    B --> T2["Task 2 → Compound Agent\naction: query_apy\nparams: USDC, v3\ndeadline: 5 min\nreward: 0.01 USDC"]
    B --> T3["Task 3 → Uniswap LP Agent\naction: query_pool_apy\nparams: USDC/WETH, fee 500\ndeadline: 5 min\nreward: 0.01 USDC"]
```

### Phase 2: 并行执行 + 结果汇总

```mermaid
flowchart LR
    A1["Aave Agent"] --> Q1["查询链上 APY"] --> R1["3.2% APY"]
    A2["Compound Agent"] --> Q2["查询链上 APY"] --> R2["2.8% APY"]
    A3["Uniswap LP Agent"] --> Q3["查询 pool 状态"] --> R3["5.1% APY\n(含 IL 风险)"]
    R1 --> SUM["Orchestrator 汇总:\nAave: 3.2% (低风险)\nCompound: 2.8% (低风险)\nUniswap: 5.1% (中风险, IL)"]
    R2 --> SUM
    R3 --> SUM
```

### Phase 3: 决策 + 权限委托

```mermaid
flowchart TD
    A["Orchestrator 生成分配方案:\nAave: 400 USDC (40%)\nUniswap: 400 USDC (40%)\nCompound: 200 USDC (20%)"]
    A --> B["风险检查 (Orchestrator 内部)\n✓ 单协议 ≤ 40%\n✓ 总额 = 1000 USDC\n✓ 所有协议在白名单内\n✗ Uniswap LP 有 IL 风险 → 需用户确认"]
    B --> C["通知用户确认:\n建议分配: Aave 400 / Uniswap LP 400 / Compound 200\n注意: Uniswap LP 有 IL 风险"]
    C --> D{"用户确认？"}
    D -- "Y" --> E["Orchestrator 委托执行权限\n(链上 Session Key 二级委托)"]
    E --> F["→ Aave Agent\ntarget: Aave V3 Pool\nmethod: supply(USDC, 400e6)\none-time, deadline: 1h"]
    E --> G["→ Compound Agent\ntarget: Compound V3 Comet\nmethod: supply(USDC, 200e6)\none-time, deadline: 1h"]
    E --> H["→ Uniswap LP Agent\ntarget: NonfungiblePositionManager\nmethod: mint(...)\nmax_value: 400 USDC\none-time, deadline: 1h"]
```

### Phase 4: 结果验证

```mermaid
flowchart TD
    A1["Aave Agent\ntx_hash_1: supply 400 USDC ✓\nproof: aToken balance += 400"]
    A2["Compound Agent\ntx_hash_2: supply 200 USDC ✓\nproof: cToken balance += 200"]
    A3["Uniswap LP Agent\ntx_hash_3: mint LP position ✓\nproof: NFT tokenId = 12345\nactual: 400 USDC + 0.14 WETH"]

    A1 --> V["Orchestrator 验证"]
    A2 --> V
    A3 --> V

    V --> CK["Verification Checklist\n✓ tx_hash_1 on-chain confirmed\n✓ aToken balance matches expected\n✓ tx_hash_2 on-chain confirmed\n✓ cToken balance matches expected\n✓ tx_hash_3 on-chain confirmed\n✓ LP NFT owned by Smart Account\n✓ total deployed = 1000 USDC\n✓ no unexpected approvals granted"]
    CK --> R["Result: ALL PASS\n写入执行日志\n子 Agent 的 one-time Session Key 自动失效"]
```

---

## 3. 争议处理流程

多 Agent 协作必然会有执行失败、结果偏差、责任不清的情况。

### 争议类型与处理

```mermaid
flowchart TD
    A["争议触发"] --> B{"类型判定"}

    B -- "执行失败\n(tx revert)" --> C["自动处理:\n• 链上 revert 无状态变更\n• 不收取 Agent fee\n• 重试 or 降级人工"]
    B -- "结果偏差\n(滑点过大)" --> D{"阈值判定"}
    B -- "超时未完成\n(deadline 过期)" --> E["自动处理:\n• 任务标记 failed\n• 通知 Orchestrator 重新分配\n• 不收取 Agent fee"]
    B -- "权限越界\n(调用非白名单)" --> F["紧急处理:\n• 立即撤销 Session Key\n• 冻结相关 Agent\n• 全面审计所有操作\n• 通知用户"]

    D -- "偏差 < 2%" --> G["记录但接受"]
    D -- "偏差 2-5%" --> H["降低 Agent 信誉分"]
    D -- "偏差 > 5%" --> I["触发争议仲裁"]

    I --> J["链上争议仲裁 (Kleros / UMA)\n证据: 原始任务定义、Agent 执行 tx、\n链上状态变化、预期 vs 实际\n仲裁结果: 退款/扣罚、信誉扣分、黑名单"]
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

```mermaid
flowchart TD
    User["用户 (Safe Owner)"] -- "签发 Session Key A\nscope: 可调用子 Agent 注册合约\nbudget: 1000 USDC/day\nduration: 7 days" --> Orch["Orchestrator Agent\n(持有 Session Key A)"]

    Orch -- "通过链上 Delegation Registry" --> B1["Sub-Session Key B1 → Aave Agent\nscope: 仅 Aave V3 Pool.supply()\nbudget: 400 USDC\nduration: 1 hour, one-time"]
    Orch --> B2["Sub-Session Key B2 → Compound Agent\nscope: 仅 Compound Comet.supply()\nbudget: 200 USDC\nduration: 1 hour, one-time"]
    Orch --> B3["Sub-Session Key B3 → Uniswap LP Agent\nscope: 仅 PositionManager.mint()\nbudget: 400 USDC\nduration: 1 hour, one-time"]
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

```mermaid
flowchart LR
    subgraph Traditional["传统 DAO 治理 (每次决策都走全流程)"]
        T1["提案"] --> T2["投票"] --> T3["执行"]
    end

    subgraph Agent["Agent 协作治理 (常态自动，异常才治理)"]
        A1["规则设定"] --> A2["自动执行"] --> A3["异常触发人工"]
    end
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

```mermaid
flowchart TD
    DAO["DAO (Governor + Safe)"]

    DAO --> P1["提案: 增加 Aave Agent 单日限额到 500 USDC\n→ 投票通过 → 更新链上 Session Key Policy"]
    DAO --> P2["提案: 注册新的 Morpho Agent 到协作网络\n→ 投票通过 → Agent Registry 添加新条目\n→ 签发 Session Key 给新 Agent"]
    DAO --> P3["提案: 向 Paymaster 补充 0.5 ETH deposit\n→ 投票通过 → Safe 执行 ETH 转账到 Paymaster"]
    DAO --> P4["提案: 暂停 Uniswap LP Agent (IL 损失过大)\n→ 投票通过 → 撤销 Session Key\n→ 触发 Orchestrator 重新分配资金"]
    DAO --> NORMAL["日常运行: Agent 自动执行，无需投票"]
    DAO --> ALERT["异常触发: 偏差 > 5% → 自动暂停 → 提案讨论"]
```

---

## 6. 完整协作流程图

```mermaid
flowchart TD
    subgraph GOV["治理层 (DAO)"]
        G1["规则设定\n(Governor)"]
        G2["Agent 注册\n(Registry)"]
        G3["预算分配\n(Treasury)"]
    end

    subgraph STRATEGY["策略层 (Orchestrator)"]
        ORCH["Orchestrator Agent\n• 解析用户意图\n• 分解任务\n• 分配子 Agent\n• 汇总 + 验证\n• 异常上报"]
    end

    subgraph EXEC["执行层 (Sub-Agents)"]
        SA1["Aave Agent"]
        SA2["Comp Agent"]
        SA3["Uni Agent"]
    end

    subgraph CHAIN["链上执行层"]
        EP["EntryPoint\n• validateUserOp (Session Key 验证)\n• validatePaymaster\n• execute (supply / swap / mint)"]
    end

    subgraph MONITOR["监控层 (横切)"]
        MON["• 执行日志记录\n• 偏差检测 (实际 vs 预期)\n• 异常告警 → 用户 / DAO\n• 信誉更新 (per Agent)"]
    end

    G1 --> ORCH
    G2 --> ORCH
    G3 --> ORCH
    ORCH --> SA1
    ORCH --> SA2
    ORCH --> SA3
    SA1 --> EP
    SA2 --> EP
    SA3 --> EP
    EP --> MON
    MON --> GOV
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

```mermaid
flowchart TD
    P1["Phase 1 (现在): Conservative / Rule-driven\n• Orchestrator 是固定逻辑，不用 LLM\n• 子 Agent 只执行预定义操作\n• Session Key 精确到 method + params\n• 任何偏差 → 暂停 + 人工"]
    P1 --> P2["Phase 2 (3-6个月): Gradual Opening\n• Orchestrator 用 LLM 做策略建议，但需人工确认\n• 子 Agent 可在协议级白名单内自选方法\n• Session Key 放宽到协议级别\n• 小额偏差自动处理，大额偏差 → 人工"]
    P2 --> P3["Phase 3 (6-12个月): Intent-driven\n• Orchestrator 自主拆解意图为任务\n• 子 Agent 在预算范围内自主决策\n• Session Key 基于信誉动态调整\n• 人工只在异常时介入"]
```

每个 Phase 的过渡条件：上一个 Phase 积累了足够的链上执行记录 + 信誉数据，证明 Agent 在受限范围内是可靠的。这就是 5/24 的"自增强信任循环"在协作场景中的应用。

---

## 8. 开放问题

- **Orchestrator 的单点风险**：所有协作都经过 Orchestrator，它被攻破 = 整个系统被攻破。去中心化的 Orchestrator 怎么做？多个 Orchestrator 的共识机制？
- **子 Agent 之间的利益冲突**：Aave Agent 和 Compound Agent 可能各自"推销"自己的协议（因为操作越多 fee 越多）。如何保证 Orchestrator 的决策不被子 Agent 的"偏见"影响？
- **跨时区/跨链的协作**：Aave 在 Ethereum，Compound 在 Arbitrum，Uniswap 在 Optimism。跨链操作的原子性如何保证？失败时如何回滚已成功的链？
- **治理速度与 Agent 速度的失配**：DAO 投票需要 3-7 天，Agent 操作是分钟级。紧急情况（如协议被 exploit）如何快速治理响应？Guardian 机制 vs Optimistic Governance 的权衡。
