from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
import sys
from typing import Callable, Iterable, Sequence

from hermes_cli.safe_refactor_audit import AuditFinding, AuditReport, parse_unified_diff, audit_diff, load_policy_bundle


_REVIEW_ORDER = ("m3_audit", "call_chain", "pytest", "report")
_PYTHON_KEYWORDS = {
    "if",
    "for",
    "while",
    "return",
    "print",
    "with",
    "assert",
    "and",
    "or",
    "not",
}
_CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")


@dataclass(frozen=True)
class CallChainAnalysis:
    changed_python_paths: tuple[str, ...]
    shared_helpers: tuple[str, ...]
    file_to_helpers: dict[str, tuple[str, ...]]
    dual_implementation_detected: bool
    approval_ready: bool
    summary: str


@dataclass(frozen=True)
class PytestExecution:
    command: tuple[str, ...]
    exit_code: int
    output: str
    summary: str


@dataclass(frozen=True)
class AutomatedReviewResult:
    verdict: str
    stage_order: tuple[str, ...]
    reasons: tuple[str, ...]
    audit_report: AuditReport
    call_chain: CallChainAnalysis
    pytest: PytestExecution
    report_text: str | None
    report_considered: bool
    report_consistency: str
    report_scope_flags: tuple[str, ...]
    machine_findings: tuple[AuditFinding, ...]


@dataclass(frozen=True)
class CorrectionDispatch:
    diff_text: str
    report_text: str | None = None
    report_path: str | Path | None = None


@dataclass(frozen=True)
class ReviewAttempt:
    attempt_number: int
    review_result: AutomatedReviewResult
    correction_instructions: str | None


@dataclass(frozen=True)
class SelfCorrectionReviewResult:
    verdict: str
    final_review: AutomatedReviewResult
    attempts: tuple[ReviewAttempt, ...]
    correction_history: tuple[str, ...]
    stopped_after_max_attempts: bool


def extract_call_chain_differences(diff_text: str) -> CallChainAnalysis:
    _parse_valid, parsed_diff = parse_unified_diff(diff_text)
    helper_map: dict[str, tuple[str, ...]] = {}
    python_paths: list[str] = []

    for path, diff_lines in parsed_diff.items():
        if not path.endswith(".py"):
            continue
        python_paths.append(path)
        helpers = sorted(_extract_called_helpers(line.text for line in diff_lines if line.kind == "added"))
        helper_map[path] = tuple(helpers)

    shared_helpers = _shared_helpers(helper_map.values())
    dual_implementation_detected = len(python_paths) >= 2 and not shared_helpers
    approval_ready = len(python_paths) >= 2 and bool(shared_helpers) and not dual_implementation_detected

    if not python_paths:
        summary = "没有可用于调用链分析的 Python 改动。"
    elif approval_ready:
        summary = f"检测到共享 helper：{', '.join(shared_helpers)}"
    elif dual_implementation_detected:
        summary = "检测到多文件 Python 改动但未复用共享 helper，存在双实现风险。"
    else:
        summary = "调用链证据不足，当前不能仅凭测试通过放行。"

    return CallChainAnalysis(
        changed_python_paths=tuple(python_paths),
        shared_helpers=tuple(shared_helpers),
        file_to_helpers=helper_map,
        dual_implementation_detected=dual_implementation_detected,
        approval_ready=approval_ready,
        summary=summary,
    )


