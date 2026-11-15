# Phase 1 design — single-server discovery

**Status:** Draft; review before any Phase 1 implementation change.

## Architecture review

| Component | Decision | Reason |
|---|---|---|
| `scripts/homelab-inventory` | Reuse after verifying the installed contract. | It owns the fixed, bounded Docker inventory boundary. |
| `src/homelab_ops/client.py` and SSH request path | Refactor only where required for a typed read-only request/result. | Keep transport and presentation separate; dry-run remains safe by default. |
| Current sanitized inventory fields and tests | Reuse as the initial supported data contract, then remove unsupported fields. | Avoid inventing broad discovery scope. |
| Direct Docker access and arbitrary host commands | Remove from requester path. | They would bypass the intended least-privilege boundary. |

## Contract and trust boundaries

The requester submits a fixed discovery request. SSH authenticates the
transport account; the server wrapper independently restricts the action.
Return bounded inventory with source, observation time, truncation and
unavailable indicators. A small deterministic summary may map observed
container state to documented meaning and a supported recommendation. Keep
observation, inference, and recommendation distinct. No state-changing request
belongs to this phase.

## Alternatives and tradeoffs

Retain the fixed inventory wrapper for the first supported Debian/Docker
environment instead of adding a generic discovery plugin framework. A new
environment requires its own adapter design and acceptance evidence.

## Verification/release design

Test fixed argv, maximum work/output, timeout, malformed input, redaction, and
denial before side effects. Verify an installed wrapper on an isolated host;
document exact hash, owner/mode, authorization, runtime evidence, and rollback.
