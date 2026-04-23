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
- **状态**：最高优先级活跃战役（三刀联合收编准备完成；已形成候选 commit）
- **自动接管入口**：`docs/exec-plans/in-progress/ar-1-engineering-wiring-task-contract.md`
- **目标**：在 `origin/main` 基线上，把第一刀、第二刀、第三刀已完成成果收束为单一、可审计、合法的联合候选提交。
- **当前重点**：第一刀与第二刀主体验证为主线既有事实；第三刀归档同步 / tracker closure 合法差异已补回并通过四项测试；当前等待最终主线收编级验收。
- **历史验收输入**：`docs/exec-plans/completed/ar-1-engineering-wiring-acceptance-report.md` 仅作历史输入与边界核查依据，不得直接当作“已入主线”证明。

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
