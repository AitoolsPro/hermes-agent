## Verification Chain（默认验证链）

**Verification Target (验证目标)**
- 对应合同项：对应三刀联合收编准备的候选边界、第三刀归档同步合法差异、四项测试复验与单一 commit 收口标准。
- 目标 1：证明第一刀与第二刀相对 `origin/main` 已是主线既有事实，本轮不会重复把零差异文件塞入 commit。
- 目标 2：证明第三刀只在 `approved=True` 时归档，并且只补回 `hermes_cli/safe_refactor_runtime.py` 与 `tests/hermes_cli/test_safe_refactor_runtime.py` 的合法差异。
- 目标 3：证明关键测试在干净 `origin/main` worktree 中仅带本轮候选文件即可通过。
- 目标 4：证明最终 Git 候选边界是单一、可审计、未 push、未 merge 的联合候选提交。

**Verification Actions (验证动作)**
- 动作 1：对比 `origin/main`、历史三刀现场与当前 worktree，逐项确认纳入 / 排除边界，特别核查 `review_orchestrator.py`、`human_gate_controller.py`、`gate_controller.py`、`safe_refactor_audit.py` 是否为 audit-only。
- 动作 2：回读 `hermes_cli/safe_refactor_runtime.py` 与 `tests/hermes_cli/test_safe_refactor_runtime.py`，确认补回的第三刀逻辑只涉及 `archive_report_path` 解析、`approved=True` 时归档、tracker closure 与对应测试。
- 动作 3：运行 `pytest -o addopts='' tests/hermes_cli/test_safe_refactor_runtime.py tests/hermes_cli/test_review_orchestrator.py tests/hermes_cli/test_human_gate_controller.py tests/hermes_cli/test_safe_refactor_audit.py -q`。
- 动作 4：在形成 commit 后核对 `git status --short`、`git diff --name-status origin/main..HEAD` 与 `git show --stat --summary HEAD`。

**Verification Result (验证结果)**
- 目标 1：通过 —— 对比 `origin/main`=`d6cd3e13` 与历史三刀现场后，确认第一刀与第二刀主体已在主线；`review_orchestrator.py`、`human_gate_controller.py`、`gate_controller.py`、`test_review_orchestrator.py`、`test_human_gate_controller.py` 本轮仅做审查与复验，不进入 delta commit。
- 目标 2：通过 —— 当前 runtime 仅补回 `archive_report_path` 契约、`approved=True` 时写结案报告 / 更新 tracker 的第三刀合法差异；`approved=False` 不归档、不平账；M5 / M6 判定逻辑未改。
- 目标 3：通过 —— `pytest -o addopts='' tests/hermes_cli/test_safe_refactor_runtime.py tests/hermes_cli/test_review_orchestrator.py tests/hermes_cli/test_human_gate_controller.py tests/hermes_cli/test_safe_refactor_audit.py -q` 实测 `28 passed in 0.07s`。
- 目标 4：通过 —— 当前候选 commit已形成；`git diff --name-status origin/main..HEAD` 与 `git show --stat --summary HEAD` 同时指向相同 6 个候选文件，且 worktree 保持干净。

**Release / Handoff Gate (放行 / 接管闸门)**
- 当前判断：可收口
- 当前缺口：缺少最终主线收编级验收与北冥对后续 push / merge 的裁决。
- 接手后第一步：以当前候选 commit 为唯一输入执行最终主线收编级验收，不得重新扩边界。
- 接手入口：先看 `docs/exec-plans/in-progress/ar-1-engineering-wiring-task-contract.md`、当前 status ledger、`git show --stat --summary HEAD`、`hermes_cli/safe_refactor_runtime.py`、`tests/hermes_cli/test_safe_refactor_runtime.py`。
