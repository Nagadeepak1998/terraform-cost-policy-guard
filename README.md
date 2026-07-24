# Terraform Cost Policy Guard

`terraform-cost-policy-guard` is a production-shaped portfolio project for reviewing `terraform show -json` output before an infrastructure change reaches production. It combines a reusable policy engine, a FastAPI review service, a CLI for CI/CD pipelines, Prometheus metrics, container packaging, and deployment manifests.

## What It Demonstrates

- Terraform plan risk analysis for cost, destructive changes, tag hygiene, public ingress, and privileged IAM
- Python service design that works both as an API and as a pipeline CLI
- Markdown policy review reports for pull requests and change tickets
- Multi-plan change history with exception ownership and expiry enforcement
- FinOps budget readiness using current spend, proposed cost, warning thresholds, and team ownership
- Local test automation with `pytest`
- Container packaging plus Kubernetes and Terraform deployment scaffolding
- Basic observability through `/healthz`, `/metrics`, and structured evaluation output

## Architecture

```mermaid
flowchart LR
    A["terraform show -json"] --> B["Policy Engine"]
    B --> C["CLI Gate"]
    B --> D["FastAPI Service"]
    D --> E["Prometheus Metrics"]
    D --> F["Deployment Targets"]
    F --> G["Kubernetes"]
    F --> H["Terraform Module"]
```

## Repository Layout

```text
src/terraform_cost_policy_guard/   API, CLI, policy logic, models
tests/                            unit and API checks with plan fixtures
reports/                          generated sample policy review report
infra/docker/                     docker-compose example
infra/k8s/                        Kubernetes deployment and service
infra/terraform/                  Terraform skeleton for cluster deployment
docs/CASE_STUDY.md                recruiter-facing project narrative
docs/github-actions/ci.yml        CI workflow kept outside .github until workflow scope exists
```

## Policies Implemented

- `monthly-cost-threshold`: blocks plans above the configured monthly delta
- `protected-resource-delete`: blocks deletes for stateful resources such as RDS and S3
- `public-sensitive-port`: blocks public ingress to ports like `22`, `3306`, and `5432`
- `missing-required-tags`: flags resources missing tags such as `owner` and `environment`
- `privileged-iam-policy`: blocks IAM policies that grant `Action: "*"` on `Resource: "*"`

## Quick Start

```bash
cd /Users/nagadeepakappalaneni/Documents/New\ project/showcase-repos/terraform-cost-policy-guard
make install
make test
make sample-eval
make run
```

## CLI Usage

```bash
PYTHONPATH=src tf-policy-guard tests/fixtures/risky_plan.json --monthly-cost-limit 500
```

The CLI prints JSON with:

- evaluation summary
- violation list
- blocking decision

Generate a reviewer-friendly Markdown report:

```bash
make sample-report
```

Sample output is tracked at `reports/risky-policy-review.md`.

Review a dated set of plans and fail when a policy exception has expired:

```bash
make history-report
```

The tracked `reports/plan-history-review.md` shows cost movement, plan decisions, waived violations, recurring policies, and expired exception owners. The same review is available through `POST /history`.

Review whether a proposed infrastructure change fits a team's monthly budget:

```bash
make budget-report
```

The tracked `reports/budget-readiness-review.md` records the team, owner, change ID, projected spend, utilization, remaining budget, and the blocking reason. The same deterministic review is available through `POST /budget/review`.

Fail a pipeline when the plan is blocked:

```bash
PYTHONPATH=src tf-policy-guard tests/fixtures/risky_plan.json --monthly-cost-limit 500 --fail-on-block
```

Blocked plans exit with code `2`.

## API Usage

Start the service:

```bash
make run
```

Evaluate a plan:

```bash
curl -X POST http://127.0.0.1:8080/evaluate \
  -H 'Content-Type: application/json' \
  -d @<(jq -n --slurpfile plan tests/fixtures/risky_plan.json '{plan: $plan[0], monthly_cost_limit: 500}')
```

Review a budget projection:

```bash
curl -X POST http://127.0.0.1:8080/budget/review \
  -H 'Content-Type: application/json' \
  --data @tests/fixtures/budget_review.json
```

Health and metrics:

```bash
curl http://127.0.0.1:8080/healthz
curl http://127.0.0.1:8080/metrics
```

## Docker

```bash
docker build -t terraform-cost-policy-guard:local .
docker run --rm -p 8080:8080 terraform-cost-policy-guard:local
```

An example compose file is included at `infra/docker/docker-compose.yml`.

## Deployment Notes

- `infra/k8s/deployment.yaml` deploys two replicas and exposes Prometheus scrape annotations.
- `infra/terraform/` shows one way to template the Kubernetes deployment from Terraform.
- `docs/github-actions/ci.yml` is ready to move into `.github/workflows/ci.yml` once the GitHub token has workflow scope.

Exact command to enable workflow pushes later:

```bash
gh auth refresh -h github.com -s workflow
```

## Verification

Commands verified locally in this run:

- `. .venv/bin/activate && PYTHONPATH=src pytest` (14 passed)
- `. .venv/bin/activate && PYTHONPATH=src python -m compileall src tests`
- `make sample-report`
- `make history-report` returned the expected exit code `2` for the expired exception
- `make budget-report` returned the expected exit code `2` at 104% projected utilization
- `terraform -chdir=infra/terraform fmt -check -recursive`
- `kubectl apply --dry-run=client --validate=false -f infra/k8s`
- `docker build -t terraform-cost-policy-guard:local .`
- Live container smoke passed for `/healthz`, `/budget/review`, and the budget review Prometheus counter

## Limitations

- Cost estimation is fixture-driven and expects a monthly delta field in the plan JSON.
- Current spend and budget values come from the review manifest; no cloud billing API is called.
- Exceptions are deliberately explicit in the history manifest; this project does not integrate an external approval system.
- Policies are intentionally small and easy to extend rather than tied to a full policy framework.
- Terraform deployment files are a starter skeleton and assume an existing Kubernetes provider configuration.
