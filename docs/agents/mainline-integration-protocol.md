# Mainline Integration Protocol

## 适用范围

当任务进入 safe-refactor-loop 的“主线收编模式”时，必须遵守本协议。
本协议当前用于 AR-1「工程化接线收口」主线收编与收编前纠偏准备，严格区分：
- 任务级结案
- 候选提交形成
- 真正进入 `origin/main`

本轮若未得到统帅明确放行，只允许形成本地候选提交，不得 `push`，不得视为已收编。

## 强制前置检查

1. 必须先确认战役身份一致；本轮对象只能是 AR-1，不得继续沿用 PAC-CORE-001 专用协议审 AR-1。
2. 必须先确认候选工作树基线为干净 `origin/main`，不得把前置分支或无关历史夹带进来。
3. 必须先恢复并核对 AR-1 现场文档：Task Contract、Status Ledger、Verification Chain、Acceptance Report、`tech-debt-tracker.md`。
4. 必须先把协议纠偏为 AR-1 版本，再整理候选提交；协议未纠偏前，不得开始正式主线验收。
5. 必须依次完成：文件范围审查、代码与文档一致性审查、测试复验、Git 收编边界审查。
6. 本轮准备任务必须形成“单一可审计候选提交”；未形成提交前，不得宣称候选已就位。

## 验收通过条件

只有同时满足以下条件，才允许把 AR-1 视为“主线候选已形成”：

- `docs/agents/mainline-integration-protocol.md` 已纠偏为 AR-1 主线收编协议。
- `git status --short` 中除 AR-1 合法候选文件外，不存在其他待纳入改动。
- 候选提交为单一、本地、可审计 commit，且 commit 内容只覆盖 AR-1 合法收编文件。
- 代码实现、战时文档、账本、结案报告口径一致。
- 约定最小测试复验通过，且结果与文档一致。
- 未执行 `git push`，未直接收编到 `origin/main`。

任一条件不满足，直接打回，不得以“代码已经差不多完成”替代边界验收。

## AR-1 合法收编范围

本轮 AR-1「工程化接线收口」允许纳入候选提交的文件仅限：

- `docs/agents/mainline-integration-protocol.md`
- `docs/exec-plans/in-progress/ar-1-engineering-wiring-task-contract.md`
- `docs/exec-plans/in-progress/architecture-safe-refactor-loop-status-ledger.md`
- `docs/exec-plans/in-progress/architecture-safe-refactor-loop-verification-chain.md`
- `docs/exec-plans/completed/ar-1-engineering-wiring-acceptance-report.md`
- `docs/exec-plans/tech-debt-tracker.md`
- `hermes_cli/gate_controller.py`
- `hermes_cli/human_gate_controller.py`
- `hermes_cli/review_orchestrator.py`
- `hermes_cli/safe_refactor_runtime.py`
- `tests/hermes_cli/test_human_gate_controller.py`
- `tests/hermes_cli/test_review_orchestrator.py`
- `tests/hermes_cli/test_safe_refactor_runtime.py`

除上述文件外：
- 不得混入 PAC-CORE-001 专用文件
- 不得混入无关 CLI/Provider/Website 改动
- 不得为凑提交而顺手补其他技术债

## Git 动作纪律

本轮是“纠偏准备任务”，Git 动作只允许到候选提交为止：

1. `git add` 仅添加 AR-1 合法收编文件。
2. `git commit` 必须形成单一可审计候选提交，并明确标注这是 `AR-1 主线收编候选`。
3. 禁止 `git push origin main`。
4. 禁止在未获统帅后续放行前执行任何直接收编动作。

若验收不通过：
- 不得执行 `git push`
- 不得伪造“候选已形成”
- 不得把工作树脏改动冒充为可审计候选提交

## 统帅汇报模板

1. 任务结论
2. 新协议是否已就位
3. AR-1 候选提交是否已形成
4. 纳入候选文件
5. 排除文件
6. 测试与 Git 证据
7. 下一步约束
