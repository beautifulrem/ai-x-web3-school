# Learning Agent Setup · Claude Code 作为 Week 1 主工具

> Week 1 · AI 向任务 +20

---

## 选型

| 候选 | 我为什么选它 |
|---|---|
| **Claude Code (Opus 4.7, 1M context)** ✅ | 1M context 适合长任务、跨多文件;在终端跑,与 forge/cast/gh 无缝;支持 MCP、SubAgent、并行 fan-out |
| Codex CLI | 也好,但我没有 OpenAI Plus 订阅,且 SubAgent 流程不如 Claude Code 成熟 |
| Hermes Agent | Web3 友好但更适合"长期 workflow",不是日常 dev |

**结论**:Week 1 用 Claude Code 作为主入口,Hermes 留到 Week 2+ 做"长期任务执行层"。

---

## 配置清单(均已生效)

### 1. CLI 安装与登录

```bash
# 已装(本机版本)
claude --version          # 0.x.x (Opus 4.7)
gh auth status            # Logged in to github.com as beautifulrem
forge --version           # 1.5.1-stable
cast --version            # 同 forge 一起装

# Claude 设置
~/.claude/settings.json   # 全局
~/.claude/CLAUDE.md       # 全局 user instructions(已配 RTK)
```

### 2. 接入的 MCP 服务器

| 名 | 用途 | Week 1 用例 |
|---|---|---|
| `claude-in-chrome` | 浏览器自动化(读/点/输入/截图) | 抓课程任务详情、跑 quiz demo |
| `context7` | 拉官方文档实时版本 | 查 Anthropic Docs / Foundry / OpenZeppelin |
| `figma` | 设计稿读写 + diagram 生成 | 后续可视化产物 |
| `github` | GitHub API | 提 issue / 看 PR / 推文件 |
| `playwright` | 备用浏览器自动化 | E2E 测试场景 |

### 3. 全局 user instructions

已加 `RTK.md`(Rust Token Killer)路径,所有日常 git / gh / forge 命令透明代理,降低 60-90% token。

### 4. SubAgent 类型(本周已使用)

- `general-purpose` — 调研 + 撰写(本周 3 个并行实例:AI 卡片、Web3 卡片、项目拆解)
- `agent-skills:code-reviewer` — 提交前 review
- `agent-skills:security-auditor` — 涉及合约必走
- `feature-dev:code-architect` — 大设计前用

---

## 已跑通的真实任务(本周内,均有 commit 凭证)

| 任务 | Claude Code 做了什么 | 产物路径 |
|---|---|---|
| 仓库初始化 | `gh repo create` + 8 个子目录 + README | `https://github.com/beautifulrem/ai-x-web3-school` |
| 8 张 AI 概念卡片 | 派 general-purpose 子代理产初稿,我精修后入库 | `notes/concepts/ai-concept-cards.md` |
| 8 张 Web3 概念卡片 + EOA/SCW/多签对比 | 同上 | `notes/concepts/web3-concept-cards.md`、`...account-comparison...` |
| 2 个项目拆解 | 同上,带官方源验证 | `notes/industry/project-teardown-week1.md` |
| Foundry 合约 + 5 个单测全过 | 直接生成 src/test/script | `contracts/src/HelloWeek1.sol` 等 |
| AI × Web3 最小交叉流程图 | Mermaid + mermaid.ink 渲染 | `diagrams/png/ai-x-web3-min-cross-flow.png` |
| Concept Quiz HTML | 单文件 vanilla JS 互动 | `demos/concept-quiz/index.html` |
| Restricted Web3 Helper | guardrails + helper.py stub | `demos/restricted-web3-helper/` |
| 行业关注清单 | 三层信息源(官方/X/中文) | `resources/follow-list.md` |

---

## 工作流约束(我给自己定的)

1. **每个非平凡任务先 Plan**:不直接动键盘,先写 todo
2. **能并行就并行**:三家 AI(Claude / ChatGPT / Gemini / Grok 共四个端点)分工,subagent 跑长任务
3. **官方文档优先**:context7 拉文档;不轻信我自己的记忆
4. **commit 粒度小**:一类产物一个 commit,便于追溯
5. **不进私钥**:Claude Code 进程永不持有 mainnet 私钥;测试钱包(`0x3D58...d2B8`)独立、放 `.env`(gitignored)

---

## 失败 / 边界记录

- **mermaid-cli 缺 Chrome**:本地 mermaid 渲染失败,改用 mermaid.ink 远程渲染。教训:工具链依赖要早暴露
- **faucet 域名权限**:Claude in Chrome 对每个新域名都要 explicit permission,自动化跑 faucet 受限
- **多模型 token 配额**:免费 Gemini/Grok/ChatGPT 网页版没有 API key,只能手动复制问答,不能跑工具链
- **本机 npx puppeteer 缓存**:用 mermaid-cli 需要先 `npx puppeteer browsers install chrome-headless-shell`,本周决定绕开

---

## 下周可改进

- 给 `restricted-web3-helper` 接 LLM 解释(目前是 stub),并暴露成 MCP server
- Claude Code 加一个 hook:每次跑 forge / cast 自动 log 到 `logs/agent-sessions/`
- 试一次 `subagent-driven-development` skill 模式,跑一个完整 Week 2 任务

