# AI × Web3 · Week 1 Concept Quiz

> 一份单文件 HTML 可交互学习产物 · 5 题 AI + 5 题 Web3 · 答错有解释

## 跑起来

```bash
# 任选其一
python3 -m http.server 8000  # 然后浏览器开 http://localhost:8000
open index.html               # 直接 file:// 打开也行
```

## 设计思路

1. **覆盖 Week 1 的 8 张概念卡片**:LLM / Prompt / Workflow vs Agent / Tool Use / Context Window / MCP · 钱包 / 账户 / 签名 / Gas / 智能合约 / 测试网
2. **题目偏"反直觉"**:专挑常见误区(LLM 当数据库、签消息零风险、L2 gas 简单换算……),答错才能记牢
3. **答错给一句话解释**:不是"正解 = X",而是"为什么"。降低反复刷题的需要
4. **结果分段反馈**:满分给庆祝,80+ 给推进信号,50 以下回去重读卡片

## 全在一个文件

无构建、无依赖、无后端。一份 HTML 包含:
- CSS:深色 + 蓝紫渐变(AI 蓝 → Web3 紫)
- JS:vanilla 实现题目状态机
- 内容:全部 10 题 + 解释直接内联,便于 GitHub Pages 静态托管

## 后续可扩展

- Week 2+ 题目可以挂到同一份 `QUESTIONS` 数组
- 加 localStorage 记录正确率随时间变化
- 把"我能做 / 不能做"也单独出题型
