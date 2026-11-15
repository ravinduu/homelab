# Phase 2 tasks — approval-gated remediation

**Status:** Verification Pending; verify the existing path before extending it.

| # | Vertical slice | Completion evidence | Status |
|---|---|---|---|
| 1 | Review exact installed gateway/approval contract | Trusted inputs, approval binding, fixed argv and installed consumers documented. | Todo |
| 2 | Prove server-side allow and denial | Denial occurs before inventory/Docker side effects; policy is protected. | Partial; local coverage exists |
| 3 | Prove approval lifecycle | Exact binding, expiry, replay, race, tamper, and rejection tests pass. | Partial; verify criteria against current contract |
| 4 | Prove operation result verification and audit | Health check follows action; request, approval, decision, execution and outcome correlate. | Todo |
| 5 | Exercise install and rollback | Immutable candidate, isolated install, permissions, failure cleanup, denial on disable, restoration. | Todo |

Do not generalize policy or add adapters in this phase; those are Phase 3 and
Phase 5 deliverables.
