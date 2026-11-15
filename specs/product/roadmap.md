# Product delivery roadmap

The target is one v1.0 product at the end of Phase 7. Phases 1–7 are
incremental releases of the same operation, identity, policy, approval,
execution, and audit contract. Phase 0 is an enabling repository foundation,
not a product release. A phase number or existing code does not establish
release status.

Statuses below reflect repository evidence reviewed on 2026-11-15. User-reported
server activity is identified as reported; this review did not access the
server.

| Milestone | User-visible working release | Required exit evidence | Current status |
|---|---|---|---|
| Phase 1 — Secure single-server discovery | An authorized operator requests bounded read-only inventory and receives a sanitized, timestamped health summary with source and limitations. | Supported install and read-only runtime check; output/redaction and denial tests; bounds/timeouts; documented recovery; exact revision and evidence. | **Verification Pending** — local wrapper/client/tests exist; prior host behavior is reported, not reverified. |
| Phase 2 — Approval-gated remediation | The operator requests one explicitly supported corrective action; the gateway authenticates the request, checks protected authorization, consumes a separate valid approval when required, executes a fixed operation, and verifies service health. | End-to-end allow, deny-before-side-effect, approval binding/replay/race/expiry, health verification, audit correlation, install and rollback evidence. | **Verification Pending** — narrow status/restart implementation and tests exist; prior server behavior is reported; complete current-revision release evidence is missing. |
| Phase 3 — Canonical policy and authorization | Administrators define a versioned protected policy for typed principals, operations, resources, roles, and obligations; gateway decisions are deterministic and explainable. | One supported runtime schema and evaluator; decision matrix; schema 2 gateway/installed tests; policy transition and rollback verified; security review. | **Verification Pending** — schema 2 evaluator exists locally; schema 1 runtime reader remains under review; installed schema 2, CI, rollback, and security evidence are outstanding. |
| Phase 4 — Independent agent identity | Each authorized agent has an independently mapped credential that can be rotated and revoked without granting shell or host privileges. | Credential-to-principal tests, host-key and forced-command checks, revocation denial, staged rotation/recovery, admin-approved runtime evidence. | **Planned** |
| Phase 5 — Production execution adapters | One selected infrastructure adapter executes a typed, bounded, policy-authorized operation with declared side effects, health check, and recovery. | Adapter-specific threat/design review, integration and disposable-host tests, negative arbitrary-input tests, immutable install and tested recovery. Additional adapters ship separately. | **Planned** |
| Phase 6 — Agent integrations | A standard CLI and MCP integration let multiple independent agents discover capabilities, submit typed requests, resume after approval, and receive verified reports. | CLI/MCP contract and adversarial tests; at least two independent agent clients; approval-resume and audit correlation; credential/setup and rollback evidence. | **Planned** |
| Phase 7 — Multi-server operations | Operators inspect and safely manage at least two independently authenticated hosts with clear per-host health, policy, audit, and partial-failure results. | Multi-host E2E; enrollment/revocation, isolation, policy drift, partial failure, per-host recovery and rollback; full v1.0 product success criteria. | **Planned** |

## Dependency and release rules

- Phase 1 establishes the supported observation and health evidence contract.
- Phase 2 adds one bounded, approval-gated remediation path on that contract.
- Phase 3 makes the gateway's authorization contract canonical before adding
  new principals or adapters.
- Phase 4 supplies independent identity; Phase 5 adds adapter capabilities
  behind the shared security boundary.
- Phase 6 adds clients to the stable request and approval-resume contract.
- Phase 7 composes already released single-host behavior; it does not replace
  per-host enforcement with a fleet-wide bypass.
- Each phase requires an installable increment, applicable quality gates,
  runtime evidence, operational documentation, and tested rollback before it
  is marked Released. Production deployment still requires explicit approval.
- v1.0 is one release after Phase 7, not a renumbering or declaration that
  earlier repository work was already released.

## Next highest-value vertical slice

Complete the Phase 1 read-only health report using the existing bounded
inventory as its only data source. Convert observed service/container state into
a concise report that distinguishes healthy, degraded, missing, stale,
truncated, and unavailable data; cite source and observation time; explain only
what the evidence supports; and offer only a documented recommendation. Keep
the result read-only and add fixture-driven tests for each state. Do not add a
new remote command or mutate a service. Then finish Phase 1 install/runtime/
rollback evidence before taking on the next product capability.
