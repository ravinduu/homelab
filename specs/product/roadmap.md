# Roadmap

Statuses are based on repository artifacts and the dated operations notes
reviewed 2026-11-14. Reported server activity is not independently rechecked
here. Phase 3 is planning only; no Phase 3 behavior is authorized or present.

| Phase | Status | Dependencies | Measurable milestone / exit evidence |
|---|---|---|---|
| 0 Foundation | Complete locally | Repository evidence | Product/architecture/phase specs, ADRs, templates, and local package migration are present; security contract retained; compatibility suite and local checks pass. No server migration. |
| 1 Discovery | Implemented locally; operation reported | SSH account and approved wrapper | Negative argument, timeout, truncation and sanitization tests pass; admin verifies installed path, mode and invocation rule. |
| 2 Secure gateway | Implemented locally; server behavior reported | Phase 1 | Exact operation, approval replay/race, identity mismatch and protected-path tests pass; administrator verifies installed hashes/modes, sudoers and approved live operation. |
| 3 Generalized policy | Planned | Phase 0 and 2; principal semantics decision | Versioned schema/evaluator; decision matrix tests for allow, deny, conflicts, scopes and approval obligations; legacy Phase 2 decisions preserved by fixture comparison. |
| 4 Remote security | Planned | Phase 3 principal model and administrator access procedure | Per-principal credential mapping; revoked key denial, host-key mismatch and shell/forwarding negative checks; staged rotation and rollback demonstrated. |
| 5 Execution adapters | Planned | Phases 3–4 | Each adapter separately reviewed and tested for fixed scope, denied arbitrary inputs, timeout, failure, health and recovery; deploy adapter only after immutable release flow exists. |
| 6 Agent integration | Planned | Stable policy, transport and adapter contracts | Protocol conformance and adversarial tests; unsupported operations denied server-side; compatibility and secret-redaction evidence recorded. |
| 7 Multi-server | Planned | Phases 3–6 and single-host recovery | Enrollment/revocation, policy drift, partial failure, isolation, audit correlation and per-host rollback tests pass in multi-host simulation. |

Dependencies are sequential where trust assumptions change: Phase 3 depends on
the Phase 0 vocabulary and Phase 2 invariants; Phase 4 depends on stable
principal semantics; Phase 5 depends on policy and approval contracts; Phase 6
depends on stable operation discovery/schema; Phase 7 depends on per-host
identity, policy distribution, and audit guarantees. No phase implies
deployment permission.
