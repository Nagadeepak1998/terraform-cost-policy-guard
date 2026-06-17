from __future__ import annotations

import json
from pathlib import Path

from terraform_cost_policy_guard.policies import evaluate_plan


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
        "public-sensitive-port",
    }
