# Mainline Integration Protocol

## 适用范围

当任务进入 safe-refactor-loop 的“主线收编模式”时，必须遵守本协议。
本协议用于把“任务已完成”与“允许进入 main”严格区分。

## 强制前置检查

1. 必须先确认战役身份一致，不得把别的战役现场冒充为当前收编对象。
2. 必须先在干净 `main` 基线上重建候选，不得直接沿用叠在前置分支上的旧候选。
3. 必须排除前置无关提交，尤其不得混入与本战役无关的 `cli.py`、`hermes_cli/model_switch.py` 等改动。
4. 必须先修正文档与证据中的已知不一致项，再进行正式验收。
5. 必须依次完成：文件范围审查、代码与文档一致性审查、测试复验、Git 收编边界审查。

## 验收通过条件

只有同时满足以下条件，才允许进入 Git 收编动作：

- 候选分支以干净 `main` 为祖先重建。
- `git diff --name-status main..HEAD` 只包含 PAC 合法收编文件。
- 代码实现与文档描述一致，不存在已知矛盾。
- 约定测试复验通过，且结果与文档一致。
- 不存在会把前置无关提交带入 `main` 的边界污染。

任一条件不满足，直接打回，不得强推。

## 合法收编范围

本轮 PAC-CORE-001 主线收编允许的文件范围：

- `policies/core_rules.yaml`
- `hermes_cli/safe_refactor_audit.py`
- `tests/hermes_cli/test_safe_refactor_audit.py`
- `docs/exec-plans/tech-debt-tracker.md`
- `docs/exec-plans/in-progress/architecture-safe-refactor-loop-m5-v2-review.md`
- `docs/exec-plans/in-progress/architecture-safe-refactor-loop-m6-approval-request.md`
- `docs/exec-plans/in-progress/architecture-safe-refactor-loop-status-ledger.md`
- `docs/exec-plans/in-progress/architecture-safe-refactor-loop-task-contract.md`
- `docs/exec-plans/in-progress/architecture-safe-refactor-loop-verification-chain.md`
- `docs/agents/mainline-integration-protocol.md`
- `docs/exec-plans/in-progress/pac-core-001-mainline-task-contract.md`
- `docs/exec-plans/in-progress/pac-core-001-mainline-status-ledger.md`
- `docs/exec-plans/in-progress/pac-core-001-mainline-verification-chain.md`

## Git 动作纪律

若且仅若验收通过，才允许执行：

1. `git add` 仅添加 PAC 合法收编文件。
2. `git commit` 明确标注这是 `PAC-CORE-001 主线收编`。
3. `git push origin main` 只能在本地候选已证明可直接进入 `main` 时执行。

若验收不通过：

- 不得执行 `git push origin main`
- 不得用“测试基本通过”替代边界审查
- 不得把无关提交一并塞进本轮收编

## 统帅汇报模板

1. 任务结论
2. 法典状态
3. 关键证据
4. 关键文件清单
5. Git 状态
6. 下一步唯一建议
