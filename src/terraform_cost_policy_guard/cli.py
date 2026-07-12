from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import HistoryRequest
from .policies import evaluate_plan, review_history
from .reports import render_history_report, render_markdown_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate Terraform plan JSON against cost and safety policies.")
    parser.add_argument("plan", type=Path, help="Path to terraform show -json output or history manifest")
    parser.add_argument("--monthly-cost-limit", type=float, default=500.0)
    parser.add_argument("--required-tag", action="append", dest="required_tags", default=None)
    parser.add_argument("--report-md", type=Path, help="Optional path for a Markdown review report")
    parser.add_argument("--fail-on-block", action="store_true", help="Exit with code 2 when policies block the plan")
    parser.add_argument("--history", action="store_true", help="Review a dated multi-plan history manifest")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text())
    if args.history:
        request = HistoryRequest.model_validate({**plan, "monthly_cost_limit": args.monthly_cost_limit, "required_tags": args.required_tags or ["owner", "environment"]})
        result = review_history(request)
        if args.report_md:
            args.report_md.parent.mkdir(parents=True, exist_ok=True)
            args.report_md.write_text(render_history_report(result))
        print(result.model_dump_json(indent=2))
        return 2 if args.fail_on_block and result.status == "block" else 0
    result = evaluate_plan(plan, monthly_cost_limit=args.monthly_cost_limit, required_tags=args.required_tags)
    if args.report_md:
        args.report_md.parent.mkdir(parents=True, exist_ok=True)
        args.report_md.write_text(render_markdown_report(result))
    print(result.model_dump_json(indent=2))
    if args.fail_on_block and result.summary.blocked:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
