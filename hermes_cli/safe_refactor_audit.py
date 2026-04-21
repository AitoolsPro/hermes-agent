from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
import fnmatch
import re

import yaml


DEFAULT_POLICY_RELATIVE_PATH = Path("policies/core_rules.yaml")
DEFAULT_LOCAL_OVERRIDE_DIR = Path("~/.hermes/policies").expanduser()
ALLOWED_OVERRIDE_KEYS = {
    "restricted_globs",
    "allowed_direct_related_paths",
    "risk_notes",
}


class PolicyError(ValueError):
    """Raised when policy files are malformed or attempt unsafe overrides."""


@dataclass(frozen=True)
class RuleSpec:
    rule_id: str
    severity: str
    message: str
    file_globs: tuple[str, ...]
    removed_line_patterns: tuple[re.Pattern[str], ...]


@dataclass(frozen=True)
class AuditFinding:
    rule_id: str
    severity: str
    path: str
    line: str
    source: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class AuditReport:
    policy_id: str
    touched_files: tuple[str, ...]
    findings: tuple[AuditFinding, ...]
    risk_notes: tuple[str, ...] = ()
    parse_valid: bool = True

    @property
    def rejected(self) -> bool:
        return (not self.parse_valid) or any(finding.severity == "REJECT_HARD" for finding in self.findings)

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "touched_files": list(self.touched_files),
            "risk_notes": list(self.risk_notes),
            "parse_valid": self.parse_valid,
            "rejected": self.rejected,
            "findings": [finding.to_dict() for finding in self.findings],
        }


@dataclass(frozen=True)
class PolicyBundle:
    policy_id: str
    version: int
    restricted_globs: tuple[str, ...]
    allowed_direct_related_paths: tuple[str, ...]
    hard_reject_rules: tuple[RuleSpec, ...]
    risk_notes: tuple[str, ...] = ()
    sources: tuple[str, ...] = ()

    def is_restricted(self, relative_path: str) -> bool:
        return any(fnmatch.fnmatch(relative_path, glob) for glob in self.restricted_globs)

    def is_allowed_direct_path(self, relative_path: str) -> bool:
        return relative_path in self.allowed_direct_related_paths


@dataclass(frozen=True)
class DiffLine:
    kind: str
    text: str


