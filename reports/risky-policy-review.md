# Terraform Policy Review

Decision: **BLOCK**

## Summary

- Resource changes: 3
- Creates: 2
- Updates: 0
- Deletes: 1
- Estimated monthly cost delta: $1420.00
- Violations: 5

## Severity Counts

- critical: 3
- high: 2
- medium: 0
- low: 0

## Violations

| Severity | Policy | Resource | Message | Remediation |
| --- | --- | --- | --- | --- |
| critical | public-sensitive-port | aws_security_group_rule.db_ingress | Public ingress exposes sensitive port 5432. | Restrict ingress to approved CIDR ranges or move access behind a private network path. |
| high | missing-required-tags | aws_security_group_rule.db_ingress | Missing required tags: environment. | Add the required ownership tags before merging the infrastructure change. |
| critical | protected-resource-delete | aws_db_instance.primary | Protected data resource is scheduled for deletion. | Require explicit data-retention approval or replace the delete with a migration plan. |
| critical | privileged-iam-policy | aws_iam_policy.platform_admin | IAM policy grants Allow on Action '*' and Resource '*'. | Scope actions and resources to the minimum service permissions required for the workload. |
| high | monthly-cost-threshold | plan | Plan increases estimated monthly cost by $1420.00, above the $500.00 limit. | Split the rollout, lower provisioned capacity, or obtain an explicit budget approval. |

## Review Notes

- Attach this report to the pull request or change ticket.
- Treat BLOCK as a release gate failure until the listed resources are remediated or approved by the platform owner.
