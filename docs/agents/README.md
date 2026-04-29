# 北冥法典

AI Agent 治理的状态机闭环系统。定义谁有权做什么、什么算完成、怎么执行、怎么证明、怎么汇报。

## 阅读路径

| 你是谁 | 先读 | 再读 | 需要时查 |
|--------|------|------|----------|
| 新人（第一天） | 宪章 §1-4 + §8 术语表 | — | — |
| 执行者（要开工） | 宪章 §5-6 | 主线收编协议 | 汇报模板 |
| 审计者（要复审） | safe-refactor-loop 状态机 | 宪章 §8 | 案例书 |
| 法典维护者（要改法） | 宪章 §6 法典升级原则 | safe-refactor-loop 法典升级模式 | 案例书 |

## 文件地图

| 文件 | 职责 |
|------|------|
| `beiming-constitution.md` | 术语、主权、角色、法典层级 |
| `mainline-integration-protocol.md` | 主线收编固定检查项与红线 |
| `law-casebook.md` | 实战淬炼案例 |
| `beiming-report-template-v2.md` | 11 字段强制汇报格式 |
| `guardrails.md` | 风险边界、验证与交接纪律 |
| `runtime-risk-index.md` | 运行时高风险物理锚点索引 |
| `controlled-entry-index.md` | 高风险点到受控入口的映射 |

## 执行速查

| 任务类型 | 风险等级 | 走什么流程 |
|----------|---------|-----------|
| 问答 / 搜索 | Risk Level 0: Read-Only【L0】 | 直接执行 |
| 小脚本 / 单文件改 | Risk Level 1: Low-Risk Change【L1】 | 直接改，保留 diff |
| 配置 / 跨会话 | Risk Level 2: Configuration Change【L2】 | 先备份，建轻量台账 |
| 删除 / 生产 / 主线 | Risk Level 3: High-Risk Production【L3】 | 完整 S0-S7 + M6 签字 |

## 关键原则

- 没有北冥签字，任何代码都不准合并。
- 测试通过不等于越界无罪。
- 合同先于执行，证据先于结论。
- 任务现场状态进入 Status Ledger，不写入 memory。
