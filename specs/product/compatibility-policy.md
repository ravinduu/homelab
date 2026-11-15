# Compatibility policy

**Status:** Adopted. The project is pre-1.0 and has no external compatibility
commitment unless one is explicitly recorded in a requirement or release
contract.

## Default policy

- Internal Python APIs, policy schemas, packaging layout, and client/server
  implementation details may change before 1.0.
- Keep one canonical policy schema and one runtime evaluator. Do not retain
  alternate runtime readers solely to avoid updating internal configuration.
- Remove obsolete code and compatibility facades when no documented consumer
  requires them.
- Preserve user-visible behavior only where a product requirement or
  controlled production transition requires it.
- Every retained compatibility layer needs a documented justification, owner,
  test, and removal condition.
- Breaking changes require a conversion procedure, preflight checks, rollback
  plan, and updated operations documentation. They must not weaken existing
  security controls.

## Production transition exception

An already installed server path is an operational dependency even without a
public API promise. Keep it only as long as needed to stage and verify its
replacement. The transition must identify the exact installed revision, use
administrator-controlled inputs, preserve a known-good rollback state, and
remove obsolete paths only after approved verification. This policy does not
authorize server changes.

## Schema 1 to schema 2 review

The current local Phase 3 `migrate_schema1` function reads schema 1 at runtime
and translates it into schema 2 policy objects. The repository is pre-1.0,
there are no external schema consumers, and the function creates a second
runtime policy path with separate validation and migration logic. The preferred
direction is to **remove schema 1 runtime migration before Phase 3 is released**.

Convert the canary configuration offline to the reviewed canonical schema 2,
compare decisions for the exact supported requests, and install schema 2 only
through a separately approved administrator transition. Retain a protected
copy of the previous configuration for rollback; rollback should restore a
known-good release, not enable a second live evaluator in the new code. Do not
change the live server as part of this policy decision. Phase 3 release review
must decide whether the existing deployed gateway needs a time-bounded
transition path and record its removal condition.

## Current path obligations

The installed `/usr/local/sbin` command names and exact `status` and
`restart jellyfin` requests currently have production evidence. They are
transition constraints, not permanent API promises. Any rename or request
contract change must be staged and approved because sudoers and operator tools
refer to those paths. Legacy module facades need separate consumer evidence;
internal tests alone do not justify keeping them.
