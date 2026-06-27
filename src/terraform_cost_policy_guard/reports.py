from __future__ import annotations

from collections import Counter

from .models import EvaluationResult


def render_markdown_report(result: EvaluationResult) -> str:
    severity_counts = Counter(violation.severity for violation in result.violations)
    decision = "BLOCK" if result.summary.blocked else "ALLOW"
    lines = [
        "# Terraform Policy Review",
        "",
        f"Decision: **{decision}**",
        "",
        "## Summary",
        "",
        f"- Resource changes: {result.summary.resource_changes}",
        f"- Creates: {result.summary.create_count}",
        f"- Updates: {result.summary.update_count}",
        f"- Deletes: {result.summary.delete_count}",
        f"- Estimated monthly cost delta: ${result.summary.estimated_monthly_cost_delta:.2f}",
        f"- Violations: {result.summary.violation_count}",
        "",
        "## Severity Counts",
        "",
    ]

    for severity in ("critical", "high", "medium", "low"):
        lines.append(f"- {severity}: {severity_counts.get(severity, 0)}")

    lines.extend(["", "## Violations", ""])
    if result.violations:
        lines.extend(
            [
                "| Severity | Policy | Resource | Message |",
                "| --- | --- | --- | --- |",
            ]
        )
        for violation in result.violations:
            lines.append(
                "| "
                f"{violation.severity} | "
                f"{violation.policy_id} | "
                f"{violation.resource_address} | "
                f"{violation.message} |"
            )
    else:
        lines.append("No policy violations found.")

    lines.extend(
        [
            "",
            "## Review Notes",
            "",
            "- Attach this report to the pull request or change ticket.",
            "- Treat BLOCK as a release gate failure until the listed resources are remediated or approved by the platform owner.",
        ]
    )
    return "\n".join(lines) + "\n"
