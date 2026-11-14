# Phase 5 — Infrastructure execution adapters

**Status:** Planned; no adapters beyond current fixed inventory/restart behavior are generalized.

## Objective and scope

Add typed bounded adapters for Docker, Docker Compose, systemd, explicitly approved Ansible operations, and bounded scaling. Each adapter is independently scoped; this phase does not grant arbitrary command, arbitrary playbook, manifest, service, or resource-path execution.

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