def _dedupe(items: list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            ordered.append(item)
            seen.add(item)
    return tuple(ordered)


def _read_yaml_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise PolicyError(f"Policy file not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise PolicyError(f"Policy file must contain a mapping: {path}")
    return data


def _compile_rule(raw_rule: dict[str, Any]) -> RuleSpec:
    if not isinstance(raw_rule, dict):
        raise PolicyError("Each hard reject rule must be a mapping")
    try:
        rule_id = str(raw_rule["id"])
        severity = str(raw_rule["severity"])
        message = str(raw_rule["message"])
    except KeyError as exc:
        raise PolicyError(f"Missing required rule field: {exc.args[0]}") from exc

    file_globs = raw_rule.get("file_globs") or []
    removed_line_regex = raw_rule.get("removed_line_regex") or []
    if not isinstance(file_globs, list) or not all(isinstance(item, str) for item in file_globs):
        raise PolicyError(f"Rule {rule_id} file_globs must be a list of strings")
    if not isinstance(removed_line_regex, list) or not all(isinstance(item, str) for item in removed_line_regex):
        raise PolicyError(f"Rule {rule_id} removed_line_regex must be a list of strings")

    return RuleSpec(
        rule_id=rule_id,
        severity=severity,
        message=message,
        file_globs=tuple(file_globs),
        removed_line_patterns=tuple(re.compile(pattern) for pattern in removed_line_regex),
    )


def _validate_scope_consistency(restricted_globs: list[str], allowed_direct_related_paths: list[str]) -> None:
    for allowed_path in allowed_direct_related_paths:
        if any(fnmatch.fnmatch(allowed_path, glob) for glob in restricted_globs):
            raise PolicyError(
                f"Allowed direct-related path conflicts with restricted scope: {allowed_path}"
            )


def _build_policy_bundle(raw_policy: dict[str, Any], sources: list[str], *, risk_notes: list[str] | None = None) -> PolicyBundle:
    restricted_globs = raw_policy.get("restricted_globs") or []
    allowed_direct_related_paths = raw_policy.get("allowed_direct_related_paths") or []
    raw_rules = raw_policy.get("hard_reject_rules") or []
    if not isinstance(restricted_globs, list) or not all(isinstance(item, str) for item in restricted_globs):
        raise PolicyError("restricted_globs must be a list of strings")
    if not isinstance(allowed_direct_related_paths, list) or not all(isinstance(item, str) for item in allowed_direct_related_paths):
        raise PolicyError("allowed_direct_related_paths must be a list of strings")
    if not isinstance(raw_rules, list):
        raise PolicyError("hard_reject_rules must be a list")

    compiled_rules = tuple(_compile_rule(raw_rule) for raw_rule in raw_rules)
    _validate_scope_consistency(list(restricted_globs), list(allowed_direct_related_paths))
    return PolicyBundle(
        policy_id=str(raw_policy.get("policy_id", "unknown")),
        version=int(raw_policy.get("version", 1)),
        restricted_globs=_dedupe(list(restricted_globs)),
        allowed_direct_related_paths=_dedupe(list(allowed_direct_related_paths)),
        hard_reject_rules=compiled_rules,
        risk_notes=_dedupe(list(risk_notes or [])),
        sources=tuple(sources),
    )


def _iter_override_paths(explicit_override: str | Path | None = None, override_dir: str | Path | None = None) -> list[Path]:
    if explicit_override:
        explicit = Path(explicit_override).expanduser()
        if explicit.is_dir():
            return sorted(path for path in explicit.glob("*.yaml") if path.is_file())
        return [explicit]

    base = Path(override_dir).expanduser() if override_dir else DEFAULT_LOCAL_OVERRIDE_DIR
    if not base.exists():
        return []
    return sorted(path for path in base.glob("*.yaml") if path.is_file())


def load_policy_bundle(
    repo_root: str | Path,
    *,
    policy_path: str | Path | None = None,
    explicit_override: str | Path | None = None,
    override_dir: str | Path | None = None,
) -> PolicyBundle:
    repo_root = Path(repo_root)
    core_path = Path(policy_path) if policy_path else repo_root / DEFAULT_POLICY_RELATIVE_PATH
    core_policy = _read_yaml_file(core_path)
    bundle = _build_policy_bundle(core_policy, [str(core_path)])

    restricted = list(bundle.restricted_globs)
    allowed_paths = list(bundle.allowed_direct_related_paths)
    risk_notes = list(bundle.risk_notes)
    sources = [str(core_path)]

    for override_path in _iter_override_paths(explicit_override=explicit_override, override_dir=override_dir):
        raw_override = _read_yaml_file(override_path)
        unknown_keys = set(raw_override) - ALLOWED_OVERRIDE_KEYS
        if unknown_keys:
            raise PolicyError(
                f"Override {override_path} contains forbidden keys: {', '.join(sorted(unknown_keys))}"
            )
        restricted.extend(raw_override.get("restricted_globs") or [])
        override_allowed_paths = raw_override.get("allowed_direct_related_paths") or []
        _validate_scope_consistency(restricted, allowed_paths + list(override_allowed_paths))
        allowed_paths.extend(override_allowed_paths)
        risk_notes.extend(raw_override.get("risk_notes") or [])
        sources.append(str(override_path))

    _validate_scope_consistency(restricted, allowed_paths)

    return PolicyBundle(
        policy_id=bundle.policy_id,
        version=bundle.version,
        restricted_globs=_dedupe(restricted),
        allowed_direct_related_paths=_dedupe(allowed_paths),
        hard_reject_rules=bundle.hard_reject_rules,
        risk_notes=_dedupe(risk_notes),
        sources=tuple(sources),
    )


def _normalize_diff_path(raw_path: str) -> str | None:
    raw_path = raw_path.strip()
    if raw_path == "/dev/null":
        return None
    if raw_path.startswith("a/") or raw_path.startswith("b/"):
        return raw_path[2:]
    return raw_path


def parse_unified_diff(diff_text: str) -> tuple[bool, dict[str, list[DiffLine]]]:
    files: dict[str, list[DiffLine]] = {}
    current_path: str | None = None
    saw_diff_header = False
    saw_file_header = False
    saw_hunk = False
    for raw_line in diff_text.splitlines():
        if raw_line.startswith("diff --git "):
            saw_diff_header = True
            current_path = None
            continue
        if raw_line.startswith("--- "):
            saw_file_header = True
            continue
        if raw_line.startswith("+++ "):
            saw_file_header = True
            current_path = _normalize_diff_path(raw_line[4:])
            if current_path is not None:
                files.setdefault(current_path, [])
            continue
        if raw_line.startswith("@@ "):
            saw_hunk = True
            continue
        if current_path is None:
            continue
        if raw_line.startswith("+") and not raw_line.startswith("+++"):
            files[current_path].append(DiffLine("added", raw_line[1:]))
        elif raw_line.startswith("-") and not raw_line.startswith("---"):
            files[current_path].append(DiffLine("removed", raw_line[1:]))
    parse_valid = bool(diff_text.strip()) and saw_diff_header and saw_file_header and saw_hunk
    return parse_valid, files


def _programmatic_findings(parsed_diff: dict[str, list[DiffLine]]) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    lines = parsed_diff.get("hermes_cli/main.py", [])
    removed_lines = [line.text for line in lines if line.kind == "removed"]
    added_lines = [line.text for line in lines if line.kind == "added"]

    tty_guard_removed = any('_require_tty("uninstall")' in line for line in removed_lines)
    tty_guard_bypass_added = any(
        "isatty()" in line and any(token in line for token in ("FORCE", "CI", "TTY", "or ", "and "))
        for line in added_lines
    )
    if tty_guard_removed:
        findings.append(
            AuditFinding(
                rule_id="programmatic.uninstall_tty_guard_removed",
                severity="REJECT_HARD",
                path="hermes_cli/main.py",
                line='_require_tty("uninstall")',
                source="programmatic",
                message="cmd_uninstall must retain a direct uninstall TTY gate.",
            )
        )
    if tty_guard_bypass_added:
        findings.append(
            AuditFinding(
                rule_id="programmatic.uninstall_tty_guard_bypass",
                severity="REJECT_HARD",
                path="hermes_cli/main.py",
                line=next(line for line in added_lines if "isatty()" in line),
                source="programmatic",
                message="TTY checks may not be bypassed with environment or boolean fallbacks.",
            )
        )
    return findings


def audit_diff(diff_text: str, policy: PolicyBundle) -> AuditReport:
    parse_valid, parsed_diff = parse_unified_diff(diff_text)
    findings: list[AuditFinding] = []
    touched_files = sorted(parsed_diff)

    if not parse_valid:
        findings.append(
            AuditFinding(
                rule_id="policy.diff_parse_invalid",
                severity="REJECT_HARD",
                path="<diff>",
                line="<invalid or empty diff>",
                source="policy",
                message="Diff input must be a valid unified diff; parse failures are rejected.",
            )
        )

    for path, diff_lines in parsed_diff.items():
        if policy.is_restricted(path) and not policy.is_allowed_direct_path(path):
            findings.append(
                AuditFinding(
                    rule_id="policy.file_scope_restricted",
                    severity="REJECT_HARD",
                    path=path,
                    line=path,
                    source="policy",
                    message="Restricted file touched outside the direct-related allowlist.",
                )
            )

        removed_lines = [line.text for line in diff_lines if line.kind == "removed"]
        for rule in policy.hard_reject_rules:
            if not any(fnmatch.fnmatch(path, glob) for glob in rule.file_globs):
                continue
            for removed_line in removed_lines:
                if any(pattern.search(removed_line) for pattern in rule.removed_line_patterns):
                    findings.append(
                        AuditFinding(
                            rule_id=rule.rule_id,
                            severity=rule.severity,
                            path=path,
                            line=removed_line,
                            source="policy",
                            message=rule.message,
                        )
                    )

    findings.extend(_programmatic_findings(parsed_diff))
    return AuditReport(
        policy_id=policy.policy_id,
        touched_files=tuple(touched_files),
        findings=tuple(findings),
        risk_notes=policy.risk_notes,
        parse_valid=parse_valid,
    )
