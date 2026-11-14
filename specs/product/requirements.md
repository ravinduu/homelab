# Product requirements

**Status:** Baseline requirements for the roadmap. `Implemented` describes
observed local capability, not blanket production readiness.

## Functional

| ID | Requirement | Current evidence/status |
|---|---|---|
| FR-001 | Client supports only explicitly defined operations and targets. | Implemented: status/restart jellyfin client and gateway allowlists. |
| FR-002 | Client defaults to a non-sending dry run. | Implemented and covered by client tests. |
| FR-003 | Gateway provides bounded sanitized read-only inventory. | Implemented through fixed inventory executable; inventory tests exist. |
| FR-004 | Gateway performs a restart only for a fixed, policy-mapped service after approval. | Implemented for Jellyfin; live behavior reported in docs. |
| FR-005 | Operations have typed resource/operation schemas independent of shell syntax. | Planned; current interface is exact argv. |
| FR-006 | Policies support versioned principals, roles, permissions, scopes, and constraints. | Planned Phase 3. |
| FR-007 | Adapters expose capabilities without changing the shared security boundary. | Planned. |
| FR-008 | Requests and decisions have attributable audit records. | Implemented local syslog behavior; retention/integrity not established. |

## Security

| ID | Requirement | Current evidence/status |
|---|---|---|
| SR-001 | Unknown requests are rejected before command execution. | Implemented and negative-tested. |
| SR-002 | Server authorization does not trust client allowlists. | Implemented fixed gateway checks; generalized policy planned. |
| SR-003 | Requester cannot write policy, executables, approval state, or privileged inputs. | Installation design and path checks exist; current remote permissions need revalidation. |
| SR-004 | Sensitive execution requires a distinct, short-lived, single-use approval. | Implemented for Jellyfin restart; evidence in tests and operations note. |
| SR-005 | No arbitrary shell, caller command, Docker flags, or paths reach privileged execution. | Exact request parsing and fixed argv are implemented. |
| SR-006 | Policy and approval parsing rejects unsafe filesystem objects and malformed data. | Implemented checks/tests; race and filesystem hardening remain review topics. |
| SR-007 | Transport authenticates the connection but does not itself imply application authorization. | SSH is current transport; stronger per-principal identity mapping planned. |
| SR-008 | Denials and outcomes are auditable without leaking secrets. | Fixed syslog events implemented; tamper resistance/retention unverified. |
| SR-009 | Privileged actions fail closed on policy, identity, approval, timeout, or execution errors. | Implemented for narrow operations; future components must meet this invariant. |

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

## Compatibility

| ID | Requirement | Current evidence/status |
|---|---|---|
| CR-001 | Preserve `/usr/local/sbin/homelab-ops`, helper, module, and inventory paths. | Required for migration; observed in source and install docs. |
| CR-002 | Keep exact current status and restart request behavior until a reviewed migration. | Required. |
| CR-003 | Local tests remain runnable with documented dependencies and stable commands. | Standard-library unittest suite documented. |
| CR-004 | Policy/config schema changes are versioned and have migration/rollback plans. | Planned; current schema is version 1. |

## Non-functional

| ID | Requirement | Target |
|---|---|---|
| NFR-001 | Minimize privileged code and third-party dependencies. | Mandatory design review. |
| NFR-002 | Operations are deterministic, bounded, and explainable. | Acceptance criterion for adapters. |
| NFR-003 | Interfaces are agent/vendor independent and machine-readable. | Planned transport/API work. |
| NFR-004 | Documentation maps requirements to implementation and verification evidence. | Adopted by this specification workflow. |
| NFR-005 | Multiple-host coordination never weakens per-host policy or audit. | Planned Phase 7 constraint. |
