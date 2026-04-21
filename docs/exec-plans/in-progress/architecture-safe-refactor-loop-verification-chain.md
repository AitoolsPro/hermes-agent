## Verification Chain（默认验证链）

**Verification Target (验证目标)**
- 对应合同项：对应 AR-1 的 runtime 模块、战时文档回写、归档同步、一键启动与人审防旁路完成标准。
- 目标 1：证明 M5 runtime 能在任务合同存在时恢复或创建 Status Ledger / Verification Chain，并在运行后自动回写当前裁决。
- 目标 2：证明当复审结论达到 `APPROVE_CANDIDATE` 时，系统会进入 M6 并要求显式 `Y / Confirm`。
- 目标 3：证明只有在真实批准或显式测试白名单批准后，归档同步器才会生成结案报告并更新账本。
- 目标 4：证明一键启动入口会从账本正确选中当前活跃战役，而不是跨段误抓其他战役。

**Verification Actions (验证动作)**
- 动作 1：运行 `/opt/homebrew/bin/python3.11 -m pytest -o addopts='' tests/hermes_cli/test_safe_refactor_audit.py tests/hermes_cli/test_human_gate_controller.py tests/hermes_cli/test_review_orchestrator.py tests/hermes_cli/test_safe_refactor_runtime.py -q`。
- 动作 2：回读 `hermes_cli/review_orchestrator.py`、`hermes_cli/human_gate_controller.py`、`hermes_cli/safe_refactor_runtime.py`，确认 M5→M6 接线与文档回写逻辑已落盘。
- 动作 3：检查 runtime 测试中批准、拒绝、缺合同、跨段选战役与非 AR 战役平账路径。
- 动作 4：回读 AR-1 任务合同、状态台账、验证链、结案报告与账本，确认口径一致且可接管。

**Verification Result (验证结果)**
- 目标 1：通过 —— `tests/hermes_cli/test_safe_refactor_runtime.py` 已证明 Task Contract 缺失时直接失败，Status Ledger / Verification Chain 缺失时可按模板自动恢复，并在流水线运行后自动回写裁决。
- 目标 2：通过 —— `tests/hermes_cli/test_human_gate_controller.py` 与 `tests/hermes_cli/test_safe_refactor_runtime.py` 已证明只有 `Y / Confirm` 视为批准，且 `APPROVE_CANDIDATE` 会触发 M6 停机提示。
- 目标 3：通过 —— runtime 测试已证明未显式允许时不能注入假 gate，human reject 不归档不平账，human approve 才生成结案报告并更新 tracker。
- 目标 4：通过 —— `test_launch_safe_refactor_from_tracker_selects_active_battle_and_runs_pipeline` 与 `test_select_active_battle_does_not_cross_match_other_sections` 已证明按 section 分段选战役，且非 `AR-1` 战役也能定点更新 tracker。

**Release / Handoff Gate (放行 / 接管闸门)**
- 当前判断：可收口
- 当前缺口：本轮仅完成任务级工程化接线收口，尚未进入主线收编验收与 Git 动作。
- 接手后第一步：若要正式入主线，先按主线收编法则复跑关键测试并做逐文件边界审查。
- 接手入口：先看 AR-1 任务合同、当前状态台账、结案报告与 `tech-debt-tracker.md`。
