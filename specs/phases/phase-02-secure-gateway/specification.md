# Phase 2 — Secure operations gateway

**Status:** Implemented locally; server behavior is reported in `docs/homelab-ops-phase-2.md`, not independently rechecked in this task.

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
