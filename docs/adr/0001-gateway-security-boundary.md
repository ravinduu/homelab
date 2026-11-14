# ADR-0001: Gateway is the server-side security boundary

- **Status:** Accepted baseline (existing Phase 2 implementation and project policy)
- **Date:** 2026-11-14

## Context

Clients are not trusted to enforce policy. An unrestricted remote admin
endpoint would turn agent compromise into host compromise.

## Decision

Clients submit bounded requests. A protected server-side gateway independently
validates the exact operation and controls execution. The gateway is not a
public unrestricted administrative endpoint.

## Alternatives

Trust client allowlists/prompts; grant agents direct Docker/shell access; expose
a generic remote command service. Rejected because each expands or relocates
the privileged boundary to an untrusted requester.

## Consequences

More server-side code and policy maintenance; clearer enforcement and audit
boundary. Preserve existing installed paths while evolving this boundary.

## Reconsider when

An alternative can demonstrate equal or stronger independent server-side
authentication, authorization, bounded execution, and recovery guarantees.
