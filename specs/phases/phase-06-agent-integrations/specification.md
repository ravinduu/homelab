# Phase 6 — Agent integrations

**Status:** Planned.

## Objective and scope

Provide agent-independent CLI and protocol integrations, structured operation discovery, machine-readable schemas, and SDK evaluation. MCP is a possible adapter, not a security boundary. Out of scope: trusting model-generated identity, exposing a public unrestricted endpoint, or allowing arbitrary tools/commands.

## Dependencies

Stable Phase 3 principal/policy semantics, Phase 4 authenticated transport, and Phase 5 typed operation schemas.

## Requirements and architecture

Expose only server-authorized capabilities; validate all requests again at gateway; bound schema sizes and response data; version contracts; authenticate every request; surface approval-required state without allowing the requester to create its own approval. Do not rely on UI confirmation as server enforcement.

## Deliverables / acceptance

CLI contract, discovery/schema format, optional MCP integration design, compatibility matrix, SDK decision, conformance and adversarial tests. Acceptance: unsupported operations are absent or denied server-side; malformed/oversized requests fail safely; clients cannot bypass transport identity, policy, or approval.

## Verification

Protocol conformance, auth failures, replay, oversized inputs, schema evolution, malicious client tests, secret/redaction checks, and per-agent end-to-end tests.

## Migration / rollback

Add integrations as clients of the stable gateway contract. Revoke integration credentials or disable server capability to roll back; preserve CLI compatibility.

## Open questions

Which protocols are justified, capability discovery freshness, SDK languages, and whether local versus remote MCP hosting fits the trust model.
