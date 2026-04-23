## Task Contract（任务合同）

**Objective (目标)**  
完成 AR-1 第二刀：建立“从账本接管战役并自动串起 M3 -> M5 -> M6”的一键启动总控链，且不把第三刀归档同步器一起吸入。

**Scope / Watchouts (范围 / 警戒线)**  
IN: 只处理账本选战役、Task Contract / Status Ledger / Verification Chain 自动恢复或建立、M3 -> M5-v2 -> M6 的总控接线、精简《北冥裁决请示书》输出、最小必要测试与现场文档回写。  
OUT: 不实现归档同步器；不修改 M3 审计规则；不削弱 M6 物理停机；不绕过 `APPROVE_CANDIDATE -> M6` 的唯一入口；不修改业务无关代码；不把“选择战役”做成 battle name 硬编码。  
WATCHOUTS: 最大风险是把第二刀与第三刀重新耦死；第二风险是让账本接管依赖脆弱字符串猜测而非显式文档契约；第三风险是把历史 acceptance report 误当成本轮完成证明；第四风险是未达 `APPROVE_CANDIDATE` 却误入 M6。

**Inputs (输入)**  
- `docs/exec-plans/tech-debt-tracker.md`  
- `docs/exec-plans/in-progress/architecture-safe-refactor-loop-status-ledger.md`  
- `docs/exec-plans/in-progress/architecture-safe-refactor-loop-verification-chain.md`  
- `docs/exec-plans/in-progress/ar-1-engineering-wiring-blueprint.md`  
- `docs/exec-plans/completed/ar-1-engineering-wiring-acceptance-report.md`（仅作历史输入，不作本轮完成证明）  
- 仓库外：`~/.hermes/skills/safe-refactor-loop/SKILL.md`  
- `hermes_cli/safe_refactor_audit.py`（M3）  
- `hermes_cli/review_orchestrator.py`（M5 / M5-v2）  
- `hermes_cli/human_gate_controller.py` 与 `hermes_cli/gate_controller.py`（M6）  
- `hermes_cli/safe_refactor_runtime.py`

**Deliverables / Evidence (交付物 / 证据)**  
交付物：从账本接管战役的一键入口；自动恢复或建立战时文档的路径契约；只在 `APPROVE_CANDIDATE` 时进入 M6 的总控链；精简《北冥裁决请示书》；最小必要测试；更新后的 tracker / Task Contract / Status Ledger / Verification Chain。  
证据：入口函数可直接读取 `docs/exec-plans/tech-debt-tracker.md` 选择当前可接管战役；能依据账本与任务合同恢复或建立战时文档；M5-v2 最多 3 次自愈；`REJECT_HARD / FAKE_WIN / WARN` 不误入 M6；`APPROVE_CANDIDATE` 时输出精简《北冥裁决请示书》并物理停机；测试通过且未触碰归档同步器。

**Done (完成标准)**  
以下条件必须同时成立：  
1. 一键入口能从账本选择当前活跃或等待自动化接管的战役，而不是手工写死 battle name  
2. 系统能自动恢复或建立对应的 Task Contract / Status Ledger / Verification Chain；若缺少合法入口文档则 fail-closed  
3. 总控链能真实串起 M3 -> M5-v2 -> M6，且只在 `APPROVE_CANDIDATE` 时进入 M6  
4. `REJECT_HARD / FAKE_WIN / WARN` 时必须停在 M5-v2 自愈循环或失败态，不得误入 M6  
5. M5-v2 自愈重试上限保留为最多 3 次  
6. 不触碰归档同步器，不修改 M3 规则，不削弱 M6 物理停机  
7. 最小相关测试通过，并覆盖：账本接管、战时文档恢复、`APPROVE_CANDIDATE -> M6`、未达条件阻断 M6、fail-closed 场景
