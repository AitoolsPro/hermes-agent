## Task Contract（任务合同）

**Objective (目标)**  
在干净 `origin/main` 基线上，把北冥法典当前缺失的主干文档与 P0 / P1 / P2 / P3 的合格文档增强成果收编到独立 worktree 中，形成一次单一、可审计、仅含文档/协议/战时蓝图的主线候选提交。

**Scope / Watchouts (范围 / 警戒线)**  
IN: 只在独立 worktree `/private/tmp/beiming-law-mainline` 内恢复并校验以下对象：`docs/agents/beiming-constitution.md`、`docs/agents/beiming-report-template-v2.md`、`docs/agents/law-casebook.md`、`docs/agents/task-routing-matrix.md`、`docs/agents/mainline-integration-protocol.md`、P0 / P1 / P2 三组战时文档、`docs/exec-plans/in-progress/ar-1-engineering-wiring-blueprint.md`，以及本轮主线收编任务自身的合同 / 台账 / 验证链。  
OUT: 不改任何业务代码、运行时代码、测试代码；不改 M3 / M5 / M6 判定逻辑；不改 Git 工作流原则；不改任何 `REJECT_HARD` / `FAKE_WIN` / `APPROVE_CANDIDATE` 条件；不混入 PAC-CORE-001 代码核心、AR-1 代码战成果或仓库外 Skill 文件；未获北冥 `Y / Confirm` 前不 push。  
WATCHOUTS: 最大风险是把脏主仓中的无关改动或代码原型混入主线候选；第二风险是把“现场恢复”误当作“现场存在”而脑补缺失文档；第三风险是把文档收口扩张成新法典工程；第四风险是未完成四类主线收编验收就提前进入 Git 动作。

**Inputs (输入)**  
`docs/agents/mainline-integration-protocol.md`、`docs/exec-plans/tech-debt-tracker.md`、仓库外 `/Users/beiming/.hermes/skills/safe-refactor-loop/SKILL.md`、来源工作区 `~/.hermes/hermes-agent` 的 P0 / P1 文档、来源 worktree `/private/tmp/p2-task-routing-matrix` 的 P2 文档、来源 worktree `/private/tmp/p3-ar1-wiring-prep` 的 P3 蓝图；用户明确要求基线必须是干净 `main`，若本地 `main` 不等于 `origin/main` 则以 `origin/main` 建立 worktree。

**Deliverables / Evidence (交付物 / 证据)**  
交付物：独立 worktree 中的合法候选文件集合、单一候选提交、本轮主线收编合同 / 台账 / 验证链、最终北冥汇报与《北冥裁决请示书》（若达到 APPROVE_CANDIDATE）。  
证据：`git rev-parse` 证明 worktree 基于 `origin/main`；文件存在性检查证明目标文档物理落地；范围审查清单证明纳入/排除边界清楚；关键词与引用检查证明法典五层物理成立、关键引用正常、未混入代码战成果；`git status --short`、`git diff --cached --stat`、`git show --stat --summary HEAD` 证明候选为单一可审计文档提交。

**Done (完成标准)**  
1. 独立 worktree 已基于干净 `origin/main` 建立并作为唯一收编战场；  
2. 用户点名的 15 个目标文件已真实恢复到候选 worktree，且来源可解释；  
3. 四类主线收编验收全部通过：文件范围审查、代码与文档一致性审查、结构验证、Git 收编边界审查；  
4. 候选提交只包含本轮合法文档 / 协议 / 战时蓝图与本轮主线收编现场文档；  
5. 若达到 `APPROVE_CANDIDATE`，已完成 commit 但停在 M6，未获北冥签字前未 push。
