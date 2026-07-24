from __future__ import annotations

import json
from pathlib import Path

from terraform_cost_policy_guard.models import BudgetReviewRequest, HistoryRequest
from terraform_cost_policy_guard.policies import evaluate_plan, review_budget, review_history
from terraform_cost_policy_guard.reports import render_budget_report, render_history_report, render_markdown_report


FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_safe_plan_passes_without_blocking() -> None:
    result = evaluate_plan(load_fixture("safe_plan.json"))
    assert result.summary.blocked is False
    assert result.summary.violation_count == 0


def test_risky_plan_surfaces_multiple_policy_violations() -> None:
    result = evaluate_plan(load_fixture("risky_plan.json"), monthly_cost_limit=500.0)
    policy_ids = {violation.policy_id for violation in result.violations}
    assert result.summary.blocked is True
    assert policy_ids == {
        "monthly-cost-threshold",
        "missing-required-tags",
        "protected-resource-delete",
        "privileged-iam-policy",
        "public-sensitive-port",
    }


def test_markdown_report_summarizes_blocking_decision() -> None:
    result = evaluate_plan(load_fixture("risky_plan.json"), monthly_cost_limit=500.0)
    report = render_markdown_report(result)

    assert "Decision: **BLOCK**" in report
    assert "- critical: 3" in report
    assert "- high: 2" in report
    assert "Remediation" in report
    assert "privileged-iam-policy" in report
    assert "| critical | protected-resource-delete | aws_db_instance.primary |" in report


def test_history_review_honors_active_exception_and_blocks_expired_one() -> None:
    result = review_history(HistoryRequest.model_validate(load_fixture("plan_history.json")))
    assert result.status == "block"
    assert result.blocked_windows == 1
    assert result.windows[1].decision == "allow"
    assert result.windows[1].waived_violation_count == 1
    assert result.windows[2].expired_exception_count == 1
    assert result.recurring_policy_ids == []
    report = render_history_report(result)
    assert "Decision: **BLOCK**" in report
    assert "expired 2026-07-10" in report


def test_budget_review_blocks_projected_overspend() -> None:
    result = review_budget(BudgetReviewRequest.model_validate(load_fixture("budget_review.json")))
    assert result.status == "block"
    assert result.projected_monthly_spend == 10400
    assert result.projected_utilization_percent == 104
    assert result.remaining_budget == -400
    assert "exceeds the monthly budget by $400.00" in result.findings[0]
    assert "Decision: **BLOCK**" in render_budget_report(result)


def test_budget_review_warns_before_budget_is_exhausted() -> None:
    request = BudgetReviewRequest(
        team="ml-platform",
        owner="platform-finops",
        monthly_budget=10000,
        current_monthly_spend=7600,
        proposed_monthly_delta=600,
        change_id="gpu-batch-workers",
    )
    result = review_budget(request)
    assert result.status == "warn"
    assert result.projected_utilization_percent == 82
