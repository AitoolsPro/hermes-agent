from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Callable

from hermes_cli.human_gate_controller import HumanGateDecision, HumanGateController
from hermes_cli.review_orchestrator import run_self_correcting_review


_TRACKER_SECTION_RE = re.compile(r"(?ms)^###\s+([^\n]+)\n(.*?)(?=^###\s+|\Z)")
_STATUS_LINE_RE = re.compile(r"^- \*\*状态\*\*：(.*)$", re.M)
_MARKDOWN_PATH_RE = re.compile(r"`((?:docs|\.\.?/docs)/[^`]+\.md)`")


@dataclass(frozen=True)
class TrackerBattle:
    battle_name: str
    heading_suffix: str
    status_text: str
    body: str


@dataclass(frozen=True)
class BattleDocumentPaths:
    tracker_path: Path
    task_contract_path: Path
    status_ledger_path: Path
    verification_chain_path: Path
    battle_name: str


@dataclass(frozen=True)
class SafeRefactorRuntimeResult:
    battle_name: str
    review_result: Any
    human_gate_decision: HumanGateDecision | None
    entered_m6: bool
    attempts_used: int
    stopped_in_m5: bool


def select_active_battle(tracker_text: str) -> str:
    return select_active_battle_entry(tracker_text).battle_name


def select_active_battle_entry(tracker_text: str) -> TrackerBattle:
    waiting_battle: TrackerBattle | None = None

    for header, body in _TRACKER_SECTION_RE.findall(tracker_text):
        battle_name, heading_suffix = _split_battle_header(header)
        status_match = _STATUS_LINE_RE.search(body)
        if not status_match:
            continue
        status_text = status_match.group(1).strip()
        battle = TrackerBattle(
            battle_name=battle_name,
            heading_suffix=heading_suffix,
            status_text=status_text,
            body=body,
        )
        if "最高优先级活跃战役" in status_text:
            return battle
        if waiting_battle is None and "等待自动化接管" in status_text:
            waiting_battle = battle

    if waiting_battle is not None:
        return waiting_battle
    raise ValueError("未在账本中找到可接管战役")


def discover_battle_document_paths(
    tracker_path: str | Path,
    *,
    battle_entry: TrackerBattle | None = None,
    battle_name: str | None = None,
) -> BattleDocumentPaths:
    tracker = Path(tracker_path)
    tracker_text = tracker.read_text(encoding="utf-8")
    entry = battle_entry or _resolve_tracker_battle_entry(tracker_text, battle_name)

    task_contract_path = _resolve_task_contract_path(tracker=tracker, battle_entry=entry)
    if not task_contract_path.exists():
        raise FileNotFoundError(f"账本指定的任务合同不存在：{task_contract_path}")

    task_contract_text = task_contract_path.read_text(encoding="utf-8")
    status_ledger_path = _resolve_document_path_from_contract(
        tracker=tracker,
        task_contract_text=task_contract_text,
        suffix="status-ledger.md",
        label="状态台账",
    )
    verification_chain_path = _resolve_document_path_from_contract(
        tracker=tracker,
        task_contract_text=task_contract_text,
        suffix="verification-chain.md",
        label="验证链",
    )

    return BattleDocumentPaths(
        tracker_path=tracker,
        task_contract_path=task_contract_path,
        status_ledger_path=status_ledger_path,
        verification_chain_path=verification_chain_path,
        battle_name=entry.battle_name,
    )


def restore_or_create_battle_documents(paths: BattleDocumentPaths) -> dict[str, str]:
    if not paths.task_contract_path.exists():
        raise FileNotFoundError(f"缺少任务合同，不能自动补造：{paths.task_contract_path}")
    task_contract = paths.task_contract_path.read_text(encoding="utf-8")
    status_ledger = _read_or_create(
        paths.status_ledger_path,
        _default_status_ledger(paths.battle_name, task_contract),
    )
    verification_chain = _read_or_create(
        paths.verification_chain_path,
        _default_verification_chain(paths.battle_name),
    )
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
    attempts_used = len(getattr(review_result, "attempts", ())) or 1
    stopped_after_max_attempts = bool(getattr(review_result, "stopped_after_max_attempts", False))
    entered_m6 = final_review.verdict == "APPROVE_CANDIDATE"

    human_gate_decision: HumanGateDecision | None = None
    if entered_m6:
        if human_gate is not None and not allow_test_gate_override:
            raise ValueError("注入式 human_gate 仅允许用于测试；如确需覆盖，请显式传入 allow_test_gate_override=True")
        if human_gate is None:
            controller = HumanGateController()
            human_gate = controller.require_explicit_approval
        human_gate_decision = human_gate(final_review)

    _write_status_ledger(
        paths.status_ledger_path,
        battle_name=paths.battle_name,
        objective_line=_extract_objective_line(docs["task_contract"]),
        review_verdict=final_review.verdict,
        entered_m6=entered_m6,
        attempts_used=attempts_used,
        stopped_after_max_attempts=stopped_after_max_attempts,
    )
    _write_verification_chain(
        paths.verification_chain_path,
        battle_name=paths.battle_name,
        review_verdict=final_review.verdict,
        entered_m6=entered_m6,
        attempts_used=attempts_used,
        stopped_after_max_attempts=stopped_after_max_attempts,
    )

    return SafeRefactorRuntimeResult(
        battle_name=paths.battle_name,
        review_result=final_review,
        human_gate_decision=human_gate_decision,
        entered_m6=entered_m6,
        attempts_used=attempts_used,
        stopped_in_m5=not entered_m6,
    )


