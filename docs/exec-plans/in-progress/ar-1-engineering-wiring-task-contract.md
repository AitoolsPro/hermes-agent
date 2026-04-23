## Task Contract（任务合同）

**Objective (目标)**  
在干净 `origin/main` 基线上，把 AR-1 第一刀、第二刀、第三刀的已完成成果收束成单一、可审计、合法的联合候选提交，为最终主线收编验收做准备。

**Scope / Watchouts (范围 / 警戒线)**  
IN: 只处理三刀直接相关的代码、测试、任务合同、状态台账、验证链、账本与必要的历史验收引用；允许在独立 worktree 中形成单一候选提交，但止步于 commit。  
OUT: 不重构 M3；不改变 M5 / M6 判定逻辑；不混入三刀外 CLI / provider / website 改动；不触碰 PAC-CORE-001 核心；不 push；不 merge；不新增第四类改造。  
WATCHOUTS: 第一刀与第二刀大部分成果已在 `origin/main`，不得为“联合”而重复提交零差异文件；第三刀只能补回合法的归档同步与 tracker closure 边界，且必须保持“只有 M6 approved=True 才归档”；历史 acceptance report 只能作历史输入，不得伪装成“已入主线”证明。

**Inputs (输入)**  
- `docs/exec-plans/in-progress/architecture-safe-refactor-loop-status-ledger.md`  
- `docs/exec-plans/in-progress/architecture-safe-refactor-loop-verification-chain.md`  
- `docs/exec-plans/in-progress/ar-1-engineering-wiring-task-contract.md`  
- `docs/exec-plans/in-progress/ar-1-engineering-wiring-blueprint.md`  
- `docs/exec-plans/completed/ar-1-engineering-wiring-acceptance-report.md`  
- `docs/exec-plans/tech-debt-tracker.md`  
- 仓库外：`~/.hermes/skills/safe-refactor-loop/SKILL.md`  
- 代码基线：`origin/main`=`d6cd3e1307868118531de04a9b124638e51b6b0f`  
- 独立 worktree：`/private/tmp/ar1-three-cut-union-prep-20260424-0645a`

**Deliverables / Evidence (交付物 / 证据)**  
交付物：第三刀合法差异补回后的 `hermes_cli/safe_refactor_runtime.py`、`tests/hermes_cli/test_safe_refactor_runtime.py`，以及与“联合收编准备”边界一致的任务合同、状态台账、验证链、账本。  
证据：文件范围审查清单；代码与文档一致性审查；`tests/hermes_cli/test_safe_refactor_runtime.py`、`tests/hermes_cli/test_review_orchestrator.py`、`tests/hermes_cli/test_human_gate_controller.py`、`tests/hermes_cli/test_safe_refactor_audit.py` 复验结果；`git status --short`、`git diff --name-status origin/main..HEAD`、`git show --stat --summary HEAD` 边界核对结果。

**Done (完成标准)**  
1. 第一刀、第二刀中相对 `origin/main` 已零差异的文件只做审查，不重复进入候选提交  
2. 第三刀仅补回合法的归档同步 / tracker closure 差异，且运行时保持只有 `approved=True` 才写结案报告与更新账本  
3. `hermes_cli/safe_refactor_audit.py` 与 `tests/hermes_cli/test_safe_refactor_audit.py` 保持零改动  
4. 四个指定测试文件全部通过，且在干净 `origin/main` worktree 中仅带本轮候选文件即可通过  
5. 候选边界收束为单一可审计 commit，提交信息明确为“AR-1 三刀联合收编准备候选”  
6. 本轮停在 commit，不得 push，不得 merge，不得宣称已入主线
