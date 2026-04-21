**Task Contract Snapshot (合同快照)**
- 目标：完成 PAC-CORE-001 的真正主线收编级验收，并在干净 `main` 基线上重建只包含 PAC 核心成果的合法候选。
- 范围边界：允许重建 PAC 候选、补齐主线协议、修正文档不一致并执行四类验收；不允许混收 `cli.py`、`hermes_cli/model_switch.py` 或任何 PAC 之外改动，不允许验收失败仍强推。
- 完成标准：候选基于干净 `main` 重建，文档与代码一致，测试复验通过，Git 边界干净，只有在全部通过时才执行收编动作。

**Current State (当前状态)**
- 当前停点：PAC-CORE-001 主线收编已完成，PAC 合法文件已提交并推送到 `origin/main`。
- 已完成：已确认旧分支 `pac-core-001-policy-code` 叠在 `fix-custom-providers-multi-models` 之上；已在干净 `main` 上重建 `pac-core-001-mainline-candidate`；已补建 `docs/agents/mainline-integration-protocol.md`；已修正 M5 文档中的 `4 passed` / `9 passed` 不一致；已完成文件范围审查、代码与文档一致性审查、pytest 复验与 Git 收编边界审查；已提交 `264aab0d feat: PAC-CORE-001 mainline integration` 并推送到 `origin/main`。
- 未完成 / 当前阻塞：无。
- 当前判断：可收口

**Evidence Logged (证据登记)**
- 已有证据：`git log --graph --decorate --max-count=6` 可证明当前候选直接基于 `main`；旧分支图谱已证明前置祖先污染存在且已被隔离；`/opt/homebrew/bin/python3.11 -m pytest -o addopts='' tests/hermes_cli/test_safe_refactor_audit.py` 实测 `9 passed`；`tests/hermes_cli/test_safe_refactor_audit.py` 回读可见 9 个测试；核心代码回读可见 `parse_valid` fail-closed、`ALLOWED_OVERRIDE_KEYS` 约束与 `programmatic.uninstall_tty_guard_bypass` 拦截；`git diff --name-status origin/main..264aab0d^` 与收编前边界审查已证明未混入 `cli.py`、`hermes_cli/model_switch.py`；`git ls-remote --heads origin main` 与 `git rev-parse HEAD` 均为 `264aab0dc22320f59745da0ed234119e6c5c9252`。
- 证据对应结论：本轮已完成“先重建干净候选、再做主线验收、最后安全推送”的完整闭环，代码、测试与文档口径一致，且远端 `main` 已落入 PAC 合法收编提交。
- 证据缺口：无。

**Next Handoff (下一步 / 接管指令)**
- 接手后第一步：如需复核，先检查 `origin/main` 是否停在 `264aab0dc22320f59745da0ed234119e6c5c9252`。
- 立即核查：回看 `git show --stat --summary 264aab0d`、pytest 复验输出与主线协议，确认收编边界未漂移。
- 若受阻先排查：若远端出现后续并发提交，优先重新核对 `origin/main` 图谱与 PAC 文件范围，不要回退到旧的污染祖先链路。
