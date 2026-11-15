# Phase 6 — Agent integrations

**Status:** Planned.

## Objective and scope

Provide an agent-independent CLI and MCP integration, structured operation discovery, and machine-readable schemas used by multiple independent agents. MCP is an untrusted request adapter, not a security boundary. Out of scope: trusting model-generated identity, exposing a public unrestricted endpoint, or allowing arbitrary tools/commands.

## Dependencies

Stable Phase 3 principal/policy semantics, Phase 4 authenticated transport, and Phase 5 typed operation schemas.

## Requirements and architecture

Expose only server-authorized capabilities; validate all requests again at gateway; bound schema sizes and response data; version contracts; authenticate every request; surface approval-required state without allowing the requester to create its own approval. Do not rely on UI confirmation as server enforcement.

## Deliverables / acceptance

CLI and MCP contracts, discovery/schema format, at least two independent agent-client integrations, compatibility matrix, and conformance/adversarial tests. Acceptance: unsupported operations are absent or denied server-side; malformed/oversized requests fail safely; clients cannot bypass transport identity, policy, or approval.

## Verification

Protocol conformance, auth failures, replay, oversized inputs, schema evolution, malicious client tests, secret/redaction checks, and per-agent end-to-end tests.

## Migration / rollback

Add integrations as clients of the stable gateway contract. Revoke integration credentials or disable server capability to roll back; preserve CLI compatibility.

## Open questions

Which protocols are justified, capability discovery freshness, SDK languages, and whether local versus remote MCP hosting fits the trust model.

## Vertical slice and release evidence

- **User-visible capability:** A supported client can discover and submit one
  typed operation while the server independently authenticates and authorizes
  it.
- **Functional scope:** Select one integration and contract; do not implement
  CLI, MCP, and SDKs as a combined increment. Preserve only specified operator
  behavior.
- **Security invariants:** Client identity claims and approval prompts never
  grant authority; server validates every request; unsupported/malformed or
  oversized requests deny; credentials and secrets are not exposed.
- **Architecture/refactoring:** Reuse the canonical request and transport
  contract. Remove duplicate client allowlists or schemas if they diverge from
  server-owned definitions. Integrations remain untrusted requesters.
- **Tests:** Contract/unit tests; gateway integration; protocol conformance;
  malicious-client and auth/replay/size/redaction negatives; isolated end-to-end
  tests with supported principal credentials.
- **Installation:** Install/version the selected client independently from
  the server and provide protected credential setup and removal instructions.
- **Runtime verification:** Test against the canary server, verify success and
  denial paths, and correlate server audit events.
- **Rollback:** Revoke only the integration credential or disable its
  server-side capability; verify the core CLI/gateway remain intact.
- **Acceptance / Definition of Done:** Chosen integration passes quality
  standards and canary runtime/rollback evidence. An SDK/protocol evaluation
  alone does not complete the phase.
