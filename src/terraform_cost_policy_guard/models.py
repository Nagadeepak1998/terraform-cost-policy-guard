from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class PolicyViolation(BaseModel):
    policy_id: str
    severity: str
    message: str
    resource_address: str
    resource_type: str
    remediation: str | None = None


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


class PolicyException(BaseModel):
    policy_id: str
    owner: str
    expires_on: date
    reason: str


class HistoryWindow(BaseModel):
    reviewed_on: date
    change_id: str
    plan: dict[str, Any]
    exceptions: list[PolicyException] = Field(default_factory=list)


class HistoryRequest(BaseModel):
    windows: list[HistoryWindow]
    monthly_cost_limit: float = 500.0
    required_tags: list[str] = Field(default_factory=lambda: ["owner", "environment"])


class HistoryWindowResult(BaseModel):
    reviewed_on: date
    change_id: str
    decision: str
    violation_count: int
    waived_violation_count: int
    expired_exception_count: int
    monthly_cost_delta: float


class HistoryResult(BaseModel):
    status: str
    reviewed_windows: int
    blocked_windows: int
    total_monthly_cost_delta: float
    expired_exceptions: list[PolicyException]
    recurring_policy_ids: list[str]
    windows: list[HistoryWindowResult]


class BudgetReviewRequest(BaseModel):
    team: str
    owner: str
    monthly_budget: float = Field(gt=0)
    current_monthly_spend: float = Field(ge=0)
    proposed_monthly_delta: float
    warning_threshold_percent: float = Field(default=80.0, gt=0, le=100)
    change_id: str


class BudgetReviewResult(BaseModel):
    status: str
    team: str
    owner: str
    change_id: str
    monthly_budget: float
    projected_monthly_spend: float
    projected_utilization_percent: float
    remaining_budget: float
    findings: list[str]