def launch_safe_refactor_from_tracker(
    *,
    tracker_path: str | Path,
    diff_text: str,
    pipeline_runner: Callable[..., Any] = run_safe_refactor_pipeline,
    path_resolver: Callable[..., BattleDocumentPaths] = discover_battle_document_paths,
    **pipeline_kwargs: Any,
) -> Any:
    tracker = Path(tracker_path)
    battle_entry = select_active_battle_entry(tracker.read_text(encoding="utf-8"))
    battle_paths = path_resolver(tracker, battle_entry=battle_entry)
    return pipeline_runner(battle_paths, diff_text=diff_text, **pipeline_kwargs)


def _resolve_tracker_battle_entry(tracker_text: str, battle_name: str | None) -> TrackerBattle:
    if battle_name is None:
        return select_active_battle_entry(tracker_text)
    for header, body in _TRACKER_SECTION_RE.findall(tracker_text):
        current_name, heading_suffix = _split_battle_header(header)
        if current_name == battle_name:
            status_match = _STATUS_LINE_RE.search(body)
            status_text = status_match.group(1).strip() if status_match else ""
            return TrackerBattle(
                battle_name=current_name,
                heading_suffix=heading_suffix,
                status_text=status_text,
                body=body,
            )
    raise ValueError(f"账本中不存在战役：{battle_name}")


def _split_battle_header(header: str) -> tuple[str, str]:
    if "：" in header:
        battle_name, heading_suffix = header.split("：", 1)
        return battle_name.strip(), heading_suffix.strip()
    return header.strip(), ""


def _resolve_task_contract_path(*, tracker: Path, battle_entry: TrackerBattle) -> Path:
    explicit_paths = [
        _repo_relative_path(tracker, raw_path)
        for raw_path in _MARKDOWN_PATH_RE.findall(battle_entry.body)
        if raw_path.endswith("task-contract.md")
    ]
    if len(explicit_paths) == 1:
        return explicit_paths[0]
    if len(explicit_paths) > 1:
        raise ValueError(f"账本为 {battle_entry.battle_name} 指向了多个任务合同，无法自动接管")
    raise ValueError(f"账本缺少 {battle_entry.battle_name} 的显式任务合同路径，不能自动接管")


def _resolve_document_path_from_contract(
    *,
    tracker: Path,
    task_contract_text: str,
    suffix: str,
    label: str,
) -> Path:
    explicit_paths = [
        _repo_relative_path(tracker, raw_path)
        for raw_path in _MARKDOWN_PATH_RE.findall(task_contract_text)
        if raw_path.endswith(suffix)
    ]
    unique_paths = _dedupe_paths(explicit_paths)
    if len(unique_paths) == 1:
        return unique_paths[0]
    if len(unique_paths) > 1:
        raise ValueError(f"任务合同为 {label} 提供了多个候选路径，无法自动接管")
    raise ValueError(f"任务合同缺少 {label} 路径，不能自动建立或恢复现场")


def _repo_relative_path(tracker: Path, markdown_path: str) -> Path:
    normalized = markdown_path[2:] if markdown_path.startswith("./") else markdown_path
    repo_root = tracker.parents[2]
    return repo_root / normalized


