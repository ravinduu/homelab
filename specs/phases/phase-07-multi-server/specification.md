# Phase 7 — Multi-server management

**Status:** Planned.

## Objective and scope

Manage multiple independently installed hosts through fleet inventory, distributed policy administration, coordinated operations, and centralized observability while retaining authoritative per-host enforcement. Out of scope: a central service that silently bypasses local policy or assumes every host has identical capabilities.

## Dependencies

Stable identity, policy, transport, adapter, audit, and release contracts from Phases 3–6; tested single-host recovery.

## Requirements and architecture

Each host has unique identity and policy revision; fleet control authenticates and authorizes each target; stale/unreachable hosts fail distinctly; partial success is represented explicitly; coordinated actions have bounded concurrency, deadlines, and cancellation semantics. Policy distribution is authenticated, integrity-checked, staged, and rollbackable.

## Deliverables / acceptance

Fleet inventory model, server enrollment/removal, policy distribution design, operation coordinator, central audit/observability design, partial-failure/recovery playbooks, conformance tests. Acceptance: host isolation holds, one host compromise does not grant fleet authority, policy drift is detected, and partial execution is reported without false global success.

## Verification

Multi-host simulations; identity spoof/replay; policy rollback/tamper; unavailable host; partial execution; coordinator restart; audit correlation; enrollment/revocation; consistency and recovery tests.

## Migration / rollback

Enroll hosts incrementally with per-host compatibility checks. Fleet orchestration can be disabled without removing local gateway enforcement. Roll back staged policy per host and preserve local last-known-good revisions.

## Open questions

Central control-plane location and trust, offline behavior, policy ownership, fleet key hierarchy, data retention, and consistency model.
