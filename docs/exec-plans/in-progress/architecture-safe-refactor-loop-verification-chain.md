## Verification Chain（默认验证链）

**Verification Target (验证目标)**
- 对应合同项：对应 `policies/core_rules.yaml`、动态审计引擎、相关测试、M4/M5/M6 证据与“拦截伪造 TTY 降级 Diff 且不降硬度”的完成标准。
- 目标 1：证明仓库中已建立可读的 canonical YAML 规则文件，并由 Python 审计引擎动态加载。
- 目标 2：证明本地 override 机制即使存在，也不会降低 TTY / confirm / 文件范围 / shell / PATH 红线硬度。
- 目标 3：证明针对伪造的 TTY 降级 Diff，新架构仍给出拒绝结论，而不是误判通过。
- 目标 4：证明 M4 玄麟执行留痕、M5-v2 审计结果与 M6 人工闸门材料已落盘并可接管。

**Verification Actions (验证动作)**
- 动作 1：回读 `policies/core_rules.yaml`、`hermes_cli/safe_refactor_audit.py` 与 `tests/hermes_cli/test_safe_refactor_audit.py`，确认 canonical + override 解析路径、红线策略与回归用例。
- 动作 2：运行 `/opt/homebrew/bin/python3.11 -m pytest -o addopts='' tests/hermes_cli/test_safe_refactor_audit.py`，验证规则加载、override 行为与伪造 TTY 降级 Diff 审计场景。
- 动作 3：执行 M5-v2 自愈循环：先审计伪造 TTY 降级 diff，再根据 findings 收敛为安全 diff 并复审，确认最终可达 `APPROVE_CANDIDATE`。
- 动作 4：回读玄麟 `latest.json`、M5-v2 文档、M6 请示书、状态台账与技术债账本，确认交接入口一致。

**Verification Result (验证结果)**
- 目标 1：通过 —— 已回读 `policies/core_rules.yaml` 与 `hermes_cli/safe_refactor_audit.py`，确认 canonical YAML 被 `load_policy_bundle()` 动态加载，且核心策略与 override 合并后都会执行 scope consistency 校验。
- 目标 2：通过 —— `ALLOWED_OVERRIDE_KEYS` 仅允许 `restricted_globs`、`allowed_direct_related_paths`、`risk_notes`；测试已证明试图覆盖 `hard_reject_rules`、把 restricted path 放进 allowlist、或通过多 override 顺序重引入冲突路径，都会抛 `PolicyError`。
- 目标 3：通过 —— pytest 用例与 M5-v2 文档均证明伪造 TTY 降级 diff 会触发 `uninstall.tty_guard_removed`、`programmatic.uninstall_tty_guard_removed`、`programmatic.uninstall_tty_guard_bypass` 三条 `REJECT_HARD`，而 empty/malformed diff 也会因 `policy.diff_parse_invalid` fail-closed。
- 目标 4：通过 —— `~/.hermes/runtime/agents/xuanlin/latest.json`、M5-v2 文档、M6 请示书、独立审查通过结论与状态台账均已落盘；北冥已发出 `Y` 签字。

**Release / Handoff Gate (放行 / 接管闸门)**
- 当前判断：可收口
- 当前缺口：缺正式提交/分支留痕；未进入更高层 orchestrator/controller 工程化接线。
- 接手后第一步：整理候选为正式提交并准备后续合并/PR 材料。
- 接手入口：先看任务合同、M5-v2 文档、独立审查结论、玄麟 `latest.json` 与当前 Git 状态。
