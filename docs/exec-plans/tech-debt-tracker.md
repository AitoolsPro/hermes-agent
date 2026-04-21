# Tech Debt Tracker

## Active Campaigns

### PAC-CORE-001 — Policy-as-Code：帝国法典核心
- 状态：北冥已签字，已完成 M6 停机闸门，当前进入提交/合并准备阶段
- 优先级：P0
- 目标：把 `hermes_cli/safe_refactor_audit.py` 重构为“声明式规则 + 编程式审计”的双引擎，并以 `policies/core_rules.yaml` 作为仓库内 canonical 规则源。
- 当前阶段：M4 已落地最小实现，M5-v2 已验证伪造 TTY 降级 Diff 仍被拦截，独立复审已通过，待形成正式提交/分支留痕。
- 红线：不得降低 TTY / confirm / 文件范围 / shell / PATH 既有审计硬度；签字已完成，但仍不得绕过 Git/复核流程草率合并。
- 关键路径：`docs/exec-plans/in-progress/architecture-safe-refactor-loop-task-contract.md`、`docs/exec-plans/in-progress/architecture-safe-refactor-loop-status-ledger.md`、`docs/exec-plans/in-progress/architecture-safe-refactor-loop-verification-chain.md`、`docs/exec-plans/in-progress/architecture-safe-refactor-loop-m5-v2-review.md`、`docs/exec-plans/in-progress/architecture-safe-refactor-loop-m6-approval-request.md`
- 接管指令：在 `/tmp/policy-as-code-core-empire` 保持隔离战场，先形成正式提交/分支留痕，再进入后续 PR/合并准备。
