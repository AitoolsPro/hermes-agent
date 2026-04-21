## Task Contract（任务合同）

**Objective (目标)**  
完成“Policy-as-Code：帝国法典核心”基建级重构，使 `hermes_cli/safe_refactor_audit.py` 成为由 `policies/core_rules.yaml` 驱动的通用动态审计引擎，并保持既有审计硬度不下降。

**Scope / Watchouts (范围 / 警戒线)**  
IN: 在仓库内建立 `policies/core_rules.yaml` 作为 canonical 规则文件；如确有需要设计 `~/.hermes/policies/` 本地 override 机制；补建并接线 `hermes_cli/safe_refactor_audit.py`、相关加载器与最小必要测试；使用 M4（玄麟）完成 YAML 架构方案与 Python 适配代码；使用 M5-v2 做自愈循环验证；回写台账、验证链与技术债账本。  
OUT: 不降低任何现有 TTY / confirm / 文件范围 / shell / PATH 审计硬度；不顺手扩展到与 safe-refactor-loop 无关的 CLI、Gateway、profile、wrapper 或安装链路；未获北冥统帅签字前不合并、不删除现有保护。  
WATCHOUTS: 当前仓库未落盘相关战时文档且 `safe_refactor_audit.py` 可能缺失，必须先建合同/台账/验证链再施工；若主仓与隔离 worktree 结构不一致，以隔离战场事实为准；YAML 中心化不得把硬编码红线软化成可随意 override 的低优先级配置；本地 override 只能做加严或显式白名单扩展，不得绕过红线。

**Inputs (输入)**  
用户指令要求读取/恢复 `docs/exec-plans/in-progress/architecture-safe-refactor-loop-status-ledger.md`、`docs/exec-plans/in-progress/architecture-safe-refactor-loop-verification-chain.md`、`docs/exec-plans/tech-debt-tracker.md`、`~/.hermes/skills/safe-refactor-loop/SKILL.md`；safe-refactor-loop 与 Hermes Harness 三件套技能；仓库路径 `/Users/beiming/hermes-agent-fork`，隔离 worktree `/tmp/policy-as-code-core-empire`，基线 `HEAD=812278f7497f3652c008144ee1b73ffaa01e26d5`；现有 `hermes_cli/main.py` 中 `cmd_uninstall` 仍保留 `_require_tty("uninstall")`，`hermes_cli/uninstall.py` 仍执行高危删除与 PATH 清理。

**Deliverables / Evidence (交付物 / 证据)**  
交付物：任务合同、状态台账、验证链、技术债账本条目、`policies/core_rules.yaml`、动态规则加载审计引擎代码、相关测试、玄麟执行留痕 JSON、M5-v2 审计结果、M6《统帅裁决请示书》。  
证据：隔离 worktree 的 git diff；关键文件回读；玄麟 `latest.json` 与 `records/*.json`；针对伪造 TTY 降级 Diff 的审计输出；pytest/最小验证命令输出；台账与验证链回写结果。

**Done (完成标准)**  
在隔离 worktree 中落成可加载的 `policies/core_rules.yaml` 与动态审计引擎；M4 玄麟提交的方案与代码已落盘且留痕；M5-v2 证明新架构对伪造的 TTY 降级 Diff 仍输出拒绝结论且无硬度回退；台账、验证链、技术债账本均已更新为当前真实状态；只有在得到 `APPROVE_CANDIDATE` 后才进入 M6 物理停机等待北冥统帅签字。  
