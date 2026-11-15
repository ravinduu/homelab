# Phase 2 — Secure operations gateway

**Status:** Verification Pending. Local implementation exists and server
behavior is reported in `docs/homelab-ops-phase-2.md`; current revision and
rollback evidence are not independently verified here.

## Objective and scope

Root-controlled bounded gateway, exact sudo scope, administrator bootstrap, protected policy, one-use approval, and audit for `status` and `restart jellyfin`. Source includes gateway, shared module, approval helper, installer, tests, proposed policy, and operations/installation docs.

Out of scope: deploy, rollback, other services, arbitrary Docker/Compose, host changes, agent remote installation, and generalized policy engine.

## Dependencies and requirements

Depends on Phase 1 restricted access. FR-001–004, SR-001–009, OR-001–005, RR-001/002/004, CR-001/002. Server policy is authoritative. Approval is separate from SSH and authorization. Client defaults to dry-run. Installer refuses existing destinations; successful fresh install is not claimed.

## Architecture and security

Root execution; exact argv; fixed paths/environment; isolated interpreter; protected JSON policy; protected one-use state; fixed inventory delegation; live identity inspection before restart by full ID; bounded timeout; fixed authpriv audit. No Docker/socket or general sudo rights for `agent`.

## Deliverables and acceptance

Acceptance requires local regression suite and installer syntax validation, administrator review of protected inputs/live mapping, `visudo` validation, negative permission checks, and live status/restart verification with separate approval. Docs record 34 suite tests at an earlier checkpoint and 17 gateway tests after Nov 14; these are not rerun here. Host checks are not independently verified in this task.

## Migration / rollback

Preserve installed paths and Phase 1 sudo rule. Roll back by disabling the exact Phase 2 sudoers entry, verifying denial, then inspecting/removing only known installed files per installation docs. Approval retention is administrator-controlled.

## Open questions

Confirm installed hashes/modes, sudoers entry, approval storage, live mapping, audit retention, and status-output handling before any update.

## Vertical slice and release evidence

- **User-visible capability:** Request sanitized status or request one approved
  Jellyfin restart through the bounded gateway.
- **Functional scope:** Exact request parsing, protected service map, separate
  one-use approval, container identity check, fixed restart argv, bounded
  timeout, post-action health verification, and correlated audit events. No
  deploy, generic Docker, or host admin.
- **Security invariants:** Server policy is authoritative; no shell or caller
  command; no `agent` Docker/general sudo access; approval cannot bypass
  authorization and is consumed once before execution.
- **Architecture/refactoring:** Reuse the gateway boundary and approval store
  only as canonical owners. Do not preserve compatibility facades or duplicate
  validators without an installed consumer and a time-bounded transition plan.
- **Tests:** Unit and gateway integration tests for valid/invalid requests,
  approval replay/race/expiry, path tampering, live identity mismatch,
  timeout/failure, no execution on denial, and secret redaction; installed
  isolated package and disposable Debian E2E tests.
- **Installation:** Administrator-reviewed immutable package, exact hashes,
  protected policy/state modes, validated sudoers, no destination overwrite,
  and tested failure cleanup.
- **Runtime verification:** Verify status and negative requests; verify restart
  only under separate explicit operation approval, then check health and
  dependent services. Report success only after the declared health check;
  capture decision/execution/outcome audit correlation and exact revision.
- **Rollback:** Disable the exact gateway authorization first, prove denial,
  restore the prior known-good files/policy, validate sudoers, and retain
  approval/audit data. Test in canary before release.
- **Acceptance / Definition of Done:** Meet all applicable quality standards
  and record host, revision, install, runtime, and rollback evidence. Reported
  operations alone do not release this phase.