def run_pytest_command(command: Sequence[str], *, cwd: str | Path | None = None) -> PytestExecution:
    completed = subprocess.run(
        list(command),
        cwd=str(cwd) if cwd is not None else None,
        capture_output=True,
        text=True,
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    summary = _summarize_pytest_output(output, completed.returncode)
    return PytestExecution(command=tuple(command), exit_code=completed.returncode, output=output, summary=summary)


def read_optional_report(report_path: str | Path | None) -> str | None:
    if report_path is None:
        return None
    path = Path(report_path)
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def run_automated_review(
    diff_text: str,
    *,
    policy_bundle=None,
    pytest_command: Sequence[str] | None = None,
    report_path: str | Path | None = None,
    report_text: str | None = None,
    cwd: str | Path | None = None,
    audit_runner: Callable[[str], AuditReport] | None = None,
    call_chain_extractor: Callable[[str], CallChainAnalysis] = extract_call_chain_differences,
    pytest_runner: Callable[[Sequence[str]], PytestExecution] | None = None,
    report_reader: Callable[[str | Path | None], str | None] = read_optional_report,
) -> AutomatedReviewResult:
    if policy_bundle is None:
        repo_root = Path(cwd) if cwd is not None else Path(__file__).resolve().parents[1]
        policy_bundle = load_policy_bundle(repo_root)
    if audit_runner is None:
        audit_runner = lambda diff: audit_diff(diff, policy_bundle)
    if pytest_command is None:
        pytest_command = (sys.executable, "-m", "pytest")
    if pytest_runner is None:
        pytest_runner = lambda command: run_pytest_command(command, cwd=cwd)

    audit_report = audit_runner(diff_text)
    call_chain = call_chain_extractor(diff_text)
    pytest_result = pytest_runner(tuple(pytest_command))
    resolved_report_text = report_text if report_text is not None else report_reader(report_path)
    report_consistency, report_scope_flags = _evaluate_report(resolved_report_text)
    verdict, reasons = _synthesize_verdict(audit_report, call_chain, pytest_result, report_consistency)

    return AutomatedReviewResult(
        verdict=verdict,
        stage_order=_REVIEW_ORDER,
        reasons=tuple(reasons),
        audit_report=audit_report,
        call_chain=call_chain,
        pytest=pytest_result,
        report_text=resolved_report_text,
        report_considered=resolved_report_text is not None,
        report_consistency=report_consistency,
        report_scope_flags=tuple(report_scope_flags),
        machine_findings=audit_report.findings,
    )


def run_self_correcting_review(
    diff_text: str,
    *,
    policy_bundle=None,
    pytest_command: Sequence[str] | None = None,
    report_path: str | Path | None = None,
    report_text: str | None = None,
    cwd: str | Path | None = None,
    audit_runner: Callable[[str], AuditReport] | None = None,
    call_chain_extractor: Callable[[str], CallChainAnalysis] = extract_call_chain_differences,
    pytest_runner: Callable[[Sequence[str]], PytestExecution] | None = None,
    report_reader: Callable[[str | Path | None], str | None] = read_optional_report,
    correction_dispatcher: Callable[[int, AutomatedReviewResult, str], CorrectionDispatch | str] | None = None,
    max_attempts: int = 3,
) -> SelfCorrectionReviewResult:
    current_diff_text = diff_text
    current_report_path = report_path
    current_report_text = report_text
    attempts: list[ReviewAttempt] = []
    correction_history: list[str] = []

    for attempt_number in range(1, max_attempts + 1):
        review_result = run_automated_review(
            current_diff_text,
            policy_bundle=policy_bundle,
            pytest_command=pytest_command,
            report_path=current_report_path,
            report_text=current_report_text,
            cwd=cwd,
            audit_runner=audit_runner,
            call_chain_extractor=call_chain_extractor,
            pytest_runner=pytest_runner,
            report_reader=report_reader,
        )

        should_retry = review_result.verdict != "APPROVE_CANDIDATE" and attempt_number < max_attempts and correction_dispatcher is not None
        correction_instructions: str | None = None
        if should_retry:
            correction_instructions = build_correction_instructions(review_result, attempt_number)
            correction_history.append(correction_instructions)

        attempts.append(
            ReviewAttempt(
                attempt_number=attempt_number,
                review_result=review_result,
                correction_instructions=correction_instructions,
            )
        )

        if review_result.verdict == "APPROVE_CANDIDATE":
            return SelfCorrectionReviewResult(
                verdict=review_result.verdict,
                final_review=review_result,
                attempts=tuple(attempts),
                correction_history=tuple(correction_history),
                stopped_after_max_attempts=False,
            )

        if not should_retry:
            return SelfCorrectionReviewResult(
                verdict=review_result.verdict,
                final_review=review_result,
                attempts=tuple(attempts),
                correction_history=tuple(correction_history),
                stopped_after_max_attempts=attempt_number >= max_attempts,
            )

        dispatch = correction_dispatcher(attempt_number, review_result, correction_instructions)
        if isinstance(dispatch, str):
            dispatch = CorrectionDispatch(diff_text=dispatch)
        current_diff_text = dispatch.diff_text
        current_report_path = dispatch.report_path
        current_report_text = dispatch.report_text

    final_review = attempts[-1].review_result
    return SelfCorrectionReviewResult(
        verdict=final_review.verdict,
        final_review=final_review,
        attempts=tuple(attempts),
        correction_history=tuple(correction_history),
        stopped_after_max_attempts=True,
    )


def build_correction_instructions(review_result: AutomatedReviewResult, attempt_number: int) -> str:
    finding_lines = [_format_finding(finding) for finding in review_result.audit_report.findings]
    if not finding_lines:
        finding_lines = [f"verdict={review_result.verdict}"]
    joined_findings = "\n".join(f"- {line}" for line in finding_lines)
    joined_reasons = "\n".join(f"- {reason}" for reason in review_result.reasons) or "- 无综合理由"
    return (
        f"Attempt {attempt_number} correction request\n"
        f"Findings:\n{joined_findings}\n"
        f"Review blockers:\n{joined_reasons}\n"
        "Required action: address every listed finding, keep edits within the active battle scope, then resubmit an updated diff for a fresh M3 -> call_chain -> pytest -> report pass."
    )


def _extract_called_helpers(lines: Iterable[str]) -> set[str]:
    helpers: set[str] = set()
    for line in lines:
        for match in _CALL_RE.findall(line):
            if match not in _PYTHON_KEYWORDS:
                helpers.add(match)
    return helpers


def _shared_helpers(helper_sets: Iterable[tuple[str, ...]]) -> tuple[str, ...]:
    helper_sets = [set(items) for items in helper_sets if items]
    if len(helper_sets) < 2:
        return ()
    shared = set.intersection(*helper_sets)
    return tuple(sorted(shared))


def _evaluate_report(report_text: str | None) -> tuple[str, tuple[str, ...]]:
    if report_text is None:
        return "NOT_PROVIDED", ()
    return "CONSISTENT", ()


def _synthesize_verdict(
    audit_report: AuditReport,
    call_chain: CallChainAnalysis,
    pytest_result: PytestExecution,
    report_consistency: str,
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if audit_report.rejected:
        reasons.append("M3 审计命中硬拒绝，后续证据不得翻盘。")
        return "REJECT_HARD", reasons
    if not call_chain.approval_ready:
        reasons.append("调用链证据不足，当前结果属于 FAKE_WIN 风险。")
        return "FAKE_WIN", reasons
    if pytest_result.exit_code != 0:
        reasons.append("pytest 未通过，不能进入 APPROVE_CANDIDATE。")
        return "FAKE_WIN", reasons
    if report_consistency == "INCONSISTENT":
        reasons.append("实现报告与机器证据不一致。")
        return "WARN", reasons
    reasons.append("M3 非硬拒绝、调用链接线为真、pytest 通过。")
    return "APPROVE_CANDIDATE", reasons


def _summarize_pytest_output(output: str, exit_code: int) -> str:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    tail = lines[-1] if lines else "no pytest output"
    return f"exit={exit_code}; {tail}"


def _format_finding(finding: AuditFinding) -> str:
    location = f" @ {finding.path}" if finding.path else ""
    return f"{finding.severity}:{finding.rule_id}{location}: {finding.message}"
