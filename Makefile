PYTHON ?= python3
VENV ?= .venv
ACTIVATE = . $(VENV)/bin/activate

.PHONY: venv install test run lint sample-eval sample-report sample-gate history-report docker-build

venv:
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE) && pip install --upgrade pip

install: venv
	$(ACTIVATE) && pip install -e .[dev]

test:
	$(ACTIVATE) && PYTHONPATH=src pytest

run:
	$(ACTIVATE) && PYTHONPATH=src uvicorn terraform_cost_policy_guard.main:app --host 0.0.0.0 --port 8080

sample-eval:
	$(ACTIVATE) && PYTHONPATH=src tf-policy-guard tests/fixtures/risky_plan.json --monthly-cost-limit 500

sample-report:
	$(ACTIVATE) && PYTHONPATH=src tf-policy-guard tests/fixtures/risky_plan.json --monthly-cost-limit 500 --report-md reports/risky-policy-review.md

sample-gate:
	$(ACTIVATE) && PYTHONPATH=src tf-policy-guard tests/fixtures/risky_plan.json --monthly-cost-limit 500 --fail-on-block

history-report:
	$(ACTIVATE) && PYTHONPATH=src tf-policy-guard tests/fixtures/plan_history.json --history --report-md reports/plan-history-review.md --fail-on-block; test $$? -eq 2

docker-build:
	docker build -t terraform-cost-policy-guard:local .
