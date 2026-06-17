from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PolicyViolation(BaseModel):
    policy_id: str
    severity: str
    message: str
    resource_address: str
    resource_type: str


class EvaluationSummary(BaseModel):
    resource_changes: int
    create_count: int
    update_count: int
    delete_count: int
    estimated_monthly_cost_delta: float
    violation_count: int
    blocked: bool


class EvaluationResult(BaseModel):
    summary: EvaluationSummary
    violations: list[PolicyViolation]
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvaluationRequest(BaseModel):
    plan: dict[str, Any]
    monthly_cost_limit: float = 500.0
    required_tags: list[str] = Field(default_factory=lambda: ["owner", "environment"])
