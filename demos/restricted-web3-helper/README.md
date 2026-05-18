# Restricted Web3 Helper — 一个"绝不自动广播"的小 workflow

> Week 1 综合进阶任务(+40)· 设计目标:让 AI 帮你理解和准备链上动作,但任何写动作都强制人工确认才能执行。

---

## 设计哲学

AI Agent 一旦进入"会发交易"的领域,blast radius 立刻变成钱。这个 helper 的核心立场是:

1. **读链可以自动**:查余额、读合约 storage、解析 tx、看 events — 全部允许 Agent 自主完成
2. **写链不能自动**:转账、approve、合约调用 — Agent **只能生成 calldata**,不能直接广播
3. **签名必须人工**:私钥永远不进入 Agent 的进程内存,广播由用户自己拷出命令在另一个终端执行
4. **每一步都留痕**:所有意图、解析结果、用户最终选择都进 `logs/agent-sessions/`

---

## 能做(允许的 8 类动作)

| # | 动作 | 接口 |
|---|---|---|
| 1 | 查地址余额 | `cast balance` |
| 2 | 查合约 storage 槽位 | `cast storage` |
| 3 | 解析交易回执 | `cast receipt` |
| 4 | 解析 calldata 成 human-readable | `cast 4byte-decode` + ABI |
| 5 | 估算 gas | `cast estimate` |
| 6 | 给一个 calldata 生成"它会做什么"的自然语言描述 | LLM 解释 |
| 7 | 检查合约是否 verified、是否 proxy | Etherscan API |
| 8 | 检查地址是否进 Chainalysis / 安全名单 | Forta API(可选) |

## 不能做(明确拒绝的 5 类动作)

| # | 动作 | 拒绝理由 |
|---|---|---|
| 1 | 任何 `cast send` / `forge create` 直接广播 | 写链动作必须人工 |
| 2 | 任何形式的 `--private-key` 或 keystore 解锁 | 私钥绝不进 Agent 进程 |
| 3 | 自动 approve token / Permit 签名 | 钓鱼签名最大攻击面 |
| 4 | 跨地址转账(包括"看起来很小的金额") | 上限就是损失上限 |
| 5 | 在主网上做任何写动作(没人工 review 的情况下) | 测试网先 |

## 必须人工确认才执行(2 类灰色)

1. **生成的 calldata 拷给用户**:用户在另一个终端用自己的钱包广播,Agent 不参与签名
2. **测试网部署 / 调用**:Agent 可以构造完整 `forge script` 命令,但执行前必须显示"⚠️ 即将广播,请确认网络与 contract 地址 (Y/N)"

---

## 文件结构

```
restricted-web3-helper/
├── README.md           # 本文件
├── helper.py           # 主入口 (Python)
├── tools.py            # 工具函数:cast 调用、ABI 解析
├── guardrails.py       # 拒绝清单 + 人工确认 prompt
└── examples/
    ├── 01-read-balance.md
    ├── 02-explain-calldata.md
    └── 03-prep-deploy.md
```

## 一个最小可跑实现

`helper.py`(下面是核心循环,完整代码在同目录文件):

```python
def main():
    while True:
        cmd = input("\n[helper] > ").strip()
        if not cmd: continue
        if cmd in ("exit", "quit"): break

        # 1. 通过守卫
        if not guardrails.allow(cmd):
            print(guardrails.reason(cmd))
            log_decision(cmd, "REJECTED", guardrails.reason(cmd))
            continue

        # 2. 路由到只读工具
        result = tools.dispatch(cmd)

        # 3. 用 LLM 解释结果(可选)
        explanation = llm.explain(result) if "--explain" in cmd else None

        # 4. 落盘
        log_decision(cmd, "OK", result, explanation)
        print(result)
        if explanation: print("\n[解释]\n" + explanation)
```

## 失败模式分析

设计这种 helper 时最容易踩的坑:

1. **以为"只读"安全** — 读 storage 没问题,但若 helper 替用户做"模拟交易",可能调用恶意合约的 fallback,gas 估算虽然失败也已造成网络流量与指纹暴露。**对策**:读合约前先查 verified 状态与字节码大小,异常字节码先警告
2. **以为"测试网"安全** — 测试网地址同步到主网很常见(同一私钥可在所有 EVM 链),所以 helper 的测试钱包**绝不能与主网共用密钥**。**对策**:写一个 startup check,如果 `PRIVATE_KEY` 对应地址在主网上有过任何 tx,直接拒绝启动
3. **以为"日志"安全** — 默认日志可能把 calldata 整段写入,含敏感参数。**对策**:`logs/` 目录单独 gitignore,且 helper 退出前 prompt 用户确认是否清除
4. **以为"人在 loop"等于安全** — 用户疲劳后会盲点 Y。**对策**:每条人工确认 prompt 都显示"接下来会写到哪条链、目标合约、value 多少、可能损失上限",让人无法盲签

---

## 演示场景

### 场景 A:用户问"我钱包里 XYZ token 多少"
- helper 解析:这是只读 → 允许
- 走 `cast call XYZ_TOKEN_ADDR balanceOf(WALLET)` → 返回 raw u256
- LLM 把 18-decimal 数字转 human-readable + 时间戳 + 给个对比"你 7 天前是 X"
- 日志:`READ balanceOf XYZ 12345.67 USDC at 2026-05-19`

### 场景 B:用户问"帮我 swap 100 USDC 到 ETH"
- helper 解析:这是写动作 → **拒绝**
- 但允许生成:"目标 Uniswap V3 Router(0xE592...) 的 exactInputSingle(USDC, WETH, 0.05%, recipient, 100e6, ...) calldata 长这样"
- 给出完整 `cast send` 命令模板,留 `--private-key` 字段为空
- 提示用户:"请在另一个终端用你的钱包(MetaMask/Rabby/Frame)广播这条 calldata"
- 日志:`PREP_SWAP USDC->ETH 100 USDC calldata=0x123... user_must_sign`

### 场景 C:用户问"这个合约的 owner 是谁"
- helper 路由:`cast storage CONTRACT 0` 拿原始数据
- LLM 解释:"slot 0 通常是 OpenZeppelin Ownable 的 _owner,这里 0xABC... 看起来是 EOA,你可以在 Etherscan 查它最近 7 天的 tx"
- 给一句风险提示:"如果这是个值钱合约,这个 EOA 一旦被钓鱼,你也跟着倒霉"

---

## 它在 Week 1 体系里的位置

| 课程模块 | 这个 helper 覆盖了什么 |
|---|---|
| 模块 A:LLM → Agent | 演示了 "tool calling + guardrails" 的最小骨架 |
| 模块 B:Web3 基础 | 演示了 EOA 私钥不进 Agent 的"必要分离" |
| 模块 C:最小交叉实验 | 完整跑通 "AI 生成 → 人工复核 → 用户自签 → 链上执行 → 链下验证" |

## 后续可扩展

- 接 MCP server 暴露给 Claude Code 直接调用
- 加 Session Key 路径,允许 helper 在限额内 auto-broadcast(但保留 kill switch)
- 接 Forta / Chainalysis 做主动风险预警
- 加交易模拟器(Tenderly API)在广播前 dry-run
