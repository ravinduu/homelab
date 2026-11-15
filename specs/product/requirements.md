# Product requirements

**Status:** Baseline requirements for the roadmap. `Implemented` describes
observed local capability, not blanket production readiness.

## Functional

| ID | Requirement | Current evidence/status |
|---|---|---|
| FR-001 | Client supports only explicitly defined operations and targets. | Local `status`/`restart jellyfin` paths exist; phase release remains Verification Pending. |
| FR-002 | Client defaults to a non-sending dry run. | Locally implemented and unit tested; release evidence pending. |
| FR-003 | Gateway provides bounded sanitized read-only inventory. | Local fixed wrapper/tests exist; prior host behavior is reported, not currently reverified. |
| FR-004 | Gateway performs a restart only for a fixed, policy-mapped service after approval. | Local implementation and tests exist; prior server behavior is reported, not currently reverified. |
| FR-005 | Operations have typed resource/operation schemas independent of shell syntax. | Partial local Phase 3 request model; end-to-end schema contract not accepted or release verified. |
| FR-006 | Policies support versioned principals, roles, permissions, scopes, and constraints. | Local schema 2 evaluation exists for exact status/restart resources; not yet release verified and does not support general constraints. |
| FR-007 | Adapters expose capabilities without changing the shared security boundary. | Planned. |
| FR-008 | Requests and decisions have attributable audit records. | Local syslog events exist; decision/outcome correlation, retention, and integrity are not established. |
| FR-009 | Health summaries cite source and observation time, separate facts from diagnosis/recommendation, and disclose missing or stale data. | Planned; current inventory is raw bounded data, not a complete health-summary workflow. |
| FR-010 | A workflow can wait for valid approval and resume the exact pending request without changing its identity or scope. | Planned; current approval consumption is gateway-side and does not provide agent workflow continuation. |
| FR-011 | A successful mutation is followed by its declared outcome/health verification; failure and partial completion are explicit. | Not established for a product workflow; current restart has narrow execution checks only. |
| FR-012 | Fleet results retain per-host identity, policy, audit, and partial-failure state. | Planned. |

## Security

| ID | Requirement | Current evidence/status |
|---|---|---|
| SR-001 | Unknown requests are rejected before command execution. | Implemented and negative-tested. |
| SR-002 | Server authorization does not trust client allowlists. | Fixed gateway checks and local schema 2 evaluator exist; installed Phase 3 policy behavior is unverified. |
| SR-003 | Requester cannot write policy, executables, approval state, or privileged inputs. | Installation design and path checks exist; current remote permissions need revalidation. |
| SR-004 | Sensitive execution requires a distinct, short-lived, single-use approval. | Implemented for Jellyfin restart; evidence in tests and operations note. |
| SR-005 | No arbitrary shell, caller command, Docker flags, or paths reach privileged execution. | Exact request parsing and fixed argv are implemented. |
| SR-006 | Policy and approval parsing rejects unsafe filesystem objects and malformed data. | Implemented checks/tests; race and filesystem hardening remain review topics. |
| SR-007 | Transport authenticates the connection but does not itself imply application authorization. | SSH is current transport; stronger per-principal identity mapping planned. |
| SR-008 | Denials and outcomes are auditable without leaking secrets. | Fixed syslog events implemented; tamper resistance/retention unverified. |
| SR-009 | Privileged actions fail closed on policy, identity, approval, timeout, or execution errors. | Implemented for narrow operations; future components must meet this invariant. |
| SR-010 | Approval is bound to the authenticated principal, exact operation/resource, expiry, and applicable policy context; it is single use. | Existing approval is fixed to one restart; full binding and product-level evidence remain to be specified and verified. |
| SR-011 | One host's credentials, compromise, or failure cannot silently grant authority over another host. | Planned Phase 7 invariant. |

## Operational

| ID | Requirement | Current evidence/status |
|---|---|---|
| OR-001 | Installation is administrator-controlled and validates protected inputs. | Bootstrap script and checklist exist; first-install refusal and previous install reported. |
| OR-002 | No deployment occurs from a requester-writable working tree. | Documented design; release promotion is not implemented. |
| OR-003 | Each operation has preflight, impact, verification, and recovery guidance. | Exists for current restart/install; later operations need phase-specific procedures. |
| OR-004 | Inventory has fixed limits and timeouts. | Implemented and tested for 100-container cap and bounded execution. |
| OR-005 | Policy, approval, and audit storage locations and ownership are explicit. | Current paths documented; retention and lifecycle policy open. |

## Reliability

| ID | Requirement | Current evidence/status |
|---|---|---|
| RR-001 | One-use approvals cannot be replayed or concurrently consumed twice. | Atomic consume behavior and tests exist; host filesystem assumptions remain. |
| RR-002 | Operation timeouts are bounded and failures return non-success. | Implemented and tested locally. |
| RR-003 | Recoverable changes have a known-good revision and safe rollback path. | Required for future deploy operations; current restart has no release rollback. |
| RR-004 | Partial installation failure does not leave an enabled incomplete policy. | Installer attempts cleanup; host-side execution evidence is not independently checked here. |
| RR-005 | Fleet and multi-step results distinguish success, failure, unavailable, and partial outcomes without false aggregate success. | Planned. |

## Compatibility

| ID | Requirement | Current evidence/status |
|---|---|---|
| CR-001 | Avoid breaking currently installed command paths without a controlled transition. | Operational transition constraint only; not a permanent internal API promise. |
| CR-002 | Preserve the specified status and restart behavior until a reviewed product change and approved transition. | Required for the current installed service; retire through an explicit migration if the contract changes. |
| CR-003 | Local tests remain runnable with documented dependencies and stable commands. | Standard-library unittest suite documented. |
| CR-004 | Policy/config changes use one canonical versioned schema and include conversion/rollback evidence. | Phase 3 standard; schema 1 runtime compatibility is under review for removal. |

## Non-functional

| ID | Requirement | Target |
|---|---|---|
| NFR-001 | Minimize privileged code and third-party dependencies. | Mandatory design review. |
| NFR-002 | Operations are deterministic, bounded, and explainable. | Acceptance criterion for adapters. |
| NFR-003 | Interfaces are agent/vendor independent and machine-readable. | Planned transport/API work. |
| NFR-004 | Documentation maps requirements to implementation and verification evidence. | Adopted by this specification workflow. |
| NFR-005 | Multiple-host coordination never weakens per-host policy or audit. | Planned Phase 7 constraint. |
| NFR-006 | Every release has one documented end-to-end scenario with measurable acceptance and requirement-to-evidence links. | Required for every phase. |
| NFR-007 | v1.0 product success criteria are demonstrated together after Phase 7, not inferred by summing unit-test results. | See `vision.md`; required at final release review. |
