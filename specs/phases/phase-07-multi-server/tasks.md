# Phase 7 tasks — multi-server operations

**Status:** Planned; first release is read-only fleet inventory.

| # | Vertical slice | Completion criterion | Status |
|---|---|---|---|
| 1 | Enroll two isolated hosts | Independent host identities, credentials, policy revisions and removal steps recorded. | Todo |
| 2 | Aggregate read-only results | Per-host health/source/time and unavailable state shown without false fleet success. | Todo |
| 3 | Preserve host isolation | Spoof, replay, credential crossover and policy mismatch tests deny. | Todo |
| 4 | Exercise partial failure and coordinator recovery | One host failure/restart does not alter another; results and audit remain attributable. | Todo |
| 5 | Complete fleet release gate | Drift detection, per-host rollback, runtime verification and combined v1.0 scenario pass. | Todo |

Do not include fleet-wide mutations until an independent, reviewed vertical
slice defines authorization, concurrency, cancellation, and recovery.
