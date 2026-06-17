#!/usr/bin/env bash
set -euo pipefail

PYTHONPATH=src ./.venv/bin/tf-policy-guard tests/fixtures/risky_plan.json --monthly-cost-limit 500
