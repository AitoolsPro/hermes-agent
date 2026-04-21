from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from hermes_cli.review_orchestrator import AutomatedReviewResult


_APPROVAL_TOKENS = {"y", "confirm"}


@dataclass(frozen=True)
class HumanGateDecision:
    approved: bool
    response: str
    prompt_text: str


class HumanGateController:
    def __init__(
        self,
        *,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
    ) -> None:
        self._input_fn = input_fn
        self._output_fn = output_fn

    def require_explicit_approval(self, review_result: AutomatedReviewResult) -> HumanGateDecision:
        prompt_text = build_approval_request(review_result)
        self._output_fn(prompt_text)
        response = self._input_fn("Approve deployment? [Y/Confirm]: ").strip()
        approved = response.lower() in _APPROVAL_TOKENS
        return HumanGateDecision(approved=approved, response=response, prompt_text=prompt_text)


def build_approval_request(review_result: AutomatedReviewResult) -> str:
    return (
        f"M6 gate: {review_result.verdict} | "
        f"m3={'REJECT_HARD' if review_result.audit_report.rejected else 'PASS'} | "
        f"pytest_exit={review_result.pytest.exit_code} | "
        f"reason={review_result.reasons[0] if review_result.reasons else 'none'}"
    )
