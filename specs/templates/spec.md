# Feature / phase specification: <name>

**Status:** Planned | Design Approved | In Development | Code Complete |
Verification Pending | Release Ready | Released

## Architecture review

Record current evidence, uncertainties, and impacted components:

| Component | Reuse / Refactor / Replace / Remove | Reason and compatibility justification |
|---|---|---|

## Context and problem

Who needs the capability and what operational problem does it solve?

## User-visible vertical slice

State one complete, testable capability delivered by this phase. List user
scenarios, preconditions, success, denial, and recovery behavior.

## Functional scope and exclusions

Define supported operations, resources, inputs, outputs, limits, and explicit
non-goals. Split independent adapters/protocols into separately reviewable
increments.

## Security invariants

Define identity source, authorization boundary, approval requirements, data
handling, bounded resources, fail-closed behavior, audit requirements, and
negative cases.

## Expected architecture

Describe module boundaries, data contracts, dependencies, and where policy,
approval, execution, and audit responsibilities live.

## Requirements and dependencies

List requirement IDs and phase/system prerequisites. Link each requirement to
measurable acceptance and verification evidence.

## Tests and quality gates

Specify unit, integration, installed-layout, end-to-end, negative security,
static analysis, type checking, dependency, and packaging checks as applicable.
Name commands, fixtures, target, and expected outcomes.

## Installation and configuration

State artifact source/revision, protected configuration, owners/modes,
preflight, installation, and secret handling. If not applicable, state why.

## Runtime verification

Name the disposable/canary/production target, health/denial/audit checks,
dependencies, and exact evidence to record. Production execution still needs
separate authorization.

## Rollback

Name the known-good revision, disable/restore order, verification, data/audit
retention, and rollback test. Never broaden access during recovery.

## Acceptance and Definition of Done

List measurable outcomes and every applicable item in
[`../product/quality-standards.md`](../product/quality-standards.md). A phase
cannot be Released without its evidence record and release review.

## Open questions

Record unresolved security, compatibility, or acceptance decisions, their
owner, and the point before which they must be resolved.
