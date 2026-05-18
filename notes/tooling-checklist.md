# 课程工具准备 · Checklist

> Week 1 · 前置准备 +10
> 全部已在本机就绪,版本与路径如下。

---

## 工具栈与版本

| 工具 | 状态 | 版本 | 路径 / 备注 |
|---|---|---|---|
| **git** | ✅ | system | `/usr/bin/git` |
| **gh (GitHub CLI)** | ✅ | latest | `/opt/homebrew/bin/gh`,已登录 `beautifulrem` |
| **Node.js** | ✅ | v22+ | Homebrew,`/opt/homebrew/bin/node` |
| **Python 3** | ✅ | 3.x | `~/miniconda3/bin/python3` |
| **Claude Code** | ✅ | Opus 4.7 (1M ctx) | 全局 CLI,本仓主力 AI |
| **Foundry: forge** | ✅ | 1.5.1-stable | `~/.foundry/bin/forge` |
| **Foundry: cast** | ✅ | 同上 | `~/.foundry/bin/cast` |
| **Foundry: anvil** | ✅ | 同上 | 本地 EVM 实例 |
| Hardhat | ⛔ | 未装 | Foundry 已可替代 |
| **MCP Servers** | ✅ | n/a | claude-in-chrome / context7 / figma / github / playwright |
| **RTK (token saver)** | ✅ | 0.39.0 | 透明代理日常 dev 命令 |

---

## 仓库结构(已搭好)

```
ai-x-web3-school/
├── README.md               # 仓库导览
├── .gitignore              # 含 .env、forge cache、私钥保护
├── notes/
│   ├── concepts/           # AI / Web3 概念卡片 + 账户对比
│   ├── industry/           # 项目拆解 + 行业观察
│   └── tooling-checklist.md  ← 本文件
├── contracts/              # Foundry 项目
│   ├── foundry.toml
│   ├── src/HelloWeek1.sol      # 最小合约,5 个测试全过
│   ├── test/HelloWeek1.t.sol
│   ├── script/Deploy.s.sol
│   └── lib/forge-std/
├── demos/
│   ├── concept-quiz/index.html         # 可交互产物
│   └── restricted-web3-helper/         # 受限助手 design
├── diagrams/mermaid/                   # AI × Web3 流程图源
├── diagrams/png/                       # 渲染结果
├── logs/                                # learning-agent-setup, agent-sessions
├── prompts/                             # 复用 prompt 库
├── resources/follow-list.md             # 行业信息流
└── pow-pack/week-1/                     # Week 1 综合产物
```

---

## 验证命令(每个都跑过)

```bash
# 工具版本
git --version && gh --version && node --version && python3 --version
forge --version && cast --version

# GitHub 登录
gh auth status

# Foundry 编译 + 测试
cd contracts && forge build && forge test -vv

# Restricted Web3 Helper 自检
cd demos/restricted-web3-helper && python3 guardrails.py
```

---

## 风险与边界

- **mainnet 私钥**:完全未配置,本仓 `.env` 仅含 Sepolia 测试钱包
- **缺 Chrome (puppeteer)**:`mermaid-cli` 渲染失败,改用 mermaid.ink 远程渲染
- **API Key**:本仓无任何线上 LLM API Key;Claude Code 用 CLI 内置鉴权,不出现在文件里
- **Faucet ETH**:Sepolia 钱包 `0x3D58...d2B8` 余额为 0,等真实部署再领

---

## 已读 / 已订阅信息源

见 [`resources/follow-list.md`](../resources/follow-list.md):AI / Web3 / 跨界各一份,信息卫生纪律也在文件里。
