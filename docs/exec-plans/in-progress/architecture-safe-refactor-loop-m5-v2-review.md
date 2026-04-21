# M5-v2 Review — PAC-CORE-001

- 审核对象：`policies/core_rules.yaml`、`hermes_cli/safe_refactor_audit.py`、`tests/hermes_cli/test_safe_refactor_audit.py`
- 审核战场：`/tmp/policy-as-code-core-empire`
- 审核解释器：`/opt/homebrew/bin/python3.11`
- 当前裁决：`APPROVE_CANDIDATE`

## 固定顺序复审结果

1. M3 审计
   - 实际候选 diff：通过
   - 伪造 TTY 降级 diff：`REJECT_HARD`
   - 命中规则：
     - `uninstall.tty_guard_removed`
     - `programmatic.uninstall_tty_guard_removed`
     - `programmatic.uninstall_tty_guard_bypass`

2. 调用链/规则接线
   - `policies/core_rules.yaml` 已作为 canonical 规则源落盘。
   - `hermes_cli/safe_refactor_audit.py` 已实现动态加载 canonical YAML 与本地 override 只增不减策略。
   - 本地 override 禁止写入 `hard_reject_rules` 等放松红线的键；违规则抛 `PolicyError`。

3. pytest
   - 命令：`/opt/homebrew/bin/python3.11 -m pytest -o addopts='' tests/hermes_cli/test_safe_refactor_audit.py`
   - 结果：`9 passed`

4. 自愈循环
   - Attempt 1：投喂伪造 TTY 降级 diff，裁决 `REJECT_HARD`。
   - Self-heal 指令：保留 `cmd_uninstall` 中的直接 `_require_tty("uninstall")`，不得以环境变量或布尔 fallback 放宽。
   - Attempt 2：仅保留对 `hermes_cli/safe_refactor_audit.py` 的安全增量 diff，裁决通过。

## 放行判断

- 结果：`APPROVE_CANDIDATE`
- 依据：
  - 实际候选 diff 未触发任何 `REJECT_HARD`
  - 伪造 TTY 降级 diff 被双引擎稳定拦截
  - 最小测试通过
  - 未发现为了规则中心化而降低既有审计硬度

## 仍存边界

- 当前规则覆盖聚焦 uninstall 高危路径，尚未扩展为全仓通用法典。
- 尚未接入更高层 `review_orchestrator.py` / `human_gate_controller.py` 工程化接线。
- 因当前已达到 `APPROVE_CANDIDATE`，必须进入 M6 人工审批闸门，未获北冥统帅签字前不得合并。
