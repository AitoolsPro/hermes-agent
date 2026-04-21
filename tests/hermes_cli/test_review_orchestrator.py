from pathlib import Path

from hermes_cli.review_orchestrator import (
    AutomatedReviewResult,
    CallChainAnalysis,
    CorrectionDispatch,
    PytestExecution,
    build_correction_instructions,
    extract_call_chain_differences,
    run_automated_review,
    run_self_correcting_review,
)
from hermes_cli.safe_refactor_audit import AuditFinding, AuditReport, load_policy_bundle


SAFE_DIFF = """
diff --git a/hermes_cli/review_orchestrator.py b/hermes_cli/review_orchestrator.py
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/hermes_cli/review_orchestrator.py
@@ -0,0 +1,4 @@
+def shared_gate():
+    return True
+
+print(shared_gate())
""".strip()

SHARED_HELPER_DIFF = """
diff --git a/hermes_cli/review_orchestrator.py b/hermes_cli/review_orchestrator.py
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/hermes_cli/review_orchestrator.py
@@ -0,0 +1,4 @@
+def shared_gate():
+    return True
+
+print(shared_gate())
diff --git a/hermes_cli/safe_refactor_runtime.py b/hermes_cli/safe_refactor_runtime.py
new file mode 100644
index 0000000..2222222
--- /dev/null
+++ b/hermes_cli/safe_refactor_runtime.py
@@ -0,0 +1,4 @@
+from hermes_cli.review_orchestrator import shared_gate
+
+def pipeline():
+    return shared_gate()
""".strip()



def _pytest_ok() -> PytestExecution:
    return PytestExecution(
        command=("pytest", "tests/hermes_cli/test_safe_refactor_runtime.py"),
        exit_code=0,
        output="4 passed\n",
        summary="exit=0; 4 passed",
    )



def test_extract_call_chain_differences_detects_shared_helpers():
    analysis = extract_call_chain_differences(SHARED_HELPER_DIFF)

    assert analysis.approval_ready is True
    assert analysis.dual_implementation_detected is False
    assert "shared_gate" in analysis.shared_helpers



def test_run_automated_review_approves_candidate_when_audit_clean_and_call_chain_shared():
    repo_root = Path(__file__).resolve().parents[2]
    policy = load_policy_bundle(repo_root)

    result = run_automated_review(
        SHARED_HELPER_DIFF,
        policy_bundle=policy,
        pytest_command=("pytest",),
        pytest_runner=lambda _command: _pytest_ok(),
        report_reader=lambda _path: "共享 helper 已接线，pytest 通过。",
    )

    assert result.verdict == "APPROVE_CANDIDATE"
    assert result.audit_report.rejected is False
    assert result.pytest.exit_code == 0
    assert result.call_chain.approval_ready is True



def test_run_self_correcting_review_retries_until_approve_candidate():
    repo_root = Path(__file__).resolve().parents[2]
    policy = load_policy_bundle(repo_root)
    seen_diffs: list[str] = []

    def pytest_runner(_command) -> PytestExecution:
        return _pytest_ok()

    def correction_dispatcher(attempt_number: int, review_result: AutomatedReviewResult, instructions: str) -> CorrectionDispatch:
        assert attempt_number == 1
        assert review_result.verdict == "REJECT_HARD"
        assert "policy.file_scope_restricted" in instructions
        return CorrectionDispatch(diff_text=SHARED_HELPER_DIFF, report_text="已收敛为共享 helper 安全 diff")

    initial_diff = """
diff --git a/hermes_cli/main.py b/hermes_cli/main.py
index 1111111..2222222 100644
--- a/hermes_cli/main.py
+++ b/hermes_cli/main.py
@@ -1 +1 @@
-_require_tty(\"uninstall\")
+pass
""".strip()

    result = run_self_correcting_review(
        initial_diff,
        policy_bundle=policy,
        pytest_command=("pytest",),
        pytest_runner=lambda command: seen_diffs.append("pytest") or pytest_runner(command),
        report_reader=lambda _path: None,
        correction_dispatcher=correction_dispatcher,
    )

    assert result.verdict == "APPROVE_CANDIDATE"
    assert [attempt.review_result.verdict for attempt in result.attempts] == ["REJECT_HARD", "APPROVE_CANDIDATE"]
    assert len(result.correction_history) == 1



def test_build_correction_instructions_includes_m3_findings():
    review_result = AutomatedReviewResult(
        verdict="REJECT_HARD",
        stage_order=("m3_audit", "call_chain", "pytest", "report"),
        reasons=("M3 审计命中硬拒绝。",),
        audit_report=AuditReport(
            policy_id="hermes.safe_refactor.core",
            touched_files=("hermes_cli/main.py",),
            findings=(
                AuditFinding(
                    rule_id="policy.file_scope_restricted",
                    severity="REJECT_HARD",
                    path="hermes_cli/main.py",
                    line="hermes_cli/main.py",
                    source="policy",
                    message="Restricted file touched outside the direct-related allowlist.",
                ),
            ),
            risk_notes=(),
            parse_valid=True,
        ),
        call_chain=CallChainAnalysis(
            changed_python_paths=("hermes_cli/main.py",),
            shared_helpers=(),
            file_to_helpers={"hermes_cli/main.py": ()},
            dual_implementation_detected=False,
            approval_ready=False,
            summary="调用链证据不足",
        ),
        pytest=_pytest_ok(),
        report_text=None,
        report_considered=False,
        report_consistency="NOT_PROVIDED",
        report_scope_flags=(),
        machine_findings=(),
    )

    instructions = build_correction_instructions(review_result, 1)

    assert "policy.file_scope_restricted" in instructions
    assert "Attempt 1" in instructions
