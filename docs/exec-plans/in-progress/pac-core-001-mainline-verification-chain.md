## Verification Chain（默认验证链）

**Verification Target (验证目标)**
- 对应合同项：对应“干净 `main` 基线重建”“修正文档不一致”“四类主线收编验收”“仅在通过时执行 Git 收编动作”的交付物与完成标准。
- 目标 1：证明 PAC 候选已经在干净 `main` 基线上重建，不再夹带 `fix-custom-providers-multi-models` 前置改动。
- 目标 2：证明文档中的 `4 passed` / `9 passed` 不一致已修正，且代码、文档、测试口径一致。
- 目标 3：证明文件范围审查、代码与文档一致性审查、测试复验、Git 收编边界审查全部完成并得出可判定结果。
- 目标 4：证明只有在前 3 项全部通过时，才允许执行 PAC 合法文件的收编 Git 动作。

**Verification Actions (验证动作)**
- 动作 1：检查 `git log --graph`、`git merge-base main HEAD`、`git diff --name-status main..HEAD` 与 `git show --stat --summary HEAD`，验证候选祖先与收编边界。
- 动作 2：回读 `policies/core_rules.yaml`、`hermes_cli/safe_refactor_audit.py`、`tests/hermes_cli/test_safe_refactor_audit.py`、`tech-debt-tracker.md`、M5/M6 文档与主线协议，核对代码和文档是否一致。
- 动作 3：运行 `/opt/homebrew/bin/python3.11 -m pytest -o addopts='' tests/hermes_cli/test_safe_refactor_audit.py`，验证测试结果与文档中的 `9 passed` 一致。
- 动作 4：若前述结果全部通过，再执行仅含 PAC 合法文件的 `git add`、`git commit`、`git push origin main`；若任一项不通过，停止在打回结论。

**Verification Result (验证结果)**
- 目标 1：通过 —— `git log --graph --decorate --max-count=6` 与 `git merge-base main HEAD` 显示当前候选直接基于 `main=816e3e3774e1162e73220fd5fb2796524757bb5d`，已脱离 `fix-custom-providers-multi-models` 前置祖先污染。
- 目标 2：通过 —— M5 文档已修正为 `9 passed`；pytest 实测 `9 passed`；测试文件回读可见 9 个测试；核心代码与文档都明确包含 `parse_valid` fail-closed、override scope consistency 与 TTY 降级拦截口径。
- 目标 3：通过 —— 文件范围审查确认当前工作树仅含 PAC 合法文件；代码与文档一致性审查通过；pytest 复验通过；Git 收编边界审查确认未混入 `cli.py`、`hermes_cli/model_switch.py`。
- 目标 4：通过 —— 根据前 3 项结果，已执行仅含 PAC 合法文件的 Git 收编动作，并将 `264aab0d feat: PAC-CORE-001 mainline integration` 推送到 `origin/main`。

**Release / Handoff Gate (放行 / 接管闸门)**
- 当前判断：可收口
- 当前缺口：无。
- 接手后第一步：如需复核，先检查 `origin/main` 是否停在 `264aab0dc22320f59745da0ed234119e6c5c9252`。
- 接手入口：先看 `docs/agents/mainline-integration-protocol.md`、本轮 Task Contract、Verification Chain 与 `git show --stat --summary 264aab0d`。
