from __future__ import annotations

import argparse
import json
from pathlib import Path

from .policies import evaluate_plan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate Terraform plan JSON against cost and safety policies.")
    parser.add_argument("plan", type=Path, help="Path to terraform show -json output")
    parser.add_argument("--monthly-cost-limit", type=float, default=500.0)
    parser.add_argument("--required-tag", action="append", dest="required_tags", default=None)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text())
    result = evaluate_plan(plan, monthly_cost_limit=args.monthly_cost_limit, required_tags=args.required_tags)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
