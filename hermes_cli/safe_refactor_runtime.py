from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Callable

from hermes_cli.human_gate_controller import HumanGateDecision, HumanGateController
from hermes_cli.review_orchestrator import run_self_correcting_review


@dataclass(frozen=True)
class BattleDocumentPaths:
    tracker_path: Path
    task_contract_path: Path
    status_ledger_path: Path
    verification_chain_path: Path
    archive_report_path: Path
    battle_name: str


@dataclass(frozen=True)
class SafeRefactorRuntimeResult:
    battle_name: str
    review_result: Any
    human_gate_decision: HumanGateDecision | None
    archive_written: bool
    entered_m6: bool


def select_active_battle(tracker_text: str) -> str:
    battle_sections = re.findall(r"(?ms)^###\s+([^\n]+)\n(.*?)(?=^###\s+|\Z)", tracker_text)
    waiting_battle: str | None = None

    for header, body in battle_sections:
        battle_name = header.split("：", 1)[0].strip()
        status_match = re.search(r"^- \*\*状态\*\*：(.*)$", body, re.M)
        if not status_match:
            continue
        status_text = status_match.group(1)
        if "最高优先级活跃战役" in status_text:
            return battle_name
        if waiting_battle is None and "等待自动化接管" in status_text:
            waiting_battle = battle_name

    if waiting_battle is not None:
        return waiting_battle
    raise ValueError("未在账本中找到可接管战役")


def restore_or_create_battle_documents(paths: BattleDocumentPaths) -> dict[str, str]:
    if not paths.task_contract_path.exists():
        raise FileNotFoundError(f"缺少任务合同，不能自动补造：{paths.task_contract_path}")
    task_contract = paths.task_contract_path.read_text(encoding="utf-8")
    status_ledger = _read_or_create(paths.status_ledger_path, _default_status_ledger(paths.battle_name, task_contract))
    verification_chain = _read_or_create(paths.verification_chain_path, _default_verification_chain(paths.battle_name))
    return {
        "task_contract": task_contract,
        "status_ledger": status_ledger,
        "verification_chain": verification_chain,
    }


def run_safe_refactor_pipeline(
    paths: BattleDocumentPaths,
    *,
    diff_text: str,
    review_runner: Callable[..., Any] = run_self_correcting_review,
    human_gate: Callable[[Any], HumanGateDecision] | None = None,
    allow_test_gate_override: bool = False,
    **review_kwargs: Any,
) -> SafeRefactorRuntimeResult:
    docs = restore_or_create_battle_documents(paths)
    review_result = review_runner(diff_text=diff_text, **review_kwargs)
    final_review = getattr(review_result, "final_review", review_result)
    entered_m6 = final_review.verdict == "APPROVE_CANDIDATE"

    human_gate_decision: HumanGateDecision | None = None
    if entered_m6:
        if human_gate is not None and not allow_test_gate_override:
            raise ValueError("注入式 human_gate 仅允许用于测试；如确需覆盖，请显式传入 allow_test_gate_override=True")
        gate_callable = human_gate
        if gate_callable is None:
            gate_callable = HumanGateController().require_explicit_approval
        human_gate_decision = gate_callable(final_review)

    _write_status_ledger(
        paths.status_ledger_path,
        battle_name=paths.battle_name,
        objective_line=_extract_objective_line(docs["task_contract"]),
        review_verdict=final_review.verdict,
        entered_m6=entered_m6,
        human_gate_decision=human_gate_decision,
    )
    _write_verification_chain(
        paths.verification_chain_path,
        review_verdict=final_review.verdict,
        entered_m6=entered_m6,
        archive_ready=bool(human_gate_decision and human_gate_decision.approved),
    )

    archive_written = False
    if human_gate_decision and human_gate_decision.approved:
        _write_archive_report(paths, docs)
        _update_tracker_for_stage_closure(paths)
        archive_written = True

    return SafeRefactorRuntimeResult(
        battle_name=paths.battle_name,
        review_result=final_review,
        human_gate_decision=human_gate_decision,
        archive_written=archive_written,
        entered_m6=entered_m6,
    )


def launch_safe_refactor_from_tracker(
    *,
    tracker_path: str | Path,
    battle_paths: dict[str, BattleDocumentPaths],
    diff_text: str,
    pipeline_runner: Callable[..., Any] = run_safe_refactor_pipeline,
    **pipeline_kwargs: Any,
) -> Any:
    tracker = Path(tracker_path)
    battle_name = select_active_battle(tracker.read_text(encoding="utf-8"))
    if battle_name not in battle_paths:
        raise KeyError(f"账本中的战役 {battle_name} 没有对应路径配置")
    return pipeline_runner(battle_paths[battle_name], diff_text=diff_text, **pipeline_kwargs)


