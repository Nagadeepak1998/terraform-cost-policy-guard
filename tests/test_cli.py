from __future__ import annotations

from pathlib import Path

from terraform_cost_policy_guard.cli import main


FIXTURES = Path(__file__).parent / "fixtures"


def test_cli_can_write_markdown_report(tmp_path: Path, monkeypatch) -> None:
    report_path = tmp_path / "review.md"
    monkeypatch.setattr(
        "sys.argv",
        [
            "tf-policy-guard",
            str(FIXTURES / "risky_plan.json"),
            "--monthly-cost-limit",
            "500",
            "--report-md",
            str(report_path),
        ],
    )

    assert main() == 0
    assert "Decision: **BLOCK**" in report_path.read_text()


def test_cli_can_fail_pipeline_when_plan_is_blocked(monkeypatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "tf-policy-guard",
            str(FIXTURES / "risky_plan.json"),
            "--monthly-cost-limit",
            "500",
            "--fail-on-block",
        ],
    )

    assert main() == 2
