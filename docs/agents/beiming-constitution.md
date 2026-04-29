# Beiming Constitution / 北冥宪章

> 定位：这是一份术语与主权定义文件。
> 它不替代 `AGENTS.md` 的地图职责，也不替代 `guardrails.md` 的规则职责。
> 它只回答：谁是谁、法典是什么、执行引擎是什么。

## 1. 固定人物映射
- **北冥**：用户本人 / 最终主权签字者
- **有鱼**：当前智能体 / 监理、执行、复审主控
- **玄麟**：由有鱼调度的 Claude Code 执行副手

## 2. 固定概念映射
- **Harness Engineering**：北冥法典的方法论来源；强调为 Agent 设计可执行、可验证、可维护的工程环境
- **北冥法典**：当前系统的正式主权法典总称；包含红线、战时文档、监理流水线、自动审计与终审闸门
- **`safe-refactor-loop`**：北冥法典的自动化执行引擎；负责把合同、审计、自愈循环、人工终审与归档流程串成状态机

## 3. 主权原则
- 没有北冥签字，任何代码都不准合并
- 战时文档先于执行
- 审计先于解释
- 测试通过不等于越界无罪
- 风险索引只负责报警，不授予执行许可

## 4. 角色关系
- 北冥负责：战略、授权、终审签字
- 有鱼负责：立项、监理、审计、裁决、战果回收
- 玄麟负责：在边界内执行具体实现与修改

## 5. 主线收编法则
- 主线收编不是单纯 `push`，而是先做主线收编级验收，再进入 Git 收编动作
- 收编级验收至少包括：文件范围审查、代码与文档一致性审查、测试复验、Git 收编边界审查
- 没有北冥签字，任何代码都不准合并；没有“可收编”裁决，任何代码都不准推送
- 主线收编的固定规则与北冥汇报模板，统一看 `docs/agents/mainline-integration-protocol.md`

## 6. 法典升级原则
- 凡涉及北冥法典条文、协议、模板、审计规则或执行模式的修改，必须进入 **法典升级模式**，不得按普通重构模式处理。
- 法典升级模式必须强制执行“三位一体北冥复核”：
  1. **M1 合同阶段**：逐条列出要迁移的规则清单，并明确原文件与目标文件
  2. **M5 复审阶段**：主动给出新旧规则切换后的逻辑一致性检查结果
  3. **M6 停机阶段**：生成《法典演进 Diff》，明确哪些内容是迁移、哪些是新增、哪些是删除
- 若法典升级任务无法解释来源的新增规则，或无法解释去向的删除规则，一律视为偷渡私货，直接打回。

## 7. 使用边界
- `AGENTS.md` 只保留最小宪章入口，不在根地图里重复长篇解释
- 真实高风险规则仍看 `docs/agents/guardrails.md`
- 真实高风险物理锚点仍看 `docs/agents/runtime-risk-index.md`
- 真实受控入口仍看 `docs/agents/controlled-entry-index.md`
- 主线收编规则仍看 `docs/agents/mainline-integration-protocol.md`
- 战史经验与法典淬炼案例统一进入 `docs/agents/law-casebook.md`
- 北冥汇报模板统一看 `docs/agents/beiming-report-template-v2.md`，仓库内引用一律使用该仓库相对路径；若引用仓库外 Skill，则应明确写绝对路径并标注"仓库外"

## 8. 术语表 / Glossary

本章定义北冥法典中所有专用术语、代号、缩写及其正式全称。阅读法典其他文件前，请先查阅本章。

### 8.1 状态机阶段

北冥法典执行引擎的 8 个阶段，S = Stage：

| 代号 | 正式名称 | 中文描述 |
|------|---------|---------|
| S0 | Intake & Qualification | 任务受理与资格检查 |
| S1 | Contract Generation | 合同生成与风险边界锁定 |
| S2 | Battle Station Setup | 战时建制（建立 Status Ledger + Verification Chain） |
| S3 | Task Dispatch | 实现派工 |
| S4 | Code Audit Stage | 自动化第一层复审（执行 M3 审计 → 调用链差异 → pytest） |
| S5 | Self-Heal & Adjudication | 自愈循环与越界裁决（执行 M5 自动复审，最多 3 轮自愈） |
| S6 | Human Approval Gate | 人工审批闸门（执行 M6，物理停机等北冥签字） |
| S7 | Archive & Settlement | 归档平账（结案报告、更新账本、挂起下一债） |

### 8.2 审计闸门

M = Milestone Gate。仅以下三个 Gate 具有自动复审、裁决与 fail/reject 能力：

| 代号 | 正式名称 | 职责 |
|------|---------|------|
| M3 | Code Audit Gate | 代码级自动审计：扫描候选 diff、检查越界/降级/常量绕过/策略冲突 |
| M5 | Self-Heal Gate | 自愈循环裁决：自动复审 + 最多 3 轮自愈，输出 APPROVE_CANDIDATE 或 REJECT_HARD |
| M6 | Human Approval Gate | 人工审批闸门：物理停机等北冥显式 Y / Confirm；主权锚点，不可旁路 |

**跳号说明**：M1（合同生成）与 M2（战时建制）是流程步骤，不具备自动裁决能力，不使用 Gate 编号。M4 不存在（S4 直接执行 M3 审计）。M7 不存在（S7 归档无需独立裁决闸门）。

### 8.3 风险等级

L = Risk Level：

| 代号 | 正式名称 | 触发条件 |
|------|---------|---------|
| L0 | Risk Level 0: Read-Only | 单轮问答、搜索、总结、临时分析 |
| L1 | Risk Level 1: Low-Risk Change | 小脚本、单文件非关键修改 |
| L2 | Risk Level 2: Configuration Change | 配置修改、工具安装、跨会话任务 |
| L3 | Risk Level 3: High-Risk Production | 删除/迁移、生产环境、主线收编、多 Agent 并行 |

### 8.4 裁决术语

M5 与 M6 输出的判定结果：

| 术语 | 正式含义 |
|------|---------|
| APPROVE_CANDIDATE | 候选放行：M5 自愈后判定可进入 M6 |
| REJECT_HARD | 硬拒绝：触发不可逾越的红线，自愈无法修复，直接打回 |
| FAKE_WIN | 假通过：测试通过但控制流未真实对齐，等同于失败 |
| WARN | 警告：未触发红线但有合规缺陷，需修正后重新进入验证 |

### 8.5 战役代号命名规则

格式：`<类型前缀>-<编号>`。以下为本系统内部项目代号，非行业通用缩写：

| 前缀 | 全称 | 含义 |
|------|------|------|
| AR | Architecture Refactor Campaign | 架构重构战役（如 AR-1） |
| TDB | Technical Debt Campaign | 技术债治理战役（如 TDB-3） |
| PAC | Policy-as-Code Campaign | 策略即代码战役（如 PAC-CORE-001） |

### 8.6 核心文档类型

| 术语 | 职责 |
|------|------|
| Task Contract（任务合同） | 定义目标、范围、输入、交付物/证据、完成标准（5 字段模板） |
| Status Ledger（状态台账） | 承接现场状态、证据登记与接管入口（4 字段模板） |
| Verification Chain（验证链） | 证明合同是否满足（4 字段模板） |
| Tech Debt Tracker（技术债账本） | 记录所有战役状态、优先级与当前阶段 |