def _read_or_create(path: Path, default_text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(default_text, encoding="utf-8")
        return default_text
    return path.read_text(encoding="utf-8")


def _extract_objective_line(task_contract_text: str) -> str:
    lines = task_contract_text.splitlines()
    for index, line in enumerate(lines):
        if line.strip().startswith("**Objective"):
            for follower in lines[index + 1 :]:
                stripped = follower.strip()
                if stripped:
                    return stripped
    return "完成 safe-refactor-loop 工程化接线收口。"


def _write_status_ledger(
    path: Path,
    *,
    battle_name: str,
    objective_line: str,
    review_verdict: str,
    entered_m6: bool,
    human_gate_decision: HumanGateDecision | None,
) -> None:
    if entered_m6:
        current_stop = "M6 已停机等待北冥统帅输入 Y / Confirm"
        done_items = f"M5 已自动读取任务合同、状态台账、验证链并回写当前裁决；当前裁决为 {review_verdict}。"
        current_judgment = "验证中"
        evidence_gap = "若未获统帅签字，缺少最终放行证据。"
    else:
        current_stop = "M5 自动复审已完成，但尚未进入 M6"
        done_items = f"M5 已自动读取任务合同、状态台账、验证链并回写当前裁决；当前裁决为 {review_verdict}。"
        current_judgment = "未完成"
        evidence_gap = "尚未获得 APPROVE_CANDIDATE，不能进入 M6。"

    if human_gate_decision and human_gate_decision.approved:
        current_stop = "M6 已收到北冥统帅签字，允许进入结案归档"
        current_judgment = "可收口"
        evidence_gap = "无当前阶段缺口。"

    text = (
        "**Task Contract Snapshot (合同快照)**\n"
        f"- 目标：{objective_line}\n"
        "- 范围边界：只处理 M5 自动复审、战时文档回写、归档同步与 M6 接线；不削弱人工审批。\n"
        "- 完成标准：M5 能自动读写战时文档，APPROVE_CANDIDATE 会进入 M6，归档同步器可生成结案报告并更新账本。\n\n"
        "**Current State (当前状态)**\n"
        f"- 当前停点：{current_stop}\n"
        f"- 已完成：{done_items}\n"
        "- 未完成 / 当前阻塞：最终放行仍受 M6 人工签字控制；没有统帅签字不得合并。\n"
        f"- 当前判断：{current_judgment}\n\n"
        "**Evidence Logged (证据登记)**\n"
        f"- 已有证据：M5 已写回 review_verdict={review_verdict}；entered_m6={'yes' if entered_m6 else 'no'}。\n"
        f"- 证据对应结论：{battle_name} 已能从战时文档恢复现场并把复审结果写回当前战场。\n"
        f"- 证据缺口：{evidence_gap}\n\n"
        "**Next Handoff (下一步 / 接管指令)**\n"
        "- 接手后第一步：若 M6 已停机，则只等待北冥统帅输入 Y / Confirm；若未进 M6，则继续修复直到 APPROVE_CANDIDATE。\n"
        "- 立即核查：确认 M5 仍只负责自动复审与自愈，不负责最终放行。\n"
        "- 若受阻先排查：先查战时文档路径、review verdict 与人审闸门是否一致。\n"
    )
    path.write_text(text, encoding="utf-8")


def _write_verification_chain(path: Path, *, review_verdict: str, entered_m6: bool, archive_ready: bool) -> None:
    target1 = "通过" if review_verdict == "APPROVE_CANDIDATE" else "不通过"
    target2 = "通过" if entered_m6 else "不通过"
    target3 = "通过" if archive_ready else "未执行"
    gate = "可收口" if archive_ready else "验证中"
    gap = "无。" if archive_ready else "若未获统帅签字或未归档，则仍缺最终收口证据。"
    text = (
        "## Verification Chain（默认验证链）\n\n"
        "**Verification Target (验证目标)**\n"
        "- 对应合同项：对应 AR-1 工程化接线交付物、证据与完成标准。\n"
        "- 目标 1：证明 M5 能自动读取并回写 Task Contract / Status Ledger / Verification Chain。\n"
        "- 目标 2：证明当 M5 给出 APPROVE_CANDIDATE 时，系统会立即进入 M6。\n"
        "- 目标 3：证明归档同步器能生成结案报告并回写 tech-debt-tracker。\n\n"
        "**Verification Actions (验证动作)**\n"
        "- 动作 1：恢复或建立任务合同、状态台账、验证链，并运行 safe-refactor-loop。\n"
        "- 动作 2：检查状态台账与验证链是否已被自动回写。\n"
        "- 动作 3：如获统帅签字，检查结案报告与 tech-debt-tracker 是否已同步。\n\n"
        "**Verification Result (验证结果)**\n"
        f"- 目标 1：{target1} —— 当前 review_verdict={review_verdict}，且战时文档已被自动回写。\n"
        f"- 目标 2：{target2} —— {'系统已在 APPROVE_CANDIDATE 后进入 M6 并停机等待审批。' if entered_m6 else '当前裁决未进入 M6。'}\n"
        f"- 目标 3：{target3} —— {'结案报告与账本更新已完成。' if archive_ready else '尚未完成统帅签字后的归档同步。'}\n\n"
        "**Release / Handoff Gate (放行 / 接管闸门)**\n"
        f"- 当前判断：{gate}\n"
        f"- 当前缺口：{gap}\n"
        "- 接手后第一步：若已进入 M6，则等待北冥统帅输入 Y / Confirm；若已签字，则核查归档报告。\n"
        "- 接手入口：先看任务合同、状态台账、验证链与最新结案报告。\n"
    )
    path.write_text(text, encoding="utf-8")


def _write_archive_report(paths: BattleDocumentPaths, docs: dict[str, str]) -> None:
    report = (
        f"# {paths.battle_name} 工程化接线收口结案报告\n\n"
        "## 1. 任务合同（Task Contract）\n\n"
        f"{docs['task_contract']}\n\n"
        "---\n\n"
        "## 2. 结案结论\n\n"
        "- M5 能自动读取并回写战时文档。\n"
        "- 归档同步器已生成本结案报告并准备同步账本。\n"
        "- 一键启动链已能从账本接管任务并把 APPROVE_CANDIDATE 送入 M6。\n"
        "- M6 仍保留物理停机；没有北冥统帅签字，任何代码都不准合并。\n\n"
        "## 3. 最终状态台账\n\n"
        f"{paths.status_ledger_path.read_text(encoding='utf-8')}\n\n"
        "## 4. 最终验证链\n\n"
        f"{paths.verification_chain_path.read_text(encoding='utf-8')}\n"
    )
    paths.archive_report_path.parent.mkdir(parents=True, exist_ok=True)
    paths.archive_report_path.write_text(report, encoding="utf-8")


def _update_tracker_for_stage_closure(paths: BattleDocumentPaths) -> None:
    tracker_text = paths.tracker_path.read_text(encoding="utf-8")
    section_pattern = re.compile(rf"(?ms)^###\s+{re.escape(paths.battle_name)}：([^\n]+)\n(.*?)(?=^###\s+|\Z)")
    match = section_pattern.search(tracker_text)
    if not match:
        raise ValueError(f"未在账本中找到战役段落：{paths.battle_name}")

    title_suffix = match.group(1).strip()
    replacement = (
        f"### {paths.battle_name}：{title_suffix}\n"
        f"- **状态**：最高优先级活跃战役（阶段结案：工程化接线收口已完成，见 `docs/exec-plans/completed/{paths.archive_report_path.name}`）\n"
        "- **目标**：将当前成功的人类主控流程固化为可执行状态机。\n"
        "- **当前重点**：工程化接线收口已完成；下一阶段转入 M4 / M1 / M2 / M7 的持续工程化。\n"
    )
    tracker_text = tracker_text[: match.start()] + replacement + tracker_text[match.end() :]
    paths.tracker_path.write_text(tracker_text, encoding="utf-8")


def _default_status_ledger(_battle_name: str, task_contract_text: str) -> str:
    return (
        "**Task Contract Snapshot (合同快照)**\n"
        f"- 目标：{_extract_objective_line(task_contract_text)}\n"
        "- 范围边界：只处理工程化接线，不削弱人工审批。\n"
        "- 完成标准：M5 读写文档、归档同步与 M6 接线全部成立。\n\n"
        "**Current State (当前状态)**\n"
        "- 当前停点：待自动接管。\n"
        "- 已完成：任务合同已恢复。\n"
        "- 未完成 / 当前阻塞：尚未运行 safe-refactor-loop。\n"
        "- 当前判断：未完成\n\n"
        "**Evidence Logged (证据登记)**\n"
        "- 已有证据：任务合同已恢复。\n"
        "- 证据对应结论：可以进入 safe-refactor-loop。\n"
        "- 证据缺口：缺少自动回写与归档同步证据。\n\n"
        "**Next Handoff (下一步 / 接管指令)**\n"
        "- 接手后第一步：运行 safe-refactor-loop。\n"
        "- 立即核查：确认 M6 仍保留物理停机。\n"
        "- 若受阻先排查：先查战时文档路径是否存在。\n"
    )


def _default_verification_chain(battle_name: str) -> str:
    return (
        "## Verification Chain（默认验证链）\n\n"
        "**Verification Target (验证目标)**\n"
        f"- 对应合同项：对应 {battle_name} 交付物 / 证据与完成标准。\n"
        "- 目标 1：证明 M5 能读写战时文档。\n"
        "- 目标 2：证明 APPROVE_CANDIDATE 会进入 M6。\n\n"
        "**Verification Actions (验证动作)**\n"
        "- 动作 1：运行 safe-refactor-loop 流水线。\n"
        "- 动作 2：检查状态台账、验证链、归档报告与账本更新。\n\n"
        "**Verification Result (验证结果)**\n"
        "- 目标 1：未执行 —— 等待流水线结果。\n"
        "- 目标 2：未执行 —— 等待流水线结果。\n\n"
        "**Release / Handoff Gate (放行 / 接管闸门)**\n"
        "- 当前判断：验证中\n"
        "- 当前缺口：缺少自动执行证据。\n"
        "- 接手后第一步：从账本接管任务。\n"
        "- 接手入口：先看任务合同、状态台账、验证链。\n"
    )
