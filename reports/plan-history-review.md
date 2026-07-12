# Terraform Policy History Review

Decision: **BLOCK**

## Portfolio Summary

- Reviewed plans: 3
- Blocked plans: 1
- Combined monthly cost delta: $1470.00
- Expired exceptions: 1
- Recurring policies: none

## Change History

| Reviewed | Change | Decision | Violations | Waived | Expired exceptions | Cost delta |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| 2026-07-01 | network-baseline | allow | 0 | 0 | 0 | $120.00 |
| 2026-07-05 | database-scale-up | allow | 1 | 1 | 0 | $650.00 |
| 2026-07-12 | database-scale-up-followup | block | 1 | 0 | 1 | $700.00 |

## Exception Governance

- `monthly-cost-threshold` owned by finops expired 2026-07-10: Approved launch capacity
