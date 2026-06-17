from __future__ import annotations

from typing import Any

from .models import EvaluationResult, EvaluationSummary, PolicyViolation

PROTECTED_RESOURCE_TYPES = {"aws_db_instance", "aws_s3_bucket"}
SENSITIVE_PORTS = {22, 3389, 5432, 3306}


def evaluate_plan(
    plan: dict[str, Any],
    monthly_cost_limit: float = 500.0,
    required_tags: list[str] | None = None,
) -> EvaluationResult:
    required_tags = required_tags or ["owner", "environment"]
    changes = plan.get("resource_changes", [])
    cost_delta = float(plan.get("planned_values", {}).get("root_module", {}).get("cost_estimate_monthly_delta", 0.0))

    violations: list[PolicyViolation] = []
    create_count = update_count = delete_count = 0

    for change in changes:
        address = change.get("address", "unknown")
        resource_type = change.get("type", "unknown")
        actions = change.get("change", {}).get("actions", [])
        after = change.get("change", {}).get("after") or {}

        if "create" in actions:
            create_count += 1
        if "update" in actions:
            update_count += 1
        if "delete" in actions:
            delete_count += 1

        if "delete" in actions and resource_type in PROTECTED_RESOURCE_TYPES:
            violations.append(
                PolicyViolation(
                    policy_id="protected-resource-delete",
                    severity="critical",
                    message="Protected data resource is scheduled for deletion.",
                    resource_address=address,
                    resource_type=resource_type,
                )
            )

        if resource_type == "aws_security_group_rule":
            cidr_blocks = set(after.get("cidr_blocks") or [])
            port = after.get("from_port")
            if "0.0.0.0/0" in cidr_blocks and port in SENSITIVE_PORTS:
                violations.append(
                    PolicyViolation(
                        policy_id="public-sensitive-port",
                        severity="critical",
                        message=f"Public ingress exposes sensitive port {port}.",
                        resource_address=address,
                        resource_type=resource_type,
                    )
                )

        tags = after.get("tags")
        if tags is not None:
            missing_tags = [tag for tag in required_tags if not tags.get(tag)]
            if missing_tags:
                violations.append(
                    PolicyViolation(
                        policy_id="missing-required-tags",
                        severity="high",
                        message=f"Missing required tags: {', '.join(missing_tags)}.",
                        resource_address=address,
                        resource_type=resource_type,
                    )
                )

    if cost_delta > monthly_cost_limit:
        violations.append(
            PolicyViolation(
                policy_id="monthly-cost-threshold",
                severity="high",
                message=f"Plan increases estimated monthly cost by ${cost_delta:.2f}, above the ${monthly_cost_limit:.2f} limit.",
                resource_address="plan",
                resource_type="terraform_plan",
            )
        )

    blocked = any(violation.severity in {"critical", "high"} for violation in violations)
    summary = EvaluationSummary(
        resource_changes=len(changes),
        create_count=create_count,
        update_count=update_count,
        delete_count=delete_count,
        estimated_monthly_cost_delta=cost_delta,
        violation_count=len(violations),
        blocked=blocked,
    )
    return EvaluationResult(
        summary=summary,
        violations=violations,
        metadata={"required_tags": required_tags, "monthly_cost_limit": monthly_cost_limit},
    )
