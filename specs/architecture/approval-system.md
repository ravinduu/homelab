# Approval lifecycle

The Phase 2 helper creates a root-owned short-lived approval for `restart
jellyfin`, bound to requester label `agent`, operation, service, expiry, and
random nonce. The gateway opens without following symlinks, validates
properties/schema, and atomically renames pending to consumed before execution.
Failure or timeout does not restore it. Tests cover missing, expired,
mismatched, reused, concurrent, malformed, and permission-invalid records.

This is not a general approval service. Future records should bind canonical
request digest, verified principal, resource, policy revision, approver,
creation/expiry, and unique identifier. Creation is out of band; consumption
is atomic and replay resistant. Approval cannot override authorization or OS
permissions. Revocation, retention, clock trust, approver authentication, and
multi-approver workflows remain open.

See [ADR-0005](../../docs/adr/0005-approval-model.md).
