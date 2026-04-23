from hermes_cli.human_gate_controller import HumanGateController, build_approval_request
from hermes_cli.review_orchestrator import AutomatedReviewResult, CallChainAnalysis, PytestExecution
from hermes_cli.safe_refactor_audit import AuditReport


def _review_result() -> AutomatedReviewResult:
    return AutomatedReviewResult(
        verdict="APPROVE_CANDIDATE",
        stage_order=("m3_audit", "call_chain", "pytest", "report"),
        reasons=("M3 非硬拒绝、调用链接线为真、pytest 通过。",),
        audit_report=AuditReport(
            policy_id="hermes.safe_refactor.core",
            touched_files=("hermes_cli/review_orchestrator.py",),
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
            output="3 passed\n",
            summary="exit=0; 3 passed",
        ),
        report_text="all good",
        report_considered=True,
        report_consistency="CONSISTENT",
        report_scope_flags=(),
        machine_findings=(),
    )


def test_m6_accepts_explicit_y_or_confirm_and_prints_compact_request(capsys):
    prompts: list[str] = []
    controller_y = HumanGateController(input_fn=lambda prompt: prompts.append(prompt) or "Y")
    decision_y = controller_y.require_explicit_approval(_review_result())
    out_y = capsys.readouterr().out

    assert decision_y.approved is True
    assert prompts == ["北冥是否批准进入下一步？[Y/Confirm]: "]
    assert "《北冥裁决请示书》" in out_y
    assert "当前裁决: APPROVE_CANDIDATE" in out_y
    assert "pytest: exit=0" in out_y

    controller_confirm = HumanGateController(input_fn=lambda _prompt: "Confirm")
    decision_confirm = controller_confirm.require_explicit_approval(_review_result())

    assert decision_confirm.approved is True
    assert build_approval_request(_review_result()).startswith("《北冥裁决请示书》")


def test_m6_rejects_non_explicit_inputs():
    controller = HumanGateController(input_fn=lambda _prompt: "yes")
    decision = controller.require_explicit_approval(_review_result())

    assert decision.approved is False
    assert decision.response == "yes"
