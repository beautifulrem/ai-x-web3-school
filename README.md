# AI × Web3 School — Personal Learning Workspace

> Student: **beautifulremi** (学号 3553) · Cohort: Spring 2026 · 共学营 by ETHPanda × LXDAO

This repo is my Week-1 onward learning workspace for the **AI × Web3 School** — a single source of truth for every concept note, prompt, demo, log, on-chain artifact, and Proof-of-Work submission I produce during the program.

---

## 仓库地图

| 路径 | 用途 |
|---|---|
| `notes/` | 概念卡片、读书笔记、回放笔记、每周总结 |
| `prompts/` | 复用 prompt 库 (concept-card 生成、流程图描述、研究问询等) |
| `demos/` | 可交互学习产物 (CLI、小页面、quiz、卡片) |
| `contracts/` | Foundry 智能合约工程 (Sepolia 测试网) |
| `scripts/` | cast/forge 脚本、自动化、API 调用样例 |
| `diagrams/` | AI × Web3 流程图、架构图 (Mermaid + 导出 PNG) |
| `logs/` | Agent 协作日志、调研过程、决策记录 |
| `resources/` | 链接库 (officials、tutorials、industry follow-list) |
| `pow-pack/` | Week 1 综合 Proof-of-Work 打包目录 |

---

## 工具栈

| 层 | 选型 | 备注 |
|---|---|---|
| **AI Coding Agent** | Claude Code (Opus 4.7) | 本地 CLI · 主力 |
| **辅助 LLM** | ChatGPT / Gemini / Grok 网页版 | 同任务对比、分工 |
| **Web3 工具链** | Foundry (`forge` + `cast`) | EVM 合约、链上交互 |
| **链** | Sepolia 测试网 | Faucet:[官方](https://sepoliafaucet.com) |
| **MCP 服务器** | claude-in-chrome / context7 / figma / github / playwright | 浏览器自动化、文档拉取、设计、版本控制 |
| **Token 优化** | RTK (Rust Token Killer) | 透明代理,日常 dev 命令降本 60–90% |

---

## Week 1 学习目标(摘录自课程页)

1. 理解 LLM / prompt / workflow / agent / tool use / AI coding 的基本概念
2. 理解账户、钱包、签名、交易、Gas、合约、测试网、区块浏览器如何构成一条链上操作链
3. 至少完成:一次 AI 工具实践 + 一次测试网交互 + 一个 AI × Web3 最小交叉实验
4. 建立权限、安全、人工确认、日志、验证材料和失败恢复意识

---

## 学习方法论(自己定的约束)

- **三家 LLM 交叉验证**:任何一份概念卡片或关键判断先让 ChatGPT/Gemini/Grok 各产一版,人工比对再入仓
- **源驱动**:优先官方文档(Anthropic Docs、Ethereum.org、Foundry Book、OpenZeppelin、ERC-4337),配合 context7 MCP 拉最新版本
- **链上前测试网,合约前测试**:任何写动作先测试网 + Foundry test,再考虑主网
- **AI 输出五重校验**:事实错误 / 引用错误 / 推理漂移 / 执行越权 / 工具误用 — 五条都过再相信
- **人工确认节点**:涉及签名、转账、合约写入、社交发布,必须人工 confirm,Agent 不直接执行

---

## 公开声明

- 笔记可能公开,**绝不**写入私钥 / 助记词 / API Key / 密码
- 测试网钱包独立于个人主钱包,即使泄露损失也仅限于水龙头币
- 链接到外部源时优先官方,二手内容标记来源
