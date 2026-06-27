from __future__ import annotations

import json
from typing import Any

from .models import EvaluationResult, EvaluationSummary, PolicyViolation

PROTECTED_RESOURCE_TYPES = {"aws_db_instance", "aws_s3_bucket"}
SENSITIVE_PORTS = {22, 3389, 5432, 3306}
IAM_POLICY_TYPES = {"aws_iam_policy", "aws_iam_role_policy"}


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
                    remediation="Require explicit data-retention approval or replace the delete with a migration plan.",
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
                        remediation="Restrict ingress to approved CIDR ranges or move access behind a private network path.",
                    )
                )

        if resource_type in IAM_POLICY_TYPES and _has_full_admin_statement(after.get("policy")):
            violations.append(
                PolicyViolation(
                    policy_id="privileged-iam-policy",
                    severity="critical",
                    message="IAM policy grants Allow on Action '*' and Resource '*'.",
                    resource_address=address,
                    resource_type=resource_type,
                    remediation="Scope actions and resources to the minimum service permissions required for the workload.",
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
                        remediation="Add the required ownership tags before merging the infrastructure change.",
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
                remediation="Split the rollout, lower provisioned capacity, or obtain an explicit budget approval.",
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


def _has_full_admin_statement(policy: Any) -> bool:
    if not policy:
        return False
    if isinstance(policy, str):
        try:
            policy = json.loads(policy)
        except json.JSONDecodeError:
            return False

    statements = policy.get("Statement", []) if isinstance(policy, dict) else []
    if isinstance(statements, dict):
        statements = [statements]

    for statement in statements:
        if not isinstance(statement, dict) or statement.get("Effect") != "Allow":
            continue
        if _contains_wildcard(statement.get("Action")) and _contains_wildcard(statement.get("Resource")):
            return True
    return False


def _contains_wildcard(value: Any) -> bool:
    if value == "*":
        return True
    if isinstance(value, list):
        return "*" in value
    return False
