## Verification Chain（默认验证链）

**Verification Target (验证目标)**
- 对应合同项：对应本轮交付物、证据与完成标准。
- 目标 1：证明 `docs/agents/task-routing-matrix.md` 已覆盖用户指定的 6 类任务。
- 目标 2：证明每类任务都明确写出“CLI 自动化引擎 / 当前聊天窗口 / 是否先隔离 worktree”的建议。
- 目标 3：证明决策表至少包含 1 套最适合 CLI 自动化的案例与 1 套更适合当前窗口直接做的案例。
- 目标 4：证明本轮改动只停留在文档与任务现场文件，没有触碰代码、测试、执行逻辑与 M3 / M5 / M6 判定。

**Verification Actions (验证动作)**
- 动作 1：回读 `docs/agents/task-routing-matrix.md`，逐项核对 6 类任务、建议执行方式与案例。
- 动作 2：回读本轮任务合同 / 状态台账 / 验证链，确认任务接管骨架已落盘。
- 动作 3：查看 `git diff --name-only` 与 `git diff --stat`，确认改动范围只在文档与现场文件。
- 动作 4：必要时搜索关键分类词，确认没有遗漏用户要求的任务类型。

**Verification Result (验证结果)**
- 目标 1：通过 —— `docs/agents/task-routing-matrix.md` 的分类决策表与默认落地口径已覆盖“纯文档精修、法典升级、主线收编、技术债治理、高风险代码战、小范围即改即验任务”6 类任务。
- 目标 2：通过 —— 决策表逐类写明了建议执行方式，并给出“是否需要先隔离 worktree”的明确口径或条件口径。
- 目标 3：通过 —— 文档包含 CLI 最适案例 A / B，以及当前窗口最适案例 C / D，满足至少 1 套双向案例要求。
- 目标 4：通过 —— `git status --short` 仅显示 `docs/agents/` 与 `docs/exec-plans/` 范围内的文档新增；未见代码、测试或执行逻辑文件变更。

**Release / Handoff Gate (放行 / 接管闸门)**
- 当前判断：可收口
- 当前缺口：无。
- 接手后第一步：若需复核，先回读决策表，再用 `git status --short` 复核候选边界仍只在文档目录。
- 接手入口：先看 `docs/exec-plans/in-progress/p2-task-routing-matrix-task-contract.md`、`docs/exec-plans/in-progress/p2-task-routing-matrix-status-ledger.md` 与 `docs/agents/task-routing-matrix.md`。  
