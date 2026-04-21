from pathlib import Path

from hermes_cli.human_gate_controller import HumanGateDecision
from hermes_cli.review_orchestrator import AutomatedReviewResult, CallChainAnalysis, PytestExecution
from hermes_cli.safe_refactor_audit import AuditReport
from hermes_cli.safe_refactor_runtime import (
    BattleDocumentPaths,
    launch_safe_refactor_from_tracker,
    restore_or_create_battle_documents,
    run_safe_refactor_pipeline,
    select_active_battle,
)


TASK_CONTRACT_TEXT = """## Task Contract（任务合同）

**Objective (目标)**  
完成 AR-1 工程化接线收口。

**Scope / Watchouts (范围 / 警戒线)**  
IN: 只处理 M5/M6 接线。  
OUT: 不削弱人工审批。  
WATCHOUTS: 不得绕过 M6。

**Inputs (输入)**  
- `docs/exec-plans/tech-debt-tracker.md`

**Deliverables / Evidence (交付物 / 证据)**  
交付物：战时文档接线、归档同步器、一键启动链。  
证据：战时文档回写、归档报告、M6 停机。

**Done (完成标准)**  
M5 读写文档、归档同步可跑、一键启动可进入 M6。
"""

STATUS_LEDGER_TEXT = """**Task Contract Snapshot (合同快照)**
- 目标：完成 AR-1 工程化接线收口。
- 范围边界：只处理 M5/M6 接线，不削弱人工审批。
- 完成标准：M5 读写文档、归档同步可跑、一键启动可进入 M6。

**Current State (当前状态)**
- 当前停点：待自动接管。
- 已完成：无。
- 未完成 / 当前阻塞：尚未自动回写战时文档。
- 当前判断：未完成

**Evidence Logged (证据登记)**
- 已有证据：已有任务合同。
- 证据对应结论：可以进入 safe-refactor-loop。
- 证据缺口：缺少自动回写、归档同步与一键启动证据。

**Next Handoff (下一步 / 接管指令)**
- 接手后第一步：运行 safe-refactor-loop。
- 立即核查：确认 M6 仍保留物理停机。
- 若受阻先排查：先查战时文档路径是否存在。
"""

VERIFICATION_CHAIN_TEXT = """## Verification Chain（默认验证链）

**Verification Target (验证目标)**
- 对应合同项：对应 AR-1 交付物 / 证据与完成标准。
- 目标 1：证明 M5 能读写战时文档。
- 目标 2：证明 APPROVE_CANDIDATE 会进入 M6。

**Verification Actions (验证动作)**
- 动作 1：运行 safe-refactor-loop 流水线。
- 动作 2：检查状态台账、验证链、归档报告与账本更新。

**Verification Result (验证结果)**
- 目标 1：未执行 —— 等待流水线结果。
- 目标 2：未执行 —— 等待流水线结果。

**Release / Handoff Gate (放行 / 接管闸门)**
- 当前判断：验证中
- 当前缺口：缺少自动执行证据。
- 接手后第一步：从账本接管任务。
- 接手入口：先看任务合同、状态台账、验证链。
"""

TRACKER_TEXT = """# Tech Debt Tracker / 代码层收敛任务候选清单

## 架构级升维战役

### AR-1：`safe-refactor-loop` 自动化防爆重构 Skill / 调度器
- **状态**：最高优先级活跃战役
- **目标**：将当前成功的人类主控流程固化为可执行状态机。
- **当前重点**：完成工程化接线收口。
"""


def _approved_review() -> AutomatedReviewResult:
    return AutomatedReviewResult(
        verdict="APPROVE_CANDIDATE",
        stage_order=("m3_audit", "call_chain", "pytest", "report"),
        reasons=("M3 非硬拒绝、调用链接线为真、pytest 通过。",),
        audit_report=AuditReport(
            policy_id="hermes.safe_refactor.core",
            touched_files=("hermes_cli/review_orchestrator.py", "hermes_cli/safe_refactor_runtime.py"),
            findings=(),
            risk_notes=(),
            parse_valid=True,
        ),
        call_chain=CallChainAnalysis(
            changed_python_paths=("hermes_cli/review_orchestrator.py", "hermes_cli/safe_refactor_runtime.py"),
            shared_helpers=("run_self_correcting_review",),
            file_to_helpers={
                "hermes_cli/review_orchestrator.py": ("run_self_correcting_review",),
                "hermes_cli/safe_refactor_runtime.py": ("run_self_correcting_review",),
            },
            dual_implementation_detected=False,
            approval_ready=True,
            summary="检测到共享 helper：run_self_correcting_review",
        ),
        pytest=PytestExecution(
            command=("pytest",),
            exit_code=0,
            output="1 passed\n",
            summary="exit=0; 1 passed",
        ),
        report_text="all good",
        report_considered=True,
        report_consistency="CONSISTENT",
        report_scope_flags=(),
        machine_findings=(),
    )


