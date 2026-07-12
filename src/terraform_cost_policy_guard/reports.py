from __future__ import annotations

from collections import Counter

from .models import EvaluationResult, HistoryResult


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
                "| Severity | Policy | Resource | Message | Remediation |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for violation in result.violations:
            lines.append(
                "| "
                f"{violation.severity} | "
                f"{violation.policy_id} | "
                f"{violation.resource_address} | "
                f"{violation.message} | "
                f"{violation.remediation or 'Review with platform owner.'} |"
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


def render_history_report(result: HistoryResult) -> str:
    lines = [
        "# Terraform Policy History Review", "",
        f"Decision: **{result.status.upper()}**", "",
        "## Portfolio Summary", "",
        f"- Reviewed plans: {result.reviewed_windows}",
        f"- Blocked plans: {result.blocked_windows}",
        f"- Combined monthly cost delta: ${result.total_monthly_cost_delta:.2f}",
        f"- Expired exceptions: {len(result.expired_exceptions)}",
        f"- Recurring policies: {', '.join(result.recurring_policy_ids) or 'none'}", "",
        "## Change History", "",
        "| Reviewed | Change | Decision | Violations | Waived | Expired exceptions | Cost delta |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for window in result.windows:
        lines.append(f"| {window.reviewed_on} | {window.change_id} | {window.decision} | {window.violation_count} | {window.waived_violation_count} | {window.expired_exception_count} | ${window.monthly_cost_delta:.2f} |")
    lines.extend(["", "## Exception Governance", ""])
    if result.expired_exceptions:
        for item in result.expired_exceptions:
            lines.append(f"- `{item.policy_id}` owned by {item.owner} expired {item.expires_on}: {item.reason}")
    else:
        lines.append("No expired policy exceptions found.")
    return "\n".join(lines) + "\n"
