# Terraform Policy Review

Decision: **BLOCK**

## Summary

- Resource changes: 2
- Creates: 1
- Updates: 0
- Deletes: 1
- Estimated monthly cost delta: $1420.00
- Violations: 4

## Severity Counts

- critical: 2
- high: 2
- medium: 0
- low: 0

## Violations

| Severity | Policy | Resource | Message |
| --- | --- | --- | --- |
| critical | public-sensitive-port | aws_security_group_rule.db_ingress | Public ingress exposes sensitive port 5432. |
| high | missing-required-tags | aws_security_group_rule.db_ingress | Missing required tags: environment. |
| critical | protected-resource-delete | aws_db_instance.primary | Protected data resource is scheduled for deletion. |
| high | monthly-cost-threshold | plan | Plan increases estimated monthly cost by $1420.00, above the $500.00 limit. |

## Review Notes

- Attach this report to the pull request or change ticket.
- Treat BLOCK as a release gate failure until the listed resources are remediated or approved by the platform owner.
