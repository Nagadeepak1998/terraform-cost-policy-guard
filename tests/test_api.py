from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from terraform_cost_policy_guard.api import app


FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_healthcheck() -> None:
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_evaluate_endpoint_returns_summary() -> None:
    client = TestClient(app)
    response = client.post(
        "/evaluate",
        json={"plan": load_fixture("risky_plan.json"), "monthly_cost_limit": 500.0},
    )
    payload = response.json()
    assert response.status_code == 200
    assert payload["summary"]["blocked"] is True
    assert payload["summary"]["violation_count"] == 5
