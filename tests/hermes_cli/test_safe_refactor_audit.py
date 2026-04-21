from pathlib import Path

import pytest

from hermes_cli.safe_refactor_audit import PolicyError, audit_diff, load_policy_bundle


def test_loads_canonical_policy_bundle_from_repo():
    repo_root = Path(__file__).resolve().parents[2]

    bundle = load_policy_bundle(repo_root)

    assert bundle.policy_id == "hermes.safe_refactor.core"
    assert "hermes_cli/main.py" in bundle.restricted_globs
    assert any(rule.rule_id == "uninstall.tty_guard_removed" for rule in bundle.hard_reject_rules)


def test_override_can_only_add_scope_and_notes(tmp_path):
    repo_root = tmp_path / "repo"
    (repo_root / "policies").mkdir(parents=True)
    (repo_root / "policies" / "core_rules.yaml").write_text(
        """
version: 1
policy_id: test.core
restricted_globs:
  - hermes_cli/main.py
allowed_direct_related_paths:
  - hermes_cli/safe_refactor_audit.py
hard_reject_rules:
  - id: uninstall.tty_guard_removed
    severity: REJECT_HARD
    file_globs:
      - hermes_cli/main.py
    removed_line_regex:
      - '_require_tty\\("uninstall"\\)'
    message: keep tty
""".strip(),
        encoding="utf-8",
    )
    override_dir = tmp_path / "overrides"
    override_dir.mkdir()
    (override_dir / "extra.yaml").write_text(
        """
restricted_globs:
  - hermes_cli/uninstall.py
allowed_direct_related_paths:
  - tests/hermes_cli/test_safe_refactor_audit.py
risk_notes:
  - local review required for uninstall changes
""".strip(),
        encoding="utf-8",
    )

    bundle = load_policy_bundle(repo_root, override_dir=override_dir)

    assert "hermes_cli/main.py" in bundle.restricted_globs
    assert "hermes_cli/uninstall.py" in bundle.restricted_globs
    assert "tests/hermes_cli/test_safe_refactor_audit.py" in bundle.allowed_direct_related_paths
    assert bundle.risk_notes == ("local review required for uninstall changes",)
    assert any(rule.rule_id == "uninstall.tty_guard_removed" for rule in bundle.hard_reject_rules)


