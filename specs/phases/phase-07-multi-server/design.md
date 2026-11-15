# Phase 7 design — multi-server operations

**Status:** Planned; fleet threat model and consistency decisions required.

## Architecture review

| Component | Decision | Reason |
|---|---|---|
| Phase 1–6 single-host contract | Reuse as the host-level interface and enforcement model. | Fleet coordination must not weaken host authority. |
| Host identity/policy/audit | Keep authoritative and unique per host; refactor correlation to include host identity. | Prevent cross-host confused deputy and ambiguous reports. |
| Fleet coordinator | Add only for explicit enrollment, read-only aggregation, and bounded coordination. | Do not create a central privilege bypass. |
| Central policy authority or implicit cross-host credentials | Do not assume; decide through threat analysis. | Compromise scope and policy ownership are product-critical. |

## Required design decisions

Specify enrollment/removal, host identity and credential hierarchy, policy
distribution/integrity, stale host behavior, bounded concurrency/deadlines,
cancellation, partial results, audit retention, offline operation, and
per-host rollback. The first vertical slice is read-only inventory across two
isolated hosts; mutation coordination requires a separate design and approval.
