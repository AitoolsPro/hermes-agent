## Task Contract（任务合同）

**Objective (目标)**  
完成 PAC-CORE-001 的真正主线收编级验收，并在干净 `main` 基线上重建只包含 PAC 核心成果的合法候选。

**Scope / Watchouts (范围 / 警戒线)**  
IN: 恢复 `/tmp/policy-as-code-core-empire` 现场；读取并校验 `tech-debt-tracker.md`、`mainline-integration-protocol.md` 与 safe-refactor-loop 技能；在干净 `main` 基线上重建 PAC 候选；修正已知文档不一致；执行文件范围审查、代码与文档一致性审查、测试复验、Git 收编边界审查；仅在验收通过时执行 PAC 合法文件的 `git add`、`git commit`、`git push origin main`。  
OUT: 不再沿用“AR-1 主线收编任务”名义；不收编 `cli.py`、`hermes_cli/model_switch.py` 或任何 PAC 之外改动；不因已有 `Y` 签字而跳过 Git 边界审查；不在验收失败时强推。  
WATCHOUTS: 旧 PAC 候选叠在 `fix-custom-providers-multi-models` 之上，若不重建会夹带无关提交；现有文档存在 `4 passed` / `9 passed` 不一致，必须先修正再验收；`docs/agents/mainline-integration-protocol.md` 起始缺失，若不补齐将导致主线收编模式缺协议锚点。

**Inputs (输入)**  
仓库路径 `/tmp/policy-as-code-core-empire`；账本 `docs/exec-plans/tech-debt-tracker.md`；协议 `docs/agents/mainline-integration-protocol.md`；技能 `~/.hermes/skills/safe-refactor-loop/SKILL.md`；旧战果分支 `pac-core-001-policy-code`；干净基线 `main` / `origin/main` at `816e3e3774e1162e73220fd5fb2796524757bb5d`；旧 PAC 提交 `274492bd0f0679ca22b28f812ad9ab497dc99368`；当前重建候选分支 `pac-core-001-mainline-candidate`。

**Deliverables / Evidence (交付物 / 证据)**  
交付物：主线收编协议文档、PAC-CORE-001 主线收编任务合同、状态台账、验证链、修正后的 M5 文档、干净基线重建候选、验收结论。  
证据：`git log --graph` 证明候选从 `main` 重建；`git diff --name-status main..HEAD` 证明只含 PAC 文件；关键文件回读与差异核对；pytest 复验输出；最终 Git 状态与提交记录。

**Done (完成标准)**  
只有当 PAC 候选已在干净 `main` 基线上重建、文档与测试结果一致、四类验收全部通过、且 `main..HEAD` 不再夹带无关改动时，才允许执行收编 Git 动作；否则直接打回并按统帅模板汇报原因。
