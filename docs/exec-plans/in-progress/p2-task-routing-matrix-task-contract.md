## Task Contract（任务合同）

**Objective (目标)**  
建立一份可直接用于未来派工的任务决策表，明确哪些任务应走 safe-refactor-loop / CLI 自动化引擎，哪些任务更适合由有鱼在当前聊天窗口直接处理。

**Scope / Watchouts (范围 / 警戒线)**  
IN: 只在隔离 worktree 中恢复用户点名的法典上下文文件，新增 `docs/agents/task-routing-matrix.md`，并为本轮任务补齐最小合同 / 状态台账 / 验证链。  
OUT: 不改任何业务代码、运行时代码、测试代码；不改执行逻辑；不改 M3 / M5 / M6 判定；不 push；不 merge。  
WATCHOUTS: 最大风险是把“派工决策表”写成执行流程全文，或误把轻任务都推给 CLI；第二风险是忽视主仓脏工作树导致候选 diff 被污染；第三风险是偷改法典规则口径。

**Inputs (输入)**  
`AGENTS.md`、`docs/agents/beiming-constitution.md`、`docs/agents/mainline-integration-protocol.md`、`docs/agents/law-casebook.md`、`~/.hermes/skills/safe-refactor-loop/SKILL.md`、`docs/exec-plans/tech-debt-tracker.md`；用户要求先切隔离 worktree `/tmp/p2-task-routing-matrix`，分支 `p2-task-routing-matrix`；用户红线为不改业务代码、不改执行逻辑、不改 M3 / M5 / M6 判定、不 push、不 merge。

**Deliverables / Evidence (交付物 / 证据)**  
交付物：`docs/agents/task-routing-matrix.md` 与本轮任务合同 / 状态台账 / 验证链。  
证据：回读决策表可见 6 类任务分层、每类的建议执行方式、worktree 建议、至少 1 套 CLI 最适案例与至少 1 套当前窗口最适案例；`git diff --name-only` 证明仅改文档与任务现场文件。

**Done (完成标准)**  
1. 决策表已覆盖用户指定的 6 类任务；  
2. 每类任务都明确给出“CLI 自动化引擎 / 当前聊天窗口 / 是否先隔离 worktree”的建议；  
3. 至少包含 1 套最适合 CLI 自动化的案例与 1 套更适合当前窗口直接做的案例；  
4. 所有改动均停留在文档与任务现场文件；  
5. 最终汇报可直接为北冥降低未来派工成本。  
