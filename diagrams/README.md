# Diagrams

## AI × Web3 最小交叉流程图

源文件:[`mermaid/ai-x-web3-min-cross-flow.mmd`](mermaid/ai-x-web3-min-cross-flow.mmd)

五层 + 横切可观测层:

| 层 | 谁主导 | 关键约束 |
|---|---|---|
| ① **计划层** | AI Agent | LLM 解析意图 → 生成 step + tool + 风险标签 |
| ② **复核层** | 人 + Guardrails | 高风险写入必须人工 review,calldata 可读 |
| ③ **执行层** | 智能账户 + 链 | Session Key 限额 + 白名单合约 + EIP-1559 广播 |
| ④ **验证层** | 区块浏览器 + 链下 | tx hash / events / state 与预期比对 |
| ⑤ **可观测层** | 横切 | Trace 日志、告警、成功率/gas/延迟指标 |

### 渲染

```bash
# 用任意 mermaid 渲染器,例如:
npx -y @mermaid-js/mermaid-cli -i mermaid/ai-x-web3-min-cross-flow.mmd -o png/ai-x-web3-min-cross-flow.png -b transparent
```

或直接粘贴 `.mmd` 内容到 https://mermaid.live/ 预览 / 导出 PNG。

### 设计理由

- **不是单向流水线**:验证层若不一致会回到失败回滚,人工介入循环
- **可观测层是横切**:每层都喂日志,便于事后归因
- **权限层级体现在执行层**:Session Key 是最小权限单位,智能账户上层挂着 Safe / EOA 才是策略层
- **失败比成功更重要**:三个 "bad" 出口(ABORT、FAIL)显式标红,提醒设计时不要假设成功路径
