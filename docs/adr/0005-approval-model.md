# ADR-0005: Sensitive actions require separate, single-use approval

- **Status:** Accepted for current Jellyfin restart; generalized form proposed
- **Date:** 2026-11-14

## Context

SSH authentication and policy permission do not represent a human decision
for a sensitive operation.

## Decision

For the current restart, an administrator creates a short-lived protected
record bound to operation, service, requester label, expiry, and nonce. The
gateway validates and consumes it atomically before execution. Future approval
records must bind a canonical request and verified principal.

## Alternatives

Let requester self-approve, use a reusable boolean approval, or treat SSH
authentication as consent. Rejected because they enable replay or conflate
distinct controls.

## Consequences

Approval lifecycle, expiry, races, clock, and retention require tests and
operator procedures. Current `agent` binding is not per-agent identity.

## Reconsider when

Only if a new approval system provides equal or stronger explicit, attributable,
request-bound, replay-resistant human authorization.
