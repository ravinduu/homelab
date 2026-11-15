# Phase 4 design — independent agent identity

**Status:** Planned; design approval required before implementation.

## Architecture review

| Component | Decision | Reason |
|---|---|---|
| SSH transport | Reuse initially if host identity and forced-command behavior pass review. | Avoid adding a second transport without a security or product need. |
| Shared Unix `agent` principal | Replace through staged credential/principal migration. | It cannot distinguish agents or provide independent revocation. |
| Phase 3 policy principal mapping | Refactor to consume authenticated credential identity from trusted server evidence. | Never trust a principal name supplied in request data. |
| Credential issuer/rotation machinery | Select or build only after owner, threat boundary and recovery are designed. | The authority and lifecycle are not yet decided. |

## Required design decisions

Specify enrollment authority, credential storage/handling, principal binding,
host-key distribution, rotation overlap, revocation timing, concurrency/rate
bounds, old-identity retirement, and break-glass recovery. Demonstrate that
PTY, forwarding, arbitrary commands, and account switching are denied.
