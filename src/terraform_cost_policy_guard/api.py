from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

from .models import BudgetReviewRequest, BudgetReviewResult, EvaluationRequest, EvaluationResult, HistoryRequest, HistoryResult
from .policies import evaluate_plan, review_budget, review_history

app = FastAPI(title="Terraform Cost Policy Guard", version="0.1.0")

EVALUATIONS = Counter("tf_policy_guard_evaluations_total", "Total Terraform plan evaluations", ["blocked"])
HISTORY_REVIEWS = Counter("tf_policy_guard_history_reviews_total", "Total multi-plan history reviews", ["status"])
BUDGET_REVIEWS = Counter("tf_policy_guard_budget_reviews_total", "Total budget readiness reviews", ["status"])


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    return PlainTextResponse(generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


@app.post("/evaluate", response_model=EvaluationResult)
def evaluate(request: EvaluationRequest) -> EvaluationResult:
    result = evaluate_plan(
        plan=request.plan,
        monthly_cost_limit=request.monthly_cost_limit,
        required_tags=request.required_tags,
    )
    EVALUATIONS.labels(blocked=str(result.summary.blocked).lower()).inc()
    return result


@app.post("/history", response_model=HistoryResult)
def history(request: HistoryRequest) -> HistoryResult:
    result = review_history(request)
    HISTORY_REVIEWS.labels(status=result.status).inc()
    return result


@app.post("/budget/review", response_model=BudgetReviewResult)
def budget_review(request: BudgetReviewRequest) -> BudgetReviewResult:
    result = review_budget(request)
    BUDGET_REVIEWS.labels(status=result.status).inc()
    return result
