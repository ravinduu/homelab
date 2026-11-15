# Phase 5 — Infrastructure execution adapters

**Status:** Planned; no adapters beyond current fixed inventory/restart behavior are generalized.

## Objective and scope

Deliver one complete adapter vertical slice at a time. The first adapter and
operation must be selected in an accepted feature design before implementation;
the current candidate list (Docker/Compose, systemd, Ansible, scaling) is not
one phase-sized release. No arbitrary command, playbook, manifest, service,
or resource path is allowed.

## Dependencies

Phase 3 policy/obligation contract; Phase 4 identity and transport; Phase 2 execution/audit invariants. Each adapter requires a separate threat/design review.

## Requirements and architecture

Adapters declare operations/resources, permissions, input bounds, side effects, timeout, idempotency, result schema, and recovery. Docker socket use remains isolated and treated as host-root. Compose uses protected immutable releases and fixed runtime env references. systemd uses fixed unit allowlists. Ansible uses reviewed immutable playbooks and fixed inventory/vars. Scaling has hard min/max and resource budgets.

## Deliverables and acceptance

One adapter design and verification record per capability; policy mapping; integration test harness; install/rollback docs. Negative cases must prove arbitrary names/flags/paths/playbooks and out-of-range scale requests cannot execute.

## Verification

Mocked unit/integration tests, sandbox or disposable target tests, failure/timeout tests, privilege review, health and dependency checks, data-backup/rollback evidence. No production operation is authorized by this roadmap.

## Migration / rollback

Introduce one adapter at a time behind existing exact gateway; preserve Phase 2 request forms and policy. Remove capability by server policy first; rollback data-mutating effects only through separately approved procedure.

## Open questions

Executor isolation model; Docker API reduction; release signing; per-service backup/restore; supported systemd and Ansible semantics; scaling safety bounds.

## Vertical slice and release evidence

- **User-visible capability:** An operator can request one bounded,
  policy-authorized infrastructure action through a reviewed adapter.
- **Functional scope:** One named adapter operation with typed request/result,
  explicit target, side effects, idempotency, timeout, health check, and
  recovery semantics. Additional adapters are separate releases.
- **Security invariants:** No arbitrary executable, flag, path, environment,
  playbook, Compose input, or caller-supplied identity reaches privileged
  execution. The shared authorization, approval, audit, and resource limits
  always apply.
- **Architecture/refactoring:** Reuse the canonical policy/approval/execution
  boundary. Refactor current fixed restart implementation into an adapter
  only if tests prove no authorization or identity-check regression. Remove
  duplicate fixed execution paths after transition.
- **Tests:** Adapter unit tests; gateway/adapter integration; isolated E2E on
  disposable host; negative arbitrary-input, identity, permission, timeout,
  failure, health, data-loss, and recovery tests.
- **Installation:** Install only immutable reviewed adapter artifacts and
  fixed configuration; preserve secrets in protected runtime sources.
- **Runtime verification:** Canary the exact operation on disposable or
  explicitly approved target; verify health/dependencies and audit output.
- **Rollback:** Exercise the adapter's own recovery path and remove policy
  authorization first. Data replacement recovery requires its separate
  administrator procedure.
- **Acceptance / Definition of Done:** One adapter at a time meets every
  applicable quality standard. A design for multiple candidate adapters is
  not release evidence.
