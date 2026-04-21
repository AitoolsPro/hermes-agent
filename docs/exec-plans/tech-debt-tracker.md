# Tech Debt Tracker

## Active Campaigns

### PAC-CORE-001 — Policy-as-Code：帝国法典核心
- 状态：北冥已签字，M6 闸门与主线收编验收均已完成，PAC 合法收编已推送至 `origin/main`
- 优先级：P0
- 目标：把 `hermes_cli/safe_refactor_audit.py` 重构为“声明式规则 + 编程式审计”的双引擎，并以 `policies/core_rules.yaml` 作为仓库内 canonical 规则源。
- 当前阶段：已按主线收编纪律从干净 `main` 重建 `pac-core-001-mainline-candidate`；已补建主线协议并修正 M5 文档中的 `4 passed` / `9 passed` 不一致；四类主线验收通过后，已提交并推送 `264aab0d feat: PAC-CORE-001 mainline integration` 到 `origin/main`。
- 红线：不得降低 TTY / confirm / 文件范围 / shell / PATH 既有审计硬度；不得混入 `cli.py`、`hermes_cli/model_switch.py` 等前置无关改动；未完成四类主线验收前不得执行收编 Git 动作。
- 关键路径：`docs/agents/mainline-integration-protocol.md`、`docs/exec-plans/in-progress/pac-core-001-mainline-task-contract.md`、`docs/exec-plans/in-progress/pac-core-001-mainline-status-ledger.md`、`docs/exec-plans/in-progress/pac-core-001-mainline-verification-chain.md`、`docs/exec-plans/in-progress/architecture-safe-refactor-loop-m5-v2-review.md`、`docs/exec-plans/in-progress/architecture-safe-refactor-loop-m6-approval-request.md`
- 接管指令：PAC-CORE-001 主线收编已闭环；后续若继续扩展法典范围，必须基于当前 `origin/main` 重新立项，不得回退到旧污染分支。