def _write_battle_docs(root: Path) -> BattleDocumentPaths:
    paths = BattleDocumentPaths(
        tracker_path=root / "docs/exec-plans/tech-debt-tracker.md",
        task_contract_path=root / "docs/exec-plans/in-progress/ar-1-engineering-wiring-task-contract.md",
        status_ledger_path=root / "docs/exec-plans/in-progress/architecture-safe-refactor-loop-status-ledger.md",
        verification_chain_path=root / "docs/exec-plans/in-progress/architecture-safe-refactor-loop-verification-chain.md",
        archive_report_path=root / "docs/exec-plans/completed/ar-1-engineering-wiring-acceptance-report.md",
        battle_name="AR-1",
    )
    paths.tracker_path.parent.mkdir(parents=True, exist_ok=True)
    paths.task_contract_path.parent.mkdir(parents=True, exist_ok=True)
    paths.status_ledger_path.parent.mkdir(parents=True, exist_ok=True)
    paths.verification_chain_path.parent.mkdir(parents=True, exist_ok=True)
    paths.archive_report_path.parent.mkdir(parents=True, exist_ok=True)
    paths.tracker_path.write_text(TRACKER_TEXT, encoding="utf-8")
    paths.task_contract_path.write_text(TASK_CONTRACT_TEXT, encoding="utf-8")
    paths.status_ledger_path.write_text(STATUS_LEDGER_TEXT, encoding="utf-8")
    paths.verification_chain_path.write_text(VERIFICATION_CHAIN_TEXT, encoding="utf-8")
    return paths


def test_restore_or_create_battle_documents_rebuilds_missing_ledgers(tmp_path):
    paths = _write_battle_docs(tmp_path)
    paths.status_ledger_path.unlink()
    paths.verification_chain_path.unlink()

    restored = restore_or_create_battle_documents(paths)

    assert paths.task_contract_path.exists()
    assert paths.status_ledger_path.exists()
    assert paths.verification_chain_path.exists()
    assert restored["status_ledger"].startswith("**Task Contract Snapshot (合同快照)**")
    assert restored["verification_chain"].startswith("## Verification Chain（默认验证链）")


def test_restore_or_create_battle_documents_requires_existing_task_contract(tmp_path):
    paths = _write_battle_docs(tmp_path)
    paths.task_contract_path.unlink()

    try:
        restore_or_create_battle_documents(paths)
    except FileNotFoundError as exc:
        assert str(paths.task_contract_path) in str(exc)
    else:
        raise AssertionError("缺少任务合同时必须直接失败，不能静默补造默认合同")


def test_pipeline_writes_back_war_docs_and_enters_m6_on_approve_candidate(tmp_path):
    paths = _write_battle_docs(tmp_path)
    gate_calls: list[str] = []

    result = run_safe_refactor_pipeline(
        paths,
        diff_text="safe diff",
        review_runner=lambda **_kwargs: _approved_review(),
        human_gate=lambda review: gate_calls.append(review.verdict) or HumanGateDecision(
            approved=False,
            response="N",
            prompt_text="M6 gate: APPROVE_CANDIDATE",
        ),
        allow_test_gate_override=True,
    )

    status_text = paths.status_ledger_path.read_text(encoding="utf-8")
    verification_text = paths.verification_chain_path.read_text(encoding="utf-8")

    assert result.review_result.verdict == "APPROVE_CANDIDATE"
    assert gate_calls == ["APPROVE_CANDIDATE"]
    assert "APPROVE_CANDIDATE" in status_text
    assert "M6 已停机等待北冥统帅输入 Y / Confirm" in status_text
    assert "目标 1：通过" in verification_text
    assert "当前判断：验证中" in verification_text


def test_archive_syncer_generates_acceptance_report_and_updates_tracker_after_human_approval(tmp_path):
    paths = _write_battle_docs(tmp_path)

    result = run_safe_refactor_pipeline(
        paths,
        diff_text="safe diff",
        review_runner=lambda **_kwargs: _approved_review(),
        human_gate=lambda _review: HumanGateDecision(
            approved=True,
            response="Confirm",
            prompt_text="M6 gate: APPROVE_CANDIDATE",
        ),
        allow_test_gate_override=True,
    )

    report_text = paths.archive_report_path.read_text(encoding="utf-8")
    tracker_text = paths.tracker_path.read_text(encoding="utf-8")

    assert result.archive_written is True
    assert "AR-1 工程化接线收口结案报告" in report_text
    assert "M5 能自动读取并回写战时文档" in report_text
    assert "阶段结案：工程化接线收口已完成" in tracker_text
    assert "见 `docs/exec-plans/completed/ar-1-engineering-wiring-acceptance-report.md`" in tracker_text


