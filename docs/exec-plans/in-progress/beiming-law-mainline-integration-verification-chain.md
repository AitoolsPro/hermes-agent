## Verification Chain（默认验证链）

**Verification Target (验证目标)**
- 对应合同项：对应本轮主线收编的交付物、证据与完成标准。
- 目标 1：证明本轮候选只包含合法收编文件，且纳入 / 排除边界清楚。
- 目标 2：证明法典主干五层与 P0 / P1 / P2 / P3 物理文件真实存在，并与用户点名对象一致。
- 目标 3：证明本轮结构验证通过，包括路径存在性、关键引用、关键词命中 / 去命中与 Git 状态一致性。
- 目标 4：证明候选提交基于干净 `origin/main`，且形成单一、可审计、未混入无关改动的文档提交。

**Verification Actions (验证动作)**
- 动作 1：列出候选 worktree 变更文件，逐个标注“纳入 / 排除 / 原因”。
- 动作 2：逐个检查用户点名目标文件在候选 worktree 中是否物理存在，并交叉核对来源工作区 / worktree 是否真实有源文件。
- 动作 3：执行路径存在性、关键引用与关键词检查，确认五层法典成立且未混入禁止对象。
- 动作 4：执行 Git 基线、索引、缓存 diff、提交摘要检查，确认基线为 `origin/main` 且候选提交单一可审计。

**Verification Result (验证结果)**
- 目标 1：通过 —— `git diff --name-status origin/main..HEAD` 与 `git show --stat --summary HEAD` 共同指向 18 个合法候选文件；纳入集合仅含 5 份法典主干/协议文档、P0 / P1 / P2 三组战时文档、P3 蓝图与本轮主线收编现场文档，排除了仓库外 Skill、completed 报告、账本变更、AR-1 代码文件与主仓无关脏改动。
- 目标 2：通过 —— 用户点名的 15 个目标文件已在候选 worktree 物理存在，且其来源分别可回溯到主仓工作区（P0 / P1）与 `/private/tmp/p2-task-routing-matrix`、`/private/tmp/p3-ar1-wiring-prep` worktree（P2 / P3）；未发现“汇报说完成但文件不存在”。
- 目标 3：通过 —— 路径存在性检查全部通过；`docs/agents/beiming-constitution.md`、`docs/agents/mainline-integration-protocol.md`、`docs/agents/beiming-report-template-v2.md` 的关键引用可搜索命中；模板中的固定 Session ID 兜底句式命中；主线协议对 `PAC-CORE-001|AR-1|TDB-` 搜索零命中，战史案例集中在 `docs/agents/law-casebook.md`。
- 目标 4：通过 —— `git rev-parse HEAD`、`git rev-parse origin/main` 与 `git merge-base HEAD origin/main` 在 commit 前同为 `aff80cea24fa19e5e296f91d68b1dbea9ba32159`，证明基线为干净 `origin/main`；当前单一候选提交为 `3d5aa0b5`，`git status --short` 已清空，边界可审计。

**Release / Handoff Gate (放行 / 接管闸门)**
- 当前判断：可收口
- 当前缺口：自动化验收已完成；仅缺北冥 M6 人工批准，未获 `Y / Confirm` 前不得 push。
- 接手后第一步：先向北冥提交 `3d5aa0b5` 的《北冥裁决请示书》，等待显式签字。
- 接手入口：先看 `docs/exec-plans/in-progress/beiming-law-mainline-integration-task-contract.md`、本验证链、`git show --stat --summary HEAD` 与最终汇报中的候选文件总表。
