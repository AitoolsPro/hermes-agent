**Task Contract Snapshot (合同快照)**
- 目标：完成“Policy-as-Code：帝国法典核心”基建级重构，使 `hermes_cli/safe_refactor_audit.py` 成为由 `policies/core_rules.yaml` 驱动的通用动态审计引擎，并保持既有审计硬度不下降。
- 范围边界：允许新建 canonical YAML 规则、必要的本地 override 设计、审计引擎代码、最小测试、玄麟留痕与战时文档；不允许降低 TTY / confirm / 文件范围 / shell / PATH 红线，不允许未签字合并。
- 完成标准：新引擎可动态加载规则并拦截伪造 TTY 降级 Diff，M4/M5/M6 证据完整，台账与验证链可接管。

**Current State (当前状态)**
- 当前停点：北冥已发出 `Y` 签字，M6 已解除停机；当前已完成独立复审、自愈修补与签字后的放行准备，可进入提交/合并准备阶段。
- 已完成：已创建 `policies/core_rules.yaml`、`hermes_cli/safe_refactor_audit.py`、`tests/hermes_cli/test_safe_refactor_audit.py`；已确认 `/opt/homebrew/bin/python3.11 -m pytest -o addopts='' tests/hermes_cli/test_safe_refactor_audit.py` 为 `9 passed`；已生成玄麟留痕 `~/.hermes/runtime/agents/xuanlin/latest.json`；已完成独立审查闭环并修补 fail-closed 与 override scope consistency 缺口；已获北冥 `Y` 签字。
- 未完成 / 当前阻塞：尚未创建正式提交；尚未接入更高层 `review_orchestrator.py` / `human_gate_controller.py`；当前规则仍聚焦 uninstall 高危路径。
- 当前判断：可收口

**Evidence Logged (证据登记)**
- 已有证据：`policies/core_rules.yaml` 回读可见 canonical 红线；`hermes_cli/safe_refactor_audit.py` 回读可见 YAML 动态加载、scope consistency 校验与 diff fail-closed；`tests/hermes_cli/test_safe_refactor_audit.py` 回读可见伪造 TTY 降级拦截、核心策略冲突、多 override 顺序绕过与 malformed diff 拒绝测试；pytest `9 passed`；M5-v2 文档证明伪造 TTY 降级 diff 被 `REJECT_HARD` 且自愈后达到 `APPROVE_CANDIDATE`；独立代码审查第三轮已 `passed=true`；玄麟留痕 JSON 已生成；北冥已发出 `Y` 签字。
- 证据对应结论：本轮候选已完成签字后的放行准备，且通过独立代码审查补齐了 fail-closed 与 override scope consistency 缺口，未发现因规则中心化导致硬度下降。
- 证据缺口：缺正式提交/分支留痕；缺更高层 orchestrator/controller 工程化接线证据。

**Next Handoff (下一步 / 接管指令)**
- 接手后第一步：先看当前 Git 状态并将本轮候选整理为正式提交/分支留痕。
- 立即核查：提交前再次运行 `/opt/homebrew/bin/python3.11 -m pytest -o addopts='' tests/hermes_cli/test_safe_refactor_audit.py` 并确认独立审查已通过。
- 若受阻先排查：若需复核本轮证据，优先回读独立审查结论、M5-v2 文档、玄麟 `latest.json`、pytest 输出与三份核心产物文件。
