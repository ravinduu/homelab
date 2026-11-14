# ADR-0003: Authorization is enforced server-side

- **Status:** Accepted baseline for current and target architecture
- **Date:** 2026-11-14

## Context

Clients can be modified or compromised. A client allowlist cannot restrict a
privileged server operation.

## Decision

The server maps trusted identity to principal and evaluates protected policy
for every request. Unknown and malformed cases deny. Client checks are only
usability support.

## Alternatives

Client-only enforcement or trusting an agent's claimed role. Rejected because
the requester controls those inputs.

## Consequences

Policy/schema changes need protected deployment, tests, and migration. Phase 3
must generalize without weakening exact Phase 2 behavior.

## Reconsider when

Never for privileged execution; implementation mechanics may evolve while the
server remains authoritative.