def test_human_rejection_does_not_archive_or_update_tracker(tmp_path):
    paths = _write_battle_docs(tmp_path)
    original_tracker = paths.tracker_path.read_text(encoding="utf-8")

    result = run_safe_refactor_pipeline(
        paths,
        diff_text="safe diff",
        review_runner=lambda **_kwargs: _approved_review(),
        human_gate=lambda _review: HumanGateDecision(
            approved=False,
            response="N",
            prompt_text="M6 gate: APPROVE_CANDIDATE",
        ),
        allow_test_gate_override=True,
    )

    assert result.archive_written is False
    assert not paths.archive_report_path.exists()
    assert paths.tracker_path.read_text(encoding="utf-8") == original_tracker


def test_human_gate_override_requires_explicit_test_flag(tmp_path):
    paths = _write_battle_docs(tmp_path)

    try:
        run_safe_refactor_pipeline(
            paths,
            diff_text="safe diff",
            review_runner=lambda **_kwargs: _approved_review(),
            human_gate=lambda _review: HumanGateDecision(
                approved=True,
                response="Confirm",
                prompt_text="M6 gate: APPROVE_CANDIDATE",
            ),
        )
    except ValueError as exc:
        assert "allow_test_gate_override" in str(exc)
    else:
        raise AssertionError("未显式允许时，不应接受注入式 human_gate 覆盖真实审批")


def test_launch_safe_refactor_from_tracker_selects_active_battle_and_runs_pipeline(tmp_path):
    paths = _write_battle_docs(tmp_path)
    launch_calls: list[str] = []

    result = launch_safe_refactor_from_tracker(
        tracker_path=paths.tracker_path,
        battle_paths={"AR-1": paths},
        diff_text="safe diff",
        pipeline_runner=lambda chosen_paths, **_kwargs: launch_calls.append(chosen_paths.battle_name) or {
            "battle_name": chosen_paths.battle_name,
            "entered_m6": True,
        },
    )

    assert select_active_battle(paths.tracker_path.read_text(encoding="utf-8")) == "AR-1"
    assert launch_calls == ["AR-1"]
    assert result["entered_m6"] is True
    assert result["battle_name"] == "AR-1"


def test_select_active_battle_does_not_cross_match_other_sections():
    tracker_text = """# tracker

### TDB-9：普通技术债
- **状态**：等待自动化接管
- **目标**：先放着

### BATCH-1：并行批次战役
- **状态**：最高优先级活跃战役
- **目标**：这是当前应被接管的战役
- **当前重点**：收口
"""

    assert select_active_battle(tracker_text) == "BATCH-1"


def test_stage_closure_updates_tracker_for_non_ar_battle_name(tmp_path):
    paths = BattleDocumentPaths(
        tracker_path=tmp_path / "docs/exec-plans/tech-debt-tracker.md",
        task_contract_path=tmp_path / "docs/exec-plans/in-progress/batch-1-task-contract.md",
        status_ledger_path=tmp_path / "docs/exec-plans/in-progress/batch-1-status-ledger.md",
        verification_chain_path=tmp_path / "docs/exec-plans/in-progress/batch-1-verification-chain.md",
        archive_report_path=tmp_path / "docs/exec-plans/completed/batch-1-acceptance-report.md",
        battle_name="BATCH-1",
    )
    for target in [
        paths.tracker_path,
        paths.task_contract_path,
        paths.status_ledger_path,
        paths.verification_chain_path,
        paths.archive_report_path,
    ]:
        target.parent.mkdir(parents=True, exist_ok=True)
    paths.tracker_path.write_text(
        """# tracker

### BATCH-1：并行批次战役
- **状态**：最高优先级活跃战役
- **目标**：完成批次收口。
- **当前重点**：等待工程化接线。
""",
        encoding="utf-8",
    )
    paths.task_contract_path.write_text(TASK_CONTRACT_TEXT.replace("AR-1", "BATCH-1"), encoding="utf-8")
    paths.status_ledger_path.write_text(STATUS_LEDGER_TEXT.replace("AR-1", "BATCH-1"), encoding="utf-8")
    paths.verification_chain_path.write_text(VERIFICATION_CHAIN_TEXT.replace("AR-1", "BATCH-1"), encoding="utf-8")

    run_safe_refactor_pipeline(
        paths,
        diff_text="safe diff",
        review_runner=lambda **_kwargs: _approved_review(),
        human_gate=lambda _review: HumanGateDecision(
            approved=True,
            response="Confirm",
            prompt_text="M6 gate: APPROVE_CANDIDATE",
        ),
        allow_test_gate_override=True,
    )

    tracker_text = paths.tracker_path.read_text(encoding="utf-8")
    assert "阶段结案：工程化接线收口已完成" in tracker_text
    assert "BATCH-1：并行批次战役" in tracker_text
