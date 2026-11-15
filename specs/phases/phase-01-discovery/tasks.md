# Phase 1 tasks — single-server discovery

**Status:** Verification Pending; assess existing implementation before
changing it.

| # | Vertical slice | Completion evidence | Status |
|---|---|---|---|
| 1 | Freeze supported read-only request/result contract | Reviewed schema includes evidence time, source, bounds, unavailable/truncated states, and separates fact, diagnosis, and recommendation. | Todo |
| 2 | Audit current wrapper and client | Reuse/refactor/remove decisions and exact installed invocation recorded. | Todo |
| 3 | Complete security and boundary tests | Fixed command, argument denial, output cap/redaction, timeout, failure, no side effects. | Partial; verify existing suite |
| 4 | Build reproducible install and isolated integration | Artifact installation, ownership/modes, authorization and cleanup verified on disposable Debian. | Todo |
| 5 | Demonstrate operator scenario and rollback | Sanitized health report explains a known state and supported next action, handles unavailable data honestly, and has exact revision/rollback evidence. | Todo |

Do not add diagnosis, remediation, or a second host in this phase.
