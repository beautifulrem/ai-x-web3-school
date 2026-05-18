# EOA / 智能账户 / 多签 — 权限差异对比

> Week 1 · Web3 向进阶任务(+30)
> 为什么 AI Agent 一旦触达"写动作",账户的权限边界就是安全边界。

---

## 对比表

| 维度 | **EOA** | **智能账户 (ERC-4337)** | **多签 (Safe)** |
|---|---|---|---|
| **持有形式 (Key Custody)** | 单一私钥,谁拿到谁全权控制 | 由 `owner` (可以是 EOA、Passkey、社交登录) 控制合约账户;私钥可替换 | N-of-M 个 owner 共同控制,每个 owner 自己保管一份私钥 |
| **签名验证逻辑 (Signature Verification)** | 链下 ECDSA (secp256k1) `ecrecover`,固定算法 | 合约里 `validateUserOp` 自定义,可接受 ECDSA、Passkey (secp256r1)、ZK、BLS,或 EIP-1271 `isValidSignature` | Safe 合约校验阈值 (threshold) 内的多个 owner 签名,支持 EIP-1271 嵌套验证 |
| **权限粒度 (Permission Granularity)** | 全有或全无,无法限额、限合约、限时间 | 支持模块化:Session Key (临时密钥)、限额、白名单合约、按 selector 限调用、过期时间 | 通过 Module / Guard 扩展实现限额、Spending Limit、Allowance Module、Role 模块 |
| **恢复方式 (Recovery)** | 仅靠助记词,丢即失 | 社交恢复 (Social Recovery)、Guardian、邮件 / Passkey、ZK 恢复均可由模块实现 | 通过更换 owner 实现 (剩余 owner 投票替换丢失 owner) |
| **标准 / 协议 (Standards)** | 协议内建 (Yellow Paper) | ERC-4337 (EntryPoint + UserOperation + Bundler + Paymaster);EIP-7702 让 EOA 临时变成 SCW | Safe 协议 (前 Gnosis Safe);兼容 ERC-1271、ERC-4337 模块 |
| **Gas 模型 (Gas Payment)** | EOA 必须自付 ETH | 可由 Paymaster 代付,支持 ERC-20 付费、赞助付费、gasless | 默认 owner 之一发起并付 gas;可通过 Relayer / 4337 兼容层让 Paymaster 代付 |

---

## 总结 — 给 AI Agent 的账户分层心智模型

AI Agent 一旦触达"写动作"(发交易、签 Permit、调用合约),账户的权限边界就是安全边界。把三种账户摆在一起看:

**EOA** 的权限是二元的——给了私钥就等于把整个钱包交出去,没有限额、没有撤销、没有最小权限。让 AI Agent 直接持有 EOA 私钥意味着它可以转走全部资产、签任何合约调用,这在生产环境基本不可接受。EOA 应只用于"代签证明"或"低价值热钱包"。

**多签 (Safe)** 适合机构和高价值金库——人为审批引入了延迟和审计,但要求每笔交易有人类参与,与 AI Agent 追求的"自动化执行"在节奏上冲突。Safe 适合做 Agent 的"上级账户":Agent 子账户的资金上限、模块授权、紧急冻结都从 Safe 管控。

**智能账户 (ERC-4337) + Session Key** 才是 AI × Web3 的关键基础设施。原因有三:

1. **最小权限**:Session Key 是临时密钥,可绑定到特定合约、特定方法 selector、单日限额、有效期。Agent 拿到的只是"在某 DEX 上每天最多花 50 USDC 兑换 USDT"的钥匙,而不是整个账户。即使被攻击,损失上限可预测。
2. **可撤销与可观测**:主账户可以随时撤销 Session Key、轮换、暂停,所有 UserOperation 都经过 EntryPoint,可被链上索引,审计追溯成本远低于 EOA。
3. **Gas 抽象**:Paymaster 让 Agent 不必持有 ETH 即可执行交易,可用 USDC、订阅付费或由项目方赞助——这是把 AI Agent 真正产品化的前提。

**简言之**:把 **Safe 当"金库与策略层"**,把 **ERC-4337 智能账户当"Agent 执行账户"**,把 **Session Key 当"具体任务的钥匙串"**,EOA 退化为签名工具。这套分层,才让"AI 自动上链"既敢用、也可控。

---

## 官方源

- [ERC-4337 EIP](https://eips.ethereum.org/EIPS/eip-4337)
- [Safe Docs](https://docs.safe.global)
- [Ethereum.org / Accounts](https://ethereum.org/en/developers/docs/accounts/)
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts)
- [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702) (EOA 临时挂载合约代码)
- [EIP-1271 — `isValidSignature`](https://eips.ethereum.org/EIPS/eip-1271)
