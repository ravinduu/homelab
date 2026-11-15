# Phase 3 — Generalized policy engine

**Status:** Verification Pending. Schema 2 evaluator and schema 1 runtime
migration exist locally and unit tests pass. The migration is under review per
the pre-1.0 compatibility policy. Installed integration, canary, rollback,
security review, and CI evidence remain outstanding.

## Objective and scope

Define and implement versioned server-side authorization over verified principals, roles, permissions, operation/resource scopes, and constraints with default-deny behavior. Out of scope: transport credential redesign (Phase 4), deployment adapters (Phase 5), and weakening Phase 2 compatibility.

## Dependencies

Phase 0 principles and architecture; Phase 2 gateway and protected policy baseline. Identity semantics must be explicit before policy grants are assigned.

## Functional requirements

- Resolve a stable principal from trusted server-side identity evidence. The
  shared `agent` account is one principal, not per-agent identity.
- Evaluate typed operation/resource requests against versioned protected
  policy.
- Support explicit permissions, exact resource scopes, stable denial reasons,
  and approval obligations. Unsupported constraints deny; wildcards and
  arbitrary expressions are outside this vertical slice.
- Validate one canonical policy schema and reject ambiguity/unknown unsafe
  constructs.
- Produce a policy revision and decision trace suitable for audit.

## Security and architecture considerations

Default deny; fail closed on load/parse/version error; no caller-supplied identity; no privilege from agent/vendor identity; no policy update from an agent request. Resolve explicit-deny precedence, role composition, conflict handling, path/resource canonicalization, and administrator promotion in design before coding.

## Deliverables

Canonical policy schema and design, principal mapping contract, evaluator,
offline conversion for current status/restart rules, unit/integration/negative
tests, operator policy editing and rollback procedures, install/E2E evidence,
and verification record.

## Acceptance criteria

Unknown principal/operation/resource and malformed policy deny; allowed cases
match reviewed matrices; restart cannot execute without separate valid
approval; current requests remain available during a controlled installed-path
transition; no Phase 4 identity claim is implied; tests cover conflicts,
boundary scopes, tampered files, and policy rollback. Released runtime accepts
one canonical schema; schema 1 runtime support is under review, not a permanent
compatibility commitment.

## Verification

Trace every requirement to evaluator, gateway integration, and installed-layout
tests; verify protected path rules, denial/no-execution behavior, representative
policy offline, and policy rollback. If schema 1 runtime support is removed,
compare old/new decisions in an offline fixture corpus. Production verification
requires separate approval and is not authorized by this spec.

## Migration / rollback

Convert the old protected policy offline; stage canonical policy separately;
compare old/new decisions over a fixture corpus; preserve current CLI behavior
during the approved transition; rollback to a known-good release and policy
without broadening permissions. Do not maintain two runtime evaluators solely
to simplify migration.

## Open questions

Phase 4 must replace the shared-account compatibility principal with a
per-credential mapping before claiming individual requester identity. Policy
authoring, protected promotion, and artifact provenance remain future work.

## Requirement-to-verification evidence

| Requirement | Implementation / evidence |
|---|---|
| Stable principal from trusted identity | `gateway/policy.py` resolves only the gateway-supplied Unix account from policy; unknown accounts deny. `unix:agent` is explicitly a shared-account compatibility identity. |
| Versioned typed policy and default deny | Schema 2 exact-key validation and `Decision` results in `gateway/policy.py`; `tests/test_gateway_policy.py` covers known/unknown operations, resources, principals, exact scope, and unmatched permission. |
| Roles and deny/conflict behavior | All assigned roles are evaluated; explicit deny takes precedence. Unit tests cover cross-role allow/deny conflict. |
| Approval obligation | Restart permission validation requires `require_approval: true`; execution continues to consume the existing separate single-use approval. Existing approval regression tests cover missing, expired, mismatched, replayed, and concurrent approvals. |
| Schema conversion | Current source contains a schema 1 runtime migration and unit fixture; compatibility-policy review recommends removing that reader before release and retaining the comparison as an offline conversion test. |
| Tampered/malformed policy fails closed | Strict keys, duplicate JSON key rejection, bounded file size, `O_NOFOLLOW`, regular-file/link/mode/owner checks, schema/reference validation; gateway path and evaluator negative tests. |
| Server test guide and no production deployment | `docs/operations/phase-03-policy-engine-dev-test.md` provides a canary-only manual update, allow/deny checks, evidence capture, and rollback. No server change was made in this implementation. |

Local verification on 2026-11-15: `python3 -m unittest discover -s tests -v`
passed all 49 tests before the current quality-policy changes; installer shell
syntax, Python compilation, and `git diff --check` passed. Current standards
tooling has not yet been fully run. Live schema 2 canary behavior is not
verified.

## Vertical slice and release evidence

- **User-visible capability:** The operator can review a policy decision for
  the existing status and Jellyfin restart requests; denied requests do not
  reach inventory or Docker execution.
- **Functional scope:** One canonical policy schema, verified principal
  mapping, exact resource/operation rules, role and deny composition,
  approval obligations, stable revision/reason, and operator migration and
  rollback. The current code is scoped only to two operations; do not claim a
  general adapter policy language.
- **Security invariants:** Default deny, no caller identity claims, protected
  policy, explicit-deny precedence, approval independent from policy,
  bounded parsing, and no side effects after denial.
- **Architecture/refactoring:** Before release, resolve schema 1 runtime
  support under the compatibility policy, centralize operation/resource
  semantics and schema validation, and eliminate duplicate approval
  obligations or dead helpers.
- **Tests:** Decision-matrix unit tests; schema 2 gateway integration allow and
  denial tests; malformed/tampered policy tests; installed isolated-package
  tests; disposable-host E2E and negative tests; compare migrated decisions
  only if a migration reader remains in approved scope.
- **Installation:** Install a reviewed schema 2 package and policy only in the
  canary namespace first. The current first-install installer is not an update
  mechanism; use only a reviewed administrator update procedure.
- **Runtime verification:** Verify schema 2 allowed status, explicit denial
  with no inventory execution, journal decision fields, restored policy, and
  successful status. A positive restart requires a separate approval and is
  not required to verify policy evaluation.
- **Rollback:** Restore a verified known-good canary package and policy, validate
  the canary authorization, and prove both allowed status and denied unsafe
  requests. Record the exact prior hashes. Production remains separate.
- **Acceptance / Definition of Done:** Do not advance beyond Verification
  Pending until all required quality gates, canary runtime tests, rollback
  evidence, and independent security/design review are recorded.
