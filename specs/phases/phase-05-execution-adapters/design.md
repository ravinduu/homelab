# Phase 5 design — bounded execution adapter

**Status:** Planned; select one adapter operation before design approval.

## Architecture review

| Component | Decision | Reason |
|---|---|---|
| Phase 2 gateway authorization/approval/audit boundary | Reuse as canonical policy enforcement; refactor only through reviewed interface changes. | Adapters must not bypass controls. |
| Current fixed restart implementation | Assess for reuse or refactoring into the first adapter; preserve its identity and approval protections. | Existing code is narrow and should not be generalized blindly. |
| First new adapter | Select exactly one operation and target after the user scenario and threat model are clear. | Candidate lists are not implementation scope. |
| Generic shell, Docker socket, arbitrary playbooks/manifests | Reject/remove from requester contract. | Unbounded authority is incompatible with the product boundary. |

## Required adapter contract

Specify typed request/result, operation/resource identity, authority and
approval requirements, exact executable/API, side effects, resource and time
bounds, idempotency, preflight, health verification, audit fields, and
operation-specific recovery. Treat Docker socket access as host-root
authority; do not assume containerization makes it safe.
