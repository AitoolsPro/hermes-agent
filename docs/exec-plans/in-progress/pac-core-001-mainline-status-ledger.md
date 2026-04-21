**Task Contract Snapshot (合同快照)**
- 目标：完成 PAC-CORE-001 的真正主线收编级验收，并在干净 `main` 基线上重建只包含 PAC 核心成果的合法候选。
- 范围边界：允许重建 PAC 候选、补齐主线协议、修正文档不一致并执行四类验收；不允许混收 `cli.py`、`hermes_cli/model_switch.py` 或任何 PAC 之外改动，不允许验收失败仍强推。
- 完成标准：候选基于干净 `main` 重建，文档与代码一致，测试复验通过，Git 边界干净，只有在全部通过时才执行收编动作。

**Current State (当前状态)**
- 当前停点：已完成四类主线收编验收，判定 PAC-CORE-001 可进入正式 Git 收编动作。
- 已完成：已确认旧分支 `pac-core-001-policy-code` 叠在 `fix-custom-providers-multi-models` 之上；已在干净 `main` 上重建 `pac-core-001-mainline-candidate`；已补建 `docs/agents/mainline-integration-protocol.md`；已修正 M5 文档中的 `4 passed` / `9 passed` 不一致；已完成文件范围审查、代码与文档一致性审查、pytest 复验与 Git 收编边界审查。
- 未完成 / 当前阻塞：尚未执行最终 `git add`、`git commit`、`git push origin main`。
- 当前判断：可收口

**Evidence Logged (证据登记)**
- 已有证据：`git log --graph --decorate --max-count=6` 可证明当前候选直接基于 `main`；旧分支图谱已证明前置祖先污染存在且已被隔离；`git status --short` 仅出现 PAC 合法文档与代码文件；`/opt/homebrew/bin/python3.11 -m pytest -o addopts='' tests/hermes_cli/test_safe_refactor_audit.py` 实测 `9 passed`；`tests/hermes_cli/test_safe_refactor_audit.py` 回读可见 9 个测试；核心代码回读可见 `parse_valid` fail-closed、`ALLOWED_OVERRIDE_KEYS` 约束与 `programmatic.uninstall_tty_guard_bypass` 拦截；M5/M6 文档、协议文档与任务合同均已落盘。
- 证据对应结论：本轮已完成“先重建干净候选、再做主线验收”的前置纪律，代码、测试与文档口径一致，且当前工作树中不存在 PAC 范围之外的待收编文件。
- 证据缺口：仅剩正式 Git 收编动作本身尚未执行。

**Next Handoff (下一步 / 接管指令)**
- 接手后第一步：若继续收编，先仅对 PAC 合法文件执行 `git add` 并生成正式收编提交。
- 立即核查：提交前后都检查 `git status --short`、`git show --stat --summary HEAD` 与 `git diff --name-status main..HEAD`，确认无越界文件。
- 若受阻先排查：若 Git 边界变化异常，优先检查是否误纳入 `cli.py`、`hermes_cli/model_switch.py` 或其他未列入协议的文件。
