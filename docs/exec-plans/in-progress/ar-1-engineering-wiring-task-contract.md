## Task Contract（任务合同）

**Objective (目标)**  
基于 `origin/main` 当前最新主线重新立项，完成 AR-1「工程化接线收口」的三项收口目标：M5 自动读写战时文档、归档同步器、以及 M5→M6 的一键启动真实流水线。

**Scope / Watchouts (范围 / 警戒线)**  
IN: 只处理 AR-1 工程化接线收口；允许新增 `review_orchestrator.py`、`human_gate_controller.py`、`safe_refactor_runtime.py` 等最小必要运行时模块；允许补建或回写 AR-1 的 Task Contract / Status Ledger / Verification Chain / 结案报告 / 账本条目；允许补最小必要测试。  
OUT: 不回退到旧污染分支；不重新处理 PAC-CORE-001 收编；不改 `hermes_cli/main.py`、`hermes_cli/uninstall.py` 等业务链路；不削弱 M6 人工审批保险丝；不把“接线收口”扩写成新框架重做。  
WATCHOUTS: 当前 `origin/main` 只含 PAC 核心审计器，不含 AR-1 runtime 原型；必须以当前主线事实重建，不得假设旧脏工作树文件已存在；Task Contract 缺失时必须 fail-closed；Status Ledger 与 Verification Chain 允许按模板恢复；一键启动不得绕过合同恢复与 M6 物理停机；归档同步器更新账本时必须按当前战役名定点改 section。

**Inputs (输入)**  
- 基线仓库：`/tmp/ar1-mainline-closure`（由 `origin/main` 最新主线建立的隔离 worktree，当前 `HEAD=c6f3213d`）  
- 战役账本：`docs/exec-plans/tech-debt-tracker.md`  
- 主线收编法则：`docs/agents/mainline-integration-protocol.md`  
- 已入主线的 M3 核心：`policies/core_rules.yaml`、`hermes_cli/safe_refactor_audit.py`、`tests/hermes_cli/test_safe_refactor_audit.py`  
- 法典技能：`safe-refactor-loop`、`hermes-harness-task-contract`、`hermes-harness-status-ledger`、`hermes-harness-verification-chain`、`test-driven-development`

**Deliverables / Evidence (交付物 / 证据)**  
交付物：AR-1 任务合同、状态台账、验证链、`review_orchestrator.py`、`human_gate_controller.py`、`safe_refactor_runtime.py`、相关测试、更新后的 `tech-debt-tracker.md`、结案报告。  
证据：针对 runtime / gate / tracker 接线的 pytest 结果；关键文件回读；运行后状态台账与验证链自动回写结果；M6 显式停机提示；获得批准后生成的结案报告与账本同步结果。

**Done (完成标准)**  
以下条件必须同时成立：  
1. M5 能自动读取 Task Contract，并在运行后自动回写 Status Ledger 与 Verification Chain  
2. 归档同步器仅在 M6 获得显式批准后生成结案报告并同步 `tech-debt-tracker.md`  
3. 一键启动入口能从账本中选中 AR-1 并串起 M3 → M5 → M6 真实流水线  
4. 未显式允许测试替身时，不得注入假 `human_gate` 越过真实人审  
5. 全程未回退旧污染分支、未重开 PAC 收编、未削弱人工审批红线  
6. 最小相关测试通过，且至少覆盖：战时文档恢复/回写、归档同步、M6 停机、一键启动选战役、注入式 gate 防旁路