def test_override_cannot_relax_hard_rules(tmp_path):
    repo_root = tmp_path / "repo"
    (repo_root / "policies").mkdir(parents=True)
    (repo_root / "policies" / "core_rules.yaml").write_text(
        """
version: 1
policy_id: test.core
restricted_globs: []
allowed_direct_related_paths: []
hard_reject_rules:
  - id: base
    severity: REJECT_HARD
    file_globs: [hermes_cli/main.py]
    removed_line_regex: ['foo']
    message: keep foo
""".strip(),
        encoding="utf-8",
    )
    override_dir = tmp_path / "overrides"
    override_dir.mkdir()
    (override_dir / "relax.yaml").write_text(
        """
hard_reject_rules: []
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(PolicyError, match="forbidden keys"):
        load_policy_bundle(repo_root, override_dir=override_dir)


def test_override_cannot_broaden_allowlist_for_restricted_paths(tmp_path):
    repo_root = tmp_path / "repo"
    (repo_root / "policies").mkdir(parents=True)
    (repo_root / "policies" / "core_rules.yaml").write_text(
        """
version: 1
policy_id: test.core
restricted_globs:
  - hermes_cli/main.py
allowed_direct_related_paths:
  - hermes_cli/safe_refactor_audit.py
hard_reject_rules:
  - id: uninstall.tty_guard_removed
    severity: REJECT_HARD
    file_globs: [hermes_cli/main.py]
    removed_line_regex: ['_require_tty']
    message: keep tty
""".strip(),
        encoding="utf-8",
    )
    override_dir = tmp_path / "overrides"
    override_dir.mkdir()
    (override_dir / "relax_scope.yaml").write_text(
        """
allowed_direct_related_paths:
  - hermes_cli/main.py
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(PolicyError, match="Allowed direct-related path conflicts with restricted scope"):
        load_policy_bundle(repo_root, override_dir=override_dir)


def test_core_policy_rejects_restricted_allowlist_conflict(tmp_path):
    repo_root = tmp_path / "repo"
    (repo_root / "policies").mkdir(parents=True)
    (repo_root / "policies" / "core_rules.yaml").write_text(
        """
version: 1
policy_id: test.core
restricted_globs:
  - hermes_cli/main.py
allowed_direct_related_paths:
  - hermes_cli/main.py
hard_reject_rules:
  - id: uninstall.tty_guard_removed
    severity: REJECT_HARD
    file_globs: [hermes_cli/main.py]
    removed_line_regex: ['_require_tty']
    message: keep tty
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(PolicyError, match="conflicts with restricted scope"):
        load_policy_bundle(repo_root)


def test_override_sequence_cannot_reintroduce_restricted_path_into_allowlist(tmp_path):
    repo_root = tmp_path / "repo"
    (repo_root / "policies").mkdir(parents=True)
    (repo_root / "policies" / "core_rules.yaml").write_text(
        """
version: 1
policy_id: test.core
restricted_globs: []
allowed_direct_related_paths:
  - hermes_cli/safe_refactor_audit.py
hard_reject_rules:
  - id: uninstall.tty_guard_removed
    severity: REJECT_HARD
    file_globs: [hermes_cli/main.py]
    removed_line_regex: ['_require_tty']
    message: keep tty
""".strip(),
        encoding="utf-8",
    )
    override_dir = tmp_path / "overrides"
    override_dir.mkdir()
    (override_dir / "a.yaml").write_text(
        """
restricted_globs:
  - hermes_cli/uninstall.py
""".strip(),
        encoding="utf-8",
    )
    (override_dir / "b.yaml").write_text(
        """
allowed_direct_related_paths:
  - hermes_cli/uninstall.py
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(PolicyError, match="conflicts with restricted scope"):
        load_policy_bundle(repo_root, override_dir=override_dir)


def test_forged_tty_downgrade_diff_is_rejected():
    repo_root = Path(__file__).resolve().parents[2]
    bundle = load_policy_bundle(repo_root)
    diff_text = """
diff --git a/hermes_cli/main.py b/hermes_cli/main.py
index 1111111..2222222 100644
--- a/hermes_cli/main.py
+++ b/hermes_cli/main.py
@@ -3214,7 +3214,7 @@
 def cmd_uninstall(args):
     \"\"\"Uninstall Hermes Agent.\"\"\"
-    _require_tty(\"uninstall\")
+    if not (sys.stdin.isatty() or os.getenv(\"HERMES_FORCE_TTY\")):
     from hermes_cli.uninstall import run_uninstall
     run_uninstall(args)
""".strip()

    report = audit_diff(diff_text, bundle)

    assert report.rejected is True
    rule_ids = {finding.rule_id for finding in report.findings}
    assert "uninstall.tty_guard_removed" in rule_ids
    assert "programmatic.uninstall_tty_guard_removed" in rule_ids
    assert "programmatic.uninstall_tty_guard_bypass" in rule_ids


def test_restricted_file_scope_rejects_main_py_changes_even_when_diff_is_valid():
    repo_root = Path(__file__).resolve().parents[2]
    bundle = load_policy_bundle(repo_root)
    diff_text = """
diff --git a/hermes_cli/main.py b/hermes_cli/main.py
index 1111111..2222222 100644
--- a/hermes_cli/main.py
+++ b/hermes_cli/main.py
@@ -3214,7 +3214,7 @@
 def cmd_uninstall(args):
     \"\"\"Uninstall Hermes Agent.\"\"\"
-    _require_tty(\"uninstall\")
+    _require_tty(\"uninstall\")
     from hermes_cli.uninstall import run_uninstall
     run_uninstall(args)
""".strip()

    report = audit_diff(diff_text, bundle)

    assert report.rejected is True
    assert "policy.file_scope_restricted" in {finding.rule_id for finding in report.findings}


def test_invalid_or_empty_diff_fails_closed():
    repo_root = Path(__file__).resolve().parents[2]
    bundle = load_policy_bundle(repo_root)

    empty_report = audit_diff("", bundle)
    malformed_report = audit_diff(
        "diff --git a/hermes_cli/main.py b/hermes_cli/main.py\n--- a/hermes_cli/main.py\n+++ b/hermes_cli/main.py",
        bundle,
    )

    assert empty_report.rejected is True
    assert empty_report.parse_valid is False
    assert malformed_report.rejected is True
    assert malformed_report.parse_valid is False
    malformed_ids = {finding.rule_id for finding in malformed_report.findings}
    assert "policy.diff_parse_invalid" in malformed_ids
