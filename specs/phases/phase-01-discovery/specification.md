# Phase 1 — Infrastructure discovery

**Status:** Implemented locally and documented; host behavior is supported by prior records, not re-executed during this task.

## Objective and scope

Restricted SSH-based read-only observation and sanitized Docker inventory. Repository evidence includes `scripts/homelab-inventory`, its tests, installation/security docs, audit report, and local CLI. Inventory uses fixed calls, bounds, timeouts, and selected metadata omissions.

Out of scope: direct Docker access for `agent`, secrets/environment capture, service changes, unrestricted discovery, fresh live claims without observation, and gateway deployment.

## Requirements and security

FR-003, OR-004, SR-005, SR-009, CR-003. Reject arguments; use fixed executable and Docker calls; enforce timeouts and a 100-container cap; do not bypass OS permissions. Treat remote results as scoped, timestamped evidence.

## Dependencies and architecture

Designated SSH account, installed root-owned inventory wrapper, narrowly authorized invocation. Local client dry-runs; `--send` contacts the host.

## Deliverables and acceptance

Inventory wrapper, client, docs, tests. Acceptance: unauthorized arguments fail before Docker; limits/timeouts work; output is sanitized; local tests pass; administrator separately verifies exact remote sudo rule and modes. Repository contains wrapper/client tests; host verification must be cited.

## Verification, migration, rollback

Verify wrapper cases, SSH restrictions, and installed mode as administrator. Rollback requires a separate approved change to inventory authorization; do not infer live rollout from code. No migration is proposed.

## Open questions

Current installation, effective SSH restrictions, and output policy should be reconfirmed when operationally needed.
