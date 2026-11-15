# Technical design: <name>

**Status:** Draft | Reviewed | Accepted

## Proposed architecture

Components, responsibilities, and why the change fits existing boundaries.

Before design approval, list each affected component as Reuse, Refactor,
Replace, or Remove and justify any compatibility layer.

## Components and interfaces

Typed request/response, schema/version, errors, bounds, and compatibility.

## Data flow

Include Mermaid when it clarifies request, decision, execution, and audit flow.

## Trust boundaries

Identify credential, principal, policy, approval, executor, adapter, and
operator trust. State which fields are trusted and their source.

## Security considerations

Threats, fail-closed behavior, secrets, filesystem/permission model, resource
limits, audit, and negative cases.

## Alternatives and tradeoffs

Consider at least one viable alternative and explain the choice.

## Compatibility implications

Installed paths, CLI, policy/config schemas, imports, dependencies, and
migration/rollback.

Document the supported canonical behavior and any compatibility layer's
consumer, owner, test, and removal condition.

## Verification and release evidence

List unit, integration, installed-layout, end-to-end, negative security,
static, type, dependency, install, runtime, and rollback checks as applicable.
Reference the production Definition of Done.
