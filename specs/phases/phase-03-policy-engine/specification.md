# Phase 3 — Generalized policy engine

**Status:** Planned only. This document is a specification scaffold, not implementation authority. No Phase 3 functionality is implemented here.

## Objective and scope

Define and implement versioned server-side authorization over verified principals, roles, permissions, operation/resource scopes, and constraints with default-deny behavior. Out of scope: transport credential redesign (Phase 4), deployment adapters (Phase 5), and weakening Phase 2 compatibility.

## Dependencies

Phase 0 principles and architecture; Phase 2 gateway and protected policy baseline. Identity semantics must be explicit before policy grants are assigned.

## Functional requirements

- Resolve a stable principal from trusted server-side identity evidence.
- Evaluate typed operation/resource requests against versioned protected policy.
- Support explicit permissions, scope/constraints, stable denial reasons, and approval obligations.
- Validate policy schema and reject ambiguity/unknown unsafe constructs.
- Produce a policy revision and decision trace suitable for audit.

## Security and architecture considerations

Default deny; fail closed on load/parse/version error; no caller-supplied identity; no privilege from agent/vendor identity; no policy update from an agent request. Resolve explicit-deny precedence, role composition, conflict handling, path/resource canonicalization, and administrator promotion in design before coding.

## Deliverables

Policy schema and design, principal mapping contract, evaluator, migration for current status/restart rules, unit/property/negative tests, operator policy editing and rollback procedures, verification record.

## Acceptance criteria

Unknown principal/operation/resource and malformed policy deny; allowed cases match reviewed matrices; approval-required decisions cannot execute without separately valid approval; existing CLI and installed Phase 2 paths remain compatible; no Phase 4 identity claim is implied; tests cover conflicts, boundary scopes, tampered files, and migration rollback.

## Verification

Trace every requirement to evaluator and integration tests; test installed isolated Python layout, protected path rules, denial/no-execution behavior, policy migration equivalence, and representative server policy offline. Production verification requires separate approval and is not authorized by this spec.

## Migration / rollback

Read old schema in compatibility mode only as explicitly designed; stage new policy separately; compare old/new decisions over a fixture corpus; preserve old protected file and exact CLI; rollback policy revision without broadening permissions.

## Open questions

Stable principal source before Phase 4; role and deny semantics; policy authoring/validation tool; atomic promotion and signature/provenance model.
