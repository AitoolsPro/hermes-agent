**Task Contract Snapshot (合同快照)**
- 目标：建立“任务走 CLI 自动化引擎还是当前聊天窗口”的可执行决策表。
- 范围边界：只恢复用户点名的法典上下文文件，新增 `docs/agents/task-routing-matrix.md` 与本轮现场文档；不改代码、测试、执行逻辑、M3 / M5 / M6 判定，不 push、不 merge。
- 完成标准：6 类任务已分层并写明建议执行方式、worktree 建议与代表案例，且改动边界只在文档。

**Current State (当前状态)**
- 当前停点：已在隔离 worktree 完成上下文恢复、决策表落盘与最终回读，当前可直接汇报收口。
- 已完成：已加载 `safe-refactor-loop` 与三根骨架技能；已建立 `/tmp/p2-task-routing-matrix` worktree 与分支 `p2-task-routing-matrix`；已恢复用户点名的法典上下文文件；已完成 `docs/agents/task-routing-matrix.md` 与本轮合同 / 台账 / 验证链；已执行最终分类回读与 git 边界检查。
- 未完成 / 当前阻塞：无当前阻塞；未执行任何 push / merge / 代码改动。
- 当前判断：可收口

**Evidence Logged (证据登记)**
- 已有证据：worktree 创建结果、用户点名文件回读结果、`docs/agents/task-routing-matrix.md` 回读结果、关键分类词搜索结果、`git status --short` 与文件清单输出。
- 证据对应结论：6 类任务已全部落表，CLI / 当前窗口 / worktree 建议齐备，且改动边界停留在文档与现场文件。
- 证据缺口：无当前缺口。

**Next Handoff (下一步 / 接管指令)**
- 接手后第一步：若需复核，先回读 `docs/agents/task-routing-matrix.md` 与本轮验证链，再核对最终汇报中的分类摘要。
- 立即核查：继续保持边界，不新增代码、测试、执行逻辑、push 或 merge。
- 若受阻先排查：若后续要把该表纳入主线，再先确认主仓最新上下文与目标收编范围，不要直接扩大本轮候选。  
