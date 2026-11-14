# Phase 0 — Project foundation

**Status:** Complete for the documented foundation and approved local code-layout migration; no production migration.

## Objective

Establish product intent, security architecture, development contract, traceability, and a compatibility-preserving route for later implementation.

## Scope / non-goals

In scope: specifications, threat model, roadmap, templates, ADRs, agent workflow, compatibility migration plan, and the separately requested local Python package migration with legacy launchers. Out of scope: Phase 3 behavior, server changes, installation, or policy redesign.

## Dependencies

Repository evidence review of `AGENTS.md`, scripts, tests, policies, docs, skills, and Compose snapshots.

## Requirements and architecture

Supports FR-004 evidence capture, OR-003 process, CR-001 compatibility, NFR-004 traceability. Retain paths and skills. Clearly label target design as proposal and distinguish it from current state.

## Deliverables

Product/architecture specifications; Phase 0–7 specifications; templates; ADR-0001–0006; migration strategy; repository development contract.

## Acceptance criteria

- Every phase states objective, scope, exclusions, dependencies, requirements, security, architecture, deliverables, acceptance, verification, migration, and rollback.
- Phase 1/2 claims cite repository artifacts or dated records and state limits.
- Phase 3 remains planned; the package move changes organization only and adds no Phase 3 capability or server operation.
- Markdown links resolve and `git diff --check` passes.

## Verification

Review internal consistency, paths, and retained AGENTS security rules; run documentation checks. No runtime tests are required for docs-only changes.

## Migration / rollback

No runtime migration. Correct or revert documentation locally if review finds errors; preserve all pre-existing work.

## Open questions

Which policy/principal model should Phase 3 select? Who owns policy promotion and key lifecycle? See architecture open decisions.
