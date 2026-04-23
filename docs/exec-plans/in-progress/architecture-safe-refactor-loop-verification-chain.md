## Verification Chain（默认验证链）

**Verification Target (验证目标)**
- 对应合同项：对应 AR-1 第二刀的一键启动总控链交付物、证据与完成标准。
- 目标 1：证明入口函数能从 `docs/exec-plans/tech-debt-tracker.md` 选择当前可接管战役，而不是手工写死 battle name。
- 目标 2：证明系统能依据账本与任务合同自动恢复或建立 Task Contract / Status Ledger / Verification Chain，并在入口文档缺失时 fail-closed。
- 目标 3：证明总控链真实串起 M3 -> M5-v2 -> M6，且只有 `APPROVE_CANDIDATE` 才进入 M6。
- 目标 4：证明 `REJECT_HARD / FAKE_WIN / WARN` 会停在 M5-v2 自愈循环或失败态，不会误入 M6，且最多只重试 3 次。
- 目标 5：证明第三刀归档同步器没有被吸入本轮实现。

**Verification Actions (验证动作)**
- 动作 1：回读 `hermes_cli/safe_refactor_runtime.py`，确认入口函数先读 tracker，再解析任务合同路径，再从任务合同解析状态台账与验证链路径。
- 动作 2：运行 `tests/hermes_cli/test_safe_refactor_runtime.py`，验证账本接管、fail-closed、`APPROVE_CANDIDATE -> M6`、未达条件阻断 M6、3 次自愈上限等场景。
- 动作 3：运行 `tests/hermes_cli/test_human_gate_controller.py`，验证精简《北冥裁决请示书》与显式 `Y / Confirm` 输入闸门。
- 动作 4：运行 `tests/hermes_cli/test_review_orchestrator.py` 与 `tests/hermes_cli/test_safe_refactor_audit.py`，确认复用现有 M3 规则与 M5-v2 自愈循环，没有顺手改法典规则。
- 动作 5：回读 `docs/exec-plans/tech-debt-tracker.md` 与任务合同，确认当前 tracker 只提供自动接管入口，并明确第三刀继续后置。

**Verification Result (验证结果)**
- 目标 1：通过 —— `launch_safe_refactor_from_tracker()` 先读取 tracker，再通过显式 `自动接管入口` 解析任务合同路径，不再依赖 battle name 硬编码。
- 目标 2：通过 —— `discover_battle_document_paths()` 会从任务合同中解析状态台账与验证链路径；缺少显式任务合同路径或缺少战时文档路径时，相关测试证明会直接 fail-closed。
- 目标 3：通过 —— `run_safe_refactor_pipeline()` 只在最终裁决为 `APPROVE_CANDIDATE` 时调用 M6；对应测试验证了进入 M6 时会写回 `entered_m6=yes` 并输出精简《北冥裁决请示书》。
- 目标 4：通过 —— `REJECT_HARD / FAKE_WIN / WARN` 的测试均证明不会误入 M6；3 次自愈上限测试证明达到上限后停在 M5-v2。
- 目标 5：通过 —— 本轮代码未触发归档同步器；tracker、任务合同与状态台账均明确声明第三刀继续后置。

**Release / Handoff Gate (放行 / 接管闸门)**
- 当前判断：可收口
- 当前缺口：缺少北冥对第二刀交付的最终验收；第三刀归档同步器缺口为刻意保留，不属于本轮未完成项。
- 接手后第一步：先重跑定向 pytest，确认 `26 passed` 仍成立，再按验收重点回读 tracker / task contract / runtime 入口。
- 接手入口：先看 `docs/exec-plans/in-progress/ar-1-engineering-wiring-task-contract.md`、`docs/exec-plans/in-progress/architecture-safe-refactor-loop-status-ledger.md`、`docs/exec-plans/tech-debt-tracker.md`、`hermes_cli/safe_refactor_runtime.py`。
