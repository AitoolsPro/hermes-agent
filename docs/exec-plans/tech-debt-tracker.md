# Tech Debt Tracker / 代码层收敛任务候选清单

> 定位：这里只记录已经被摸排坐实、但需要按战役单开治理的代码层收敛候选任务。  
> 它不是风险索引，也不是执行现场。  
> 这里的职责是把“后续应该单开任务治理的技术债 / 架构债”按优先级立账。

## 已解决

### PAC-CORE-001：Policy-as-Code 帝国法典核心 ✅
- **状态**：已入主线（`origin/main`），见 `docs/exec-plans/in-progress/pac-core-001-mainline-task-contract.md`
- **解决结果**：
  - `policies/core_rules.yaml` 已作为 canonical 规则源入主线
  - `hermes_cli/safe_refactor_audit.py` 已具备声明式规则 + 编程式审计双引擎
  - PAC 主线收编已闭环；后续扩展必须基于当前 `origin/main` 重新立项，不得回退旧污染分支

## 架构级升维战役

### AR-1：`safe-refactor-loop` 自动化防爆重构 Skill / 调度器
- **状态**：最高优先级活跃战役（阶段结案：工程化接线收口已完成，见 `docs/exec-plans/completed/ar-1-engineering-wiring-acceptance-report.md`）
- **目标**：把已入主线的 M3 核心继续接成可执行状态机，完成 M5 自动读写战时文档、归档同步器、以及 M5→M6 的一键启动真实流水线。
- **当前重点**：工程化接线收口已完成；下一阶段转入 M4 / M1 / M2 / M7 的持续工程化。

## P1

### TDB-3：`uninstall` CLI 参数语义与实现对齐
- **状态**：等待自动化接管
- **现状**：CLI 暴露了 `--full / --yes` 等参数，但实现仍可能强依赖交互确认。
- **风险**：
  - 参数语义与实际行为不一致
  - Agent 或用户误以为“无交互可执行”
  - 自动化脚本行为不可预测
- **建议治理方向**：
  - 统一 CLI 宣称行为与真实执行行为
  - 明确自动化安全边界

### TDB-4：`rename_profile()` 的 service 清理条件不完整
- **状态**：等待自动化接管
- **现状**：只在 gateway 正在运行时才清理旧 service，可能导致残留。
- **风险**：
  - 旧 service 留存
  - profile rename 后环境状态不干净
  - 后续排障困难
- **建议治理方向**：
  - 将 rename 时的 service / wrapper 清理规则显式化并统一

## P2

### TDB-5：active profile 读取链轻量分叉
- **状态**：等待自动化接管
- **现状**：启动期与其他路径存在轻量分叉，没有完全复用一条主链。
- **风险**：
  - profile 解析逻辑不完全一致
  - 边缘情况下 `HERMES_HOME` 作用域漂移
  - 后续继续复制逻辑的概率变高
- **建议治理方向**：
  - 统一 active profile 与 `HERMES_HOME` 解析源
  - 减少启动期分叉