def _dedupe_paths(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    unique_paths: list[Path] = []
    for path in paths:
        resolved = path.resolve(strict=False)
        if resolved in seen:
            continue
        seen.add(resolved)
        unique_paths.append(path)
    return unique_paths


def _read_or_create(path: Path, default_text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(default_text, encoding="utf-8")
        return default_text
    return path.read_text(encoding="utf-8")


def _extract_objective_line(task_contract_text: str) -> str:
    in_objective_block = False
    for line in task_contract_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("**Objective"):
            in_objective_block = True
            continue
        if in_objective_block and stripped.startswith("**"):
            break
        if in_objective_block and stripped:
            return stripped
    return "完成 safe-refactor-loop 一键启动总控链接线。"


def _write_status_ledger(
    path: Path,
    *,
    battle_name: str,
    objective_line: str,
    review_verdict: str,
    entered_m6: bool,
    attempts_used: int,
    stopped_after_max_attempts: bool,
) -> None:
    if entered_m6:
        current_stop = "M6 已停机等待北冥输入 Y / Confirm"
        done_items = f"已从账本接管 {battle_name}，并真实跑通 M3 -> M5 -> M6；当前裁决为 {review_verdict}。"
        blocked_items = "未收到北冥显式签字前，任何代码都不准合并。"
        current_judgment = "验证中"
        evidence_gap = "缺少北冥显式 `Y / Confirm` 批准信号。"
    else:
        retry_text = f"M5-v2 已运行 {attempts_used} 次自愈复审。"
        if stopped_after_max_attempts:
            current_stop = "M5-v2 自愈循环达到 3 次上限后停机"
        else:
            current_stop = "M5-v2 已停机，未达 APPROVE_CANDIDATE"
        done_items = f"已从账本接管 {battle_name}，并完成 M3 -> M5 自动复审；{retry_text} 最终裁决为 {review_verdict}。"
        blocked_items = "未达到 APPROVE_CANDIDATE，禁止进入 M6。"
        current_judgment = "未完成"
        evidence_gap = "当前仍停在 M5-v2 自愈循环或失败态，不能进入 M6。"

    text = (
        "**Task Contract Snapshot (合同快照)**\n"
        f"- 目标：{objective_line}\n"
        "- 范围边界：只处理从账本接管战役并串起 M3 -> M5 -> M6 的一键启动总控链；不吸入归档同步器，不改 M3 规则，不削弱 M6 物理停机。\n"
        "- 完成标准：能从账本选择可接管战役并恢复战时文档；只有 `APPROVE_CANDIDATE` 才进入 M6；未达条件时停在 M5-v2 自愈循环或失败态。\n\n"
        "**Current State (当前状态)**\n"
        f"- 当前停点：{current_stop}\n"
        f"- 已完成：{done_items}\n"
        f"- 未完成 / 当前阻塞：{blocked_items}\n"
        f"- 当前判断：{current_judgment}\n\n"
        "**Evidence Logged (证据登记)**\n"
        f"- 已有证据：review_verdict={review_verdict}；entered_m6={'yes' if entered_m6 else 'no'}；m5_attempts={attempts_used}。\n"
        "- 证据对应结论：战役已从账本接管，且战时文档已按真实裁决回写。\n"
        f"- 证据缺口：{evidence_gap}\n\n"
        "**Next Handoff (下一步 / 接管指令)**\n"
        "- 接手后第一步：若已进入 M6，则等待北冥输入 `Y / Confirm`；若未进入 M6，则按 M5-v2 裁决继续修复后重跑。\n"
        "- 立即核查：确认任何 `REJECT_HARD / FAKE_WIN / WARN` 都没有误入 M6。\n"
        "- 若受阻先排查：先查账本中的任务合同路径、任务合同里的状态台账/验证链路径，以及 M5-v2 最终裁决。\n"
    )
    path.write_text(text, encoding="utf-8")


def _write_verification_chain(
    path: Path,
    *,
    battle_name: str,
    review_verdict: str,
    entered_m6: bool,
    attempts_used: int,
    stopped_after_max_attempts: bool,
) -> None:
    target1 = "通过"
    target2 = "通过" if entered_m6 else "不通过"
    target3 = "通过" if entered_m6 else "不通过"
    gate = "验证中" if entered_m6 else "不通过"
    if entered_m6:
        gap = "当前等待北冥显式 `Y / Confirm`，M6 之前仍不得自动放行。"
        result2_reason = "战役已从账本自动接管，并成功恢复 Task Contract / Status Ledger / Verification Chain。"
        result3_reason = "M5-v2 给出 `APPROVE_CANDIDATE` 后才进入 M6，且 M6 已物理停机等待审批。"
    else:
        gap = "未达 `APPROVE_CANDIDATE`，当前必须停在 M5-v2 自愈循环或失败态。"
        result2_reason = "战役已从账本自动接管，并成功恢复或建立战时文档。"
        if stopped_after_max_attempts:
            result3_reason = f"M5-v2 在 {attempts_used} 次自愈后仍未得到 `APPROVE_CANDIDATE`，因此被阻断在 M5。"
        else:
            result3_reason = f"最终裁决为 {review_verdict}，不满足 `APPROVE_CANDIDATE -> M6` 的唯一入口条件。"

    text = (
        "## Verification Chain（默认验证链）\n\n"
        "**Verification Target (验证目标)**\n"
        f"- 对应合同项：对应 {battle_name} 一键启动总控链的交付物、证据与完成标准。\n"
        "- 目标 1：证明入口函数能从 `tech-debt-tracker.md` 选择当前可接管战役。\n"
        "- 目标 2：证明系统能自动恢复或建立 Task Contract / Status Ledger / Verification Chain。\n"
        "- 目标 3：证明只有 `APPROVE_CANDIDATE` 才进入 M6；否则必须停在 M5-v2 自愈循环或失败态。\n\n"
        "**Verification Actions (验证动作)**\n"
        "- 动作 1：读取 `docs/exec-plans/tech-debt-tracker.md`，选择当前活跃战役；若没有活跃战役，则回退到第一个标记为“等待自动化接管”的战役。\n"
        "- 动作 2：根据账本中的任务合同路径和任务合同中的战时文档路径，恢复或建立当前战场文档。\n"
        "- 动作 3：运行 `run_self_correcting_review()`，并仅在最终裁决为 `APPROVE_CANDIDATE` 时调用 M6 人工闸门。\n\n"
        "**Verification Result (验证结果)**\n"
        f"- 目标 1：{target1} —— 当前入口已按账本状态选择战役，而不是手工写死 battle name。\n"
        f"- 目标 2：{target2} —— {result2_reason}\n"
        f"- 目标 3：{target3} —— {result3_reason}\n\n"
        "**Release / Handoff Gate (放行 / 接管闸门)**\n"
        f"- 当前判断：{gate}\n"
        f"- 当前缺口：{gap}\n"
        "- 接手后第一步：若要继续验证，先复跑一键启动入口并核对写回后的状态台账与验证链。\n"
        "- 接手入口：先看任务合同、状态台账、验证链与 `docs/exec-plans/tech-debt-tracker.md`。\n"
    )
    path.write_text(text, encoding="utf-8")


def _default_status_ledger(battle_name: str, task_contract_text: str) -> str:
    return (
        "**Task Contract Snapshot (合同快照)**\n"
        f"- 目标：{_extract_objective_line(task_contract_text)}\n"
        "- 范围边界：只处理从账本接管战役并串起 M3 -> M5 -> M6 的一键启动总控链；不吸入归档同步器。\n"
        "- 完成标准：能从账本恢复战役文档；只有 `APPROVE_CANDIDATE` 才进入 M6；否则停在 M5-v2。\n\n"
        "**Current State (当前状态)**\n"
        "- 当前停点：待自动接管。\n"
        f"- 已完成：已确认 {battle_name} 的任务合同存在。\n"
        "- 未完成 / 当前阻塞：尚未运行一键启动总控链。\n"
        "- 当前判断：未完成\n\n"
        "**Evidence Logged (证据登记)**\n"
        f"- 已有证据：已恢复 {battle_name} 任务合同。\n"
        "- 证据对应结论：可以进入 safe-refactor-loop 一键启动总控链。\n"
        "- 证据缺口：缺少 M3 / M5 / M6 串联后的写回证据。\n\n"
        "**Next Handoff (下一步 / 接管指令)**\n"
        "- 接手后第一步：运行一键启动总控链。\n"
        "- 立即核查：确认账本中的任务合同路径与合同中的战时文档路径一致。\n"
        "- 若受阻先排查：先查任务合同实体是否存在。\n"
    )


def _default_verification_chain(battle_name: str) -> str:
    return (
        "## Verification Chain（默认验证链）\n\n"
        "**Verification Target (验证目标)**\n"
        f"- 对应合同项：对应 {battle_name} 一键启动总控链的交付物 / 证据与完成标准。\n"
        "- 目标 1：证明入口能从账本选择当前可接管战役。\n"
        "- 目标 2：证明系统能自动恢复或建立战时文档。\n"
        "- 目标 3：证明只有 `APPROVE_CANDIDATE` 才进入 M6。\n\n"
        "**Verification Actions (验证动作)**\n"
        "- 动作 1：运行一键启动入口。\n"
        "- 动作 2：检查状态台账与验证链写回内容。\n"
        "- 动作 3：核对未达 `APPROVE_CANDIDATE` 时没有进入 M6。\n\n"
        "**Verification Result (验证结果)**\n"
        "- 目标 1：未执行 —— 等待流水线结果。\n"
        "- 目标 2：未执行 —— 等待流水线结果。\n"
        "- 目标 3：未执行 —— 等待流水线结果。\n\n"
        "**Release / Handoff Gate (放行 / 接管闸门)**\n"
        "- 当前判断：验证中\n"
        "- 当前缺口：缺少一键启动链真实运行证据。\n"
        "- 接手后第一步：从账本接管当前战役。\n"
        "- 接手入口：先看任务合同、状态台账、验证链。\n"
    )
