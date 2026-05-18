# On-Chain Proof · Sepolia · Week 1

> 2026-05-19 · 部署 HelloWeek1 + 一笔 greet() 写入 · 两笔 tx 已确认

---

## 网络
- **Chain**: Sepolia (chainId 11155111)
- **RPC**: https://sepolia.drpc.org

## 部署者
- **Address**: `0xbA64397d50D71fE0c38a86B51fc77BedB580C8A4`
- (此地址非个人主钱包,Sepolia 测试用;私钥不入 repo)

## 部署 — `forge script Deploy.s.sol --broadcast`

| 字段 | 值 |
|---|---|
| Tx hash | `0xc4d3c164cc4ef06ce88fea7d6ee89e6ef4d9fc3074232509b445e2a885475f10` |
| Contract address | `0x4787F749E8D6C872D81437aa9d1d63bD395cB677` |
| Block | 10876277 |
| Gas used | 401,366 |
| Effective gas price | 0.001000014 gwei |
| Status | ✅ Success (0x1) |
| Initial greeting | "GM AI x Web3 School" |

**区块浏览器(任选)**
- Etherscan: https://sepolia.etherscan.io/tx/0xc4d3c164cc4ef06ce88fea7d6ee89e6ef4d9fc3074232509b445e2a885475f10
- 合约页:https://sepolia.etherscan.io/address/0x4787F749E8D6C872D81437aa9d1d63bD395cB677
- Blockscout:https://eth-sepolia.blockscout.com/address/0x4787F749E8D6C872D81437aa9d1d63bD395cB677

## 第一笔写入 — `cast send greet(string)`

| 字段 | 值 |
|---|---|
| Tx hash | `0x3e6e3a4b7717c43739044a3960f7cbb67495ddd57d3c3ace88bbc2e9cd83f96e` |
| Block | 10876279 |
| Gas used | 97,005 |
| 调用 | `greet("GM from beautifulremi - Week 1 done!")` |
| Event | `Greeted(caller=0xbA64...c8A4, newGreeting=...)` |
| Status | ✅ Success |

**区块浏览器**
- Etherscan: https://sepolia.etherscan.io/tx/0x3e6e3a4b7717c43739044a3960f7cbb67495ddd57d3c3ace88bbc2e9cd83f96e
- Blockscout: https://eth-sepolia.blockscout.com/tx/0x3e6e3a4b7717c43739044a3960f7cbb67495ddd57d3c3ace88bbc2e9cd83f96e

## 链上状态验证

```bash
$ cast call 0x4787F749E8D6C872D81437aa9d1d63bD395cB677 'greeting()(string)' \
    --rpc-url https://sepolia.drpc.org
"GM from beautifulremi - Week 1 done!"

$ cast call 0x4787F749E8D6C872D81437aa9d1d63bD395cB677 'greetCount()(uint256)' \
    --rpc-url https://sepolia.drpc.org
1
```

`greeting()` 与 `greetCount()` 与写入 tx 一致,合约状态与预期对齐 — 完成"AI 输出 → 人工复核 → 链上执行 → 验证"的最小闭环。

## 流程闭环 (与 [`diagrams/png/ai-x-web3-min-cross-flow.png`](../../diagrams/png/ai-x-web3-min-cross-flow.png) 对照)

1. **计划层**:Claude Code 写 Solidity + 部署脚本
2. **复核层**:5 个单测全过 + 人工 review 合约逻辑(权限边界:仅 deployer 可 reset)
3. **执行层**:`forge script --broadcast` + `cast send` 两条命令
4. **验证层**:tx hash + receipt + 链上 state 三重比对
5. **可观测层**:broadcast/ JSON + receipt + 本文档

完整闭环跑通,本周"最小交叉实验"完成。
