**Task Contract Snapshot (合同快照)**
- 目标：在干净 `origin/main` 基线上，把 AR-1 第一刀、第二刀、第三刀的已完成成果收束成单一、可审计、合法的联合候选提交，为最终主线收编验收做准备。
- 范围边界：只处理三刀直接相关文件；第一刀与第二刀零差异部分只做审查；第三刀只补回归档同步 / tracker closure 合法差异；不 push，不 merge，不改 M3，不改 M5 / M6 判定逻辑。
- 完成标准：候选边界明确；四项测试复验通过；仅形成单一候选 commit；当前仍保持未 push、未 merge。

**Current State (当前状态)**
- 当前停点：独立 worktree 中单一候选 commit 已形成，当前停在联合收编准备完成态。
- 已完成：已恢复指定现场文档；已确认第一刀与第二刀主体内容已在 `origin/main`；已在 `hermes_cli/safe_refactor_runtime.py` 恢复第三刀归档同步与 tracker closure 合法差异；已补 `tests/hermes_cli/test_safe_refactor_runtime.py` 对应回归用例；四个指定测试文件已复验通过；已形成候选 commit。
- 未完成 / 当前阻塞：本轮按红线停在 commit，不进入 push、merge 或最终 M6 放行。
- 当前判断：可收口

**Evidence Logged (证据登记)**
- 已有证据：`pytest -o addopts='' tests/hermes_cli/test_safe_refactor_runtime.py tests/hermes_cli/test_review_orchestrator.py tests/hermes_cli/test_human_gate_controller.py tests/hermes_cli/test_safe_refactor_audit.py -q` 结果为 `28 passed in 0.07s`；`git diff --name-status origin/main..HEAD` 与 `git show --stat --summary HEAD` 均指向同一组 6 个候选文件；`hermes_cli/safe_refactor_audit.py` 与对应测试未改动。
- 证据对应结论：第一刀与第二刀已作为主线既有事实被复验；第三刀已在不改 M5 / M6 判定逻辑的前提下补回合法差异；当前已形成单一可审计联合候选提交。
- 证据缺口：缺少最终主线收编级验收与北冥后续裁决；本轮故意不进入 push / merge。

**Next Handoff (下一步 / 接管指令)**
- 接手后第一步：把本次候选 commit 作为唯一输入，执行最终主线收编级验收，不得重新扩边界。
- 立即核查：复核 `git show --stat --summary HEAD`、`git diff --name-status origin/main..HEAD`、四项测试结果与文档口径是否仍一致。
- 若受阻先排查：先查是否有人在候选 worktree 上继续引入 blueprint、acceptance report、review_orchestrator、human_gate_controller 等 audit-only 文件改动，或误触 push / merge 动作。
