# Tech Debt Tracker

## Active Campaigns

### PAC-CORE-001 — Policy-as-Code：帝国法典核心
- 状态：北冥已签字，已完成 M6 停机闸门，当前进入提交/合并准备阶段
- 优先级：P0
- 目标：把 `hermes_cli/safe_refactor_audit.py` 重构为“声明式规则 + 编程式审计”的双引擎，并以 `policies/core_rules.yaml` 作为仓库内 canonical 规则源。
- 当前阶段：已按主线收编纪律从干净 `main` 重建 `pac-core-001-mainline-candidate`；已补建主线协议并修正 M5 文档中的 `4 passed` / `9 passed` 不一致；四类主线验收已通过，当前允许执行仅含 PAC 合法文件的 Git 收编动作。
- 红线：不得降低 TTY / confirm / 文件范围 / shell / PATH 既有审计硬度；不得混入 `cli.py`、`hermes_cli/model_switch.py` 等前置无关改动；未完成四类主线验收前不得执行收编 Git 动作。
- 关键路径：`docs/agents/mainline-integration-protocol.md`、`docs/exec-plans/in-progress/pac-core-001-mainline-task-contract.md`、`docs/exec-plans/in-progress/pac-core-001-mainline-status-ledger.md`、`docs/exec-plans/in-progress/pac-core-001-mainline-verification-chain.md`、`docs/exec-plans/in-progress/architecture-safe-refactor-loop-m5-v2-review.md`、`docs/exec-plans/in-progress/architecture-safe-refactor-loop-m6-approval-request.md`
- 接管指令：在 `/tmp/policy-as-code-core-empire` 的 `pac-core-001-mainline-candidate` 上继续四类验收；若任一项不通过，直接打回；只有全部通过时才允许仅对 PAC 合法文件执行 `git add`、`git commit`、`git push origin main`。
