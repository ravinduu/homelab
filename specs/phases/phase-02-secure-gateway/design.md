# Phase 2 design — approval-gated remediation

**Status:** Draft; review current gateway before implementation changes.

## Architecture review

| Component | Decision | Reason |
|---|---|---|
| `gateway/core.py` | Reuse the exact request and server-side dispatch boundary; refactor duplicated responsibility. | It is the privileged decision/execution choke point. |
| Approval store/helper | Reuse only after binding and lifecycle review; refactor to one canonical approval validator. | Approval must be separate, protected, time-bounded, and single-use. |
| Fixed Jellyfin restart path | Keep as the sole initial mutation while its need is specified; replace only through a reviewed migration. | Narrow operation scope is safer than a generic executor. |
| Client allowlist | Keep for usability only; never treat it as authorization. | Server policy must remain authoritative. |
| Generic shell/Docker execution | Remove/reject. | It bypasses typed operations and expands the trusted code base. |

## Contract and trust boundaries

Authenticate the request at the server boundary, authorize exact operation
and resource, validate a separate approval when required, execute fixed argv,
and verify service health. Bind approval to principal, operation, resource,
expiry and policy context. Emit correlated, redacted decision and outcome
events. Approval creation is a distinct human/admin workflow and never trusts
an unauthenticated chat message.

## Alternatives and tradeoffs

Start with one fixed adapter operation. Do not adopt a generic executor until a
separate design proves it can preserve the same typed input, isolation,
approval, audit, timeout, and recovery guarantees.
