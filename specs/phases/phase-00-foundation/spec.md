# Phase 0 — Project foundation

**Status:** Verification Pending. Local foundation and package-layout work exist;
production release evidence and the newly adopted quality gates are incomplete.

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
- The Phase 0 package-layout migration changed organization only; it added no policy capability or server operation at that time.
- Markdown links resolve and `git diff --check` passes.

## Verification

Review internal consistency, paths, and retained AGENTS security rules; run documentation checks. No runtime tests are required for docs-only changes.

## Migration / rollback

No runtime migration. Correct or revert documentation locally if review finds errors; preserve all pre-existing work.

## Open questions

The policy/principal model was provisionally selected for Phase 3. Policy
promotion and credential ownership remain open and must be resolved in their
own phases.

## Vertical slice and release evidence

- **User-visible capability:** Contributors can understand the framework
  boundary, phase sequence, and local development/review workflow.
- **Functional scope:** Product requirements, architecture, ADRs, templates,
  quality standards, and local source organization. No server operation.
- **Security invariants:** Documentation must not imply local source grants
  production authority; infrastructure restrictions in `AGENTS.md` remain
  authoritative.
- **Architecture/refactoring:** Reuse current Python/SSH/sudo boundary
  documents; replace the implicit permanent-compatibility stance with the
  pre-1.0 policy. Review/remove duplicate or obsolete docs rather than adding
  another parallel guide.
- **Tests:** Markdown link checks, status/requirement consistency, `git diff
  --check`, and the CI quality workflow configuration review. Unit, E2E, and
  deployment tests are not applicable to documentation-only changes and need
  a stated reason in verification.
- **Installation/runtime:** Install repository revision through its normal
  source-control workflow; no host installation or runtime change.
- **Rollback:** Revert the documentation/configuration revision without
  changing server state.
- **Acceptance / Definition of Done:** Every phase has a truthful status and
  vertical-slice contract; engineering and compatibility policy is approved;
  all applicable quality-standards items have named evidence. Current status
  remains Verification Pending until CI and document review are recorded.
