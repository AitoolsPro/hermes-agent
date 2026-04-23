**Task Contract Snapshot (合同快照)**
- 目标：完成 AR-1 第二刀：建立“从账本接管战役并自动串起 M3 -> M5 -> M6”的一键启动总控链，且不把第三刀归档同步器一起吸入。
- 范围边界：只处理账本接管、战时文档恢复或建立、M3 -> M5-v2 -> M6 接线与精简《北冥裁决请示书》；不吸入归档同步器，不改 M3 规则，不削弱 M6。
- 完成标准：入口能从账本选择可接管战役并恢复战时文档；只有 `APPROVE_CANDIDATE` 才进入 M6；未达条件时停在 M5-v2 自愈循环或失败态。

**Current State (当前状态)**
- 当前停点：第二刀代码改动与最小必要测试已完成，等待北冥验收。
- 已完成：已恢复 `ar-1-engineering-wiring-blueprint.md`；已把 `tech-debt-tracker.md` 改成显式提供自动接管入口；已实现从账本接管战役、依据任务合同恢复战时文档、只在 `APPROVE_CANDIDATE` 时进入 M6 的总控链；已补最小必要测试并通过。
- 未完成 / 当前阻塞：第三刀归档同步器仍刻意后置，尚未接入；本轮未执行真实合并或归档动作。
- 当前判断：可收口

**Evidence Logged (证据登记)**
- 已有证据：`tests/hermes_cli/test_safe_refactor_runtime.py` 新增并通过账本接管、fail-closed、M6 准入阻断等用例；`tests/hermes_cli/test_human_gate_controller.py` 验证精简《北冥裁决请示书》与显式 `Y / Confirm`；相关定向 pytest 共 `26 passed`。
- 证据对应结论：第二刀已实现“从账本接管战役并自动串起 M3 -> M5 -> M6”的一键启动总控链，且未把第三刀一起吸入。
- 证据缺口：缺少北冥对本轮第二刀代码与文档的最终验收；第三刀归档同步器证据故意留空，不属于本轮。

**Next Handoff (下一步 / 接管指令)**
- 接手后第一步：先回看 `docs/exec-plans/tech-debt-tracker.md`、本任务合同与 `hermes_cli/safe_refactor_runtime.py`，确认自动接管入口与路径契约一致。
- 立即核查：运行定向 pytest，重点确认 `REJECT_HARD / FAKE_WIN / WARN` 仍不会误入 M6，且 tracker 缺少显式任务合同路径时保持 fail-closed。
- 若受阻先排查：先查账本中的 `自动接管入口` 是否存在、任务合同中是否显式写出状态台账/验证链路径，以及 `run_safe_refactor_pipeline()` 是否仍未触发归档逻辑。
