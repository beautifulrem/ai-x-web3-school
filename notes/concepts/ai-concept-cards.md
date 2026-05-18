# AI 基础概念卡片 · Week 1

> 八张卡片,从 LLM 走到 MCP。每张控制 200–250 字,讲程序员能立刻用的细节,不写空话。
> 锚点优先官方文档。

---

## 卡片 1 — LLM (Large Language Model)

**一句话定义**:基于海量文本训练、用概率预测下一个 token 的神经网络。

**核心机制**:本质是一个函数 `f(tokens) -> probability_distribution`。输入文本切成 token 序列,Transformer 注意力层逐层计算,最终在词表上输出概率分布,采样得到下一个 token,循环直到结束符或上限。权重在训练后冻结,推理时无状态。

**能做什么**:
- 生成、改写、翻译、分类、抽取结构化数据
- 在上下文内做模式匹配与少样本推理

**不能做什么**:
- 不能真正"记住"会话(全靠 context 喂)
- 不能保证事实正确,会自信地编造

**常见误区**:把 LLM 当数据库查询,它给你的是「最可能的下一句话」,不是检索结果。

**官方锚点**:https://docs.anthropic.com/en/docs/about-claude/models/overview

---

## 卡片 2 — Prompt

**一句话定义**:喂给模型的输入文本,决定本次推理的全部行为。

**核心机制**:Prompt 在 API 层通常是 `messages: [{role, content}]` 数组,包含 system、user、assistant 三类角色。模型把整个数组拼成单一 token 序列做条件生成,所以"系统提示"和"用户消息"对模型而言只是位置不同的上下文,没有特权。

**能做什么**:
- 通过角色设定、示例、约束改变输出分布
- 用结构化标签(XML/JSON)提升解析稳定性

**不能做什么**:
- 不能突破模型能力上限,只能调用已有能力
- 不能持久生效,每次请求都要重发

**常见误区**:以为"加一句别幻觉"就能消除幻觉,实际只有结构、示例、工具才有用。

**官方锚点**:https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview

---

## 卡片 3 — Workflow(与 Agent 的边界)

**一句话定义**:由代码预先编排 LLM 调用路径的确定性流程。

**核心机制**:开发者用代码写好步骤,例如"先抽取 → 再分类 → 再总结",每步是一次固定 prompt 的 LLM 调用,分支由代码 `if/else` 决定。LLM 只负责单步语言处理,不决定下一步去哪。常见模式:prompt chaining、routing、parallelization。

**能做什么**:
- 在已知任务上获得可预测、可测试的结果
- 控制 token 成本和延迟

**不能做什么**:
- 不能处理路径未知的开放任务
- 不能在运行时自适应新工具

**常见误区**:把所有 LLM 应用都叫 Agent,其实 90% 的生产系统是 Workflow,更稳更便宜。

**官方锚点**:https://www.anthropic.com/research/building-effective-agents

---

## 卡片 4 — Agent

**一句话定义**:由 LLM 自主决定下一步动作并循环调用工具的程序。

**核心机制**:核心是一个 while 循环:模型看上下文 → 输出工具调用 → 程序执行工具 → 结果拼回上下文 → 模型再决策,直到模型输出"停止"或触达上限。路径不由代码写死,由模型在运行时生成。

**能做什么**:
- 处理路径未知的多步任务(调试、检索、操作)
- 根据中间结果动态换策略

**不能做什么**:
- 不能保证步数和成本,可能死循环烧 token
- 不能在工具描述不清时做出正确选择

**常见误区**:以为 Agent 必然比 Workflow 强,实际只有任务真的需要动态决策时才值得用。

**官方锚点**:https://docs.anthropic.com/en/docs/agents-and-tools/overview

---

## 卡片 5 — Tool Use(Function Calling)

**一句话定义**:让模型输出结构化 JSON 来请求外部函数执行。

**核心机制**:开发者把工具定义(name、description、JSON Schema 的入参)随请求发给模型,模型若决定调用,会输出 `tool_use` 块附带参数 JSON。程序解析 JSON、执行真实函数、把 `tool_result` 拼回 messages,再请求模型继续。模型本身不执行任何代码。

**能做什么**:
- 让 LLM 操作数据库、API、文件系统
- 强制结构化输出(把 schema 当工具骗模型)

**不能做什么**:
- 不能保证参数 100% 合法,需校验
- 不能直接执行,工具运行在你的环境里

**常见误区**:把工具描述写得很短,模型选错或漏调,描述质量直接决定成功率。

**官方锚点**:https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview

---

## 卡片 6 — AI Coding(Claude Code / Codex / Cursor)

**一句话定义**:以 LLM 为内核、能读写代码库并执行命令的编程 Agent。

**核心机制**:本质是 Agent + 一组代码相关工具(Read、Edit、Bash、Grep)。模型在循环里搜代码、改文件、跑测试、看报错、再改。差异在于宿主:Cursor 在编辑器内联,Claude Code 在终端跑长任务,Codex 偏云端任务化执行。

**能做什么**:
- 跨多文件重构、定位 bug、跑测试闭环
- 把自然语言需求翻译成可运行的 diff

**不能做什么**:
- 不能理解未在上下文中的隐性约定
- 不能替代代码评审与架构判断

**常见误区**:以为它在"理解"代码,实际是基于上下文做模式匹配,上下文不全就会乱编。

**官方锚点**:https://docs.claude.com/en/docs/claude-code/overview

---

## 卡片 7 — Context Window

**一句话定义**:模型单次推理能容纳的 token 总数上限。

**核心机制**:Transformer 注意力在序列长度上是 O(n²) 的算力开销,所以模型有硬上限,例如 200K 或 1M token。所有 system、历史 messages、工具定义、工具结果都计入这个池子。超出就要截断或压缩,会话不会"自动记住"过去。

**能做什么**:
- 在窗口内做长文档 QA、跨文件代码分析
- 通过 prompt caching 复用前缀降本

**不能做什么**:
- 不能等同于记忆,跨会话信息必须自己存
- 不能保证窗口越长效果越好,长上下文会衰减

**常见误区**:把大窗口当垃圾桶塞,信息越多模型越容易迷路(lost in the middle)。

**官方锚点**:https://docs.anthropic.com/en/docs/build-with-claude/context-windows

---

## 卡片 8 — MCP(Model Context Protocol)

**一句话定义**:让 LLM 客户端与外部工具/数据源对接的开放协议。

**核心机制**:基于 JSON-RPC 的 client-server 协议。MCP server 暴露 tools、resources、prompts 三类能力;MCP client(Claude Code、Claude Desktop 等)在启动时连接 server、拉取能力清单,运行时把工具注入到模型的 tool 列表。一次写 server,任意兼容客户端可用。

**能做什么**:
- 把企业内部 API、数据库标准化暴露给任意 LLM 客户端
- 解耦工具实现与模型宿主

**不能做什么**:
- 不能替代鉴权与权限控制,需自己实现
- 不能让不支持 MCP 的模型直接用

**常见误区**:以为 MCP 是 Anthropic 私有的,实际是开放协议,OpenAI、Google 客户端也在接入。

**官方锚点**:https://modelcontextprotocol.io/introduction
