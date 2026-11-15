# Phase 3 architecture and quality assessment

**Review date:** 2026-11-15
**Status:** Assessment of local source and repository evidence only. No host was
contacted and no server change was made.

## Summary

The local implementation can evaluate a small schema 2 policy for the
existing `status` and Jellyfin restart operations. Its unit tests demonstrate
some allow, deny, conflict, scope, and schema validation behavior. That is not
yet a production-quality generalized policy engine or a released vertical
slice. Phase 3 remains **Verification Pending**.

The project has no external pre-1.0 policy commitment. The recommended
direction is one canonical schema and evaluator. Remove the schema 1 runtime
migration before Phase 3 release; convert configuration offline and migrate
the canary only through a separately approved, reversible administrator
procedure. This recommendation does not change the live server.

## Verified findings

| Priority | Finding | Evidence and impact |
|---|---|---|
| P0 | Schema 1 and schema 2 have separate runtime paths. | `gateway/core.py` accepts both; `gateway/policy.py:migrate_schema1` synthesizes schema 2 at runtime. The test suite uses schema 1 for most gateway dispatch/approval tests. There are no external commitments recorded. This duplicates validation and decision semantics and makes schema 2 not the sole supported runtime contract. |
| P0 | The “generalized” evaluator only recognizes two fixed operations and exact local resources. | `parse_request`, `validate_policy`, `evaluate`, the schema 1 migration, and the canary installer each encode `status`, `restart`, or Jellyfin assumptions. This matches the current two-operation scope but does not establish a reusable operation/resource contract for later adapters. |
| P1 | Approval obligation is represented twice. | `Decision.require_approval` is returned, while `run_restart` unconditionally consumes the fixed approval. Validation now hardcodes that restart must require approval. This preserves the safeguard but creates two sources of truth and does not demonstrate a general obligation executor. |
| P1 | Policy validation is duplicated in the canary installer. | The installer reimplements schema, principal, role, permission, and Jellyfin checks rather than invoking the canonical validator. The strict equality to one baseline policy is a bootstrap restriction, not a general policy authoring/validation tool. Drift between runtime and install-time validation is possible. |
| P1 | The schema 2 gateway integration is under-tested. | `tests/test_gateway_policy.py` tests schema 2 evaluation directly. The gateway no-execution denial test injects a schema 2 policy, while the principal status success and most restart integration tests use schema 1. No test exercises a valid schema 2 protected policy through the installed isolated entrypoint. |
| P1 | Installed-layout tests do not establish a functioning installation. | Entry-point subprocess tests primarily assert fail-closed behavior when fixed system paths are absent. Package-tree tests use a temporary tree for mode/symlink checks, but the full installer and resulting artifact are not executed end to end. |
| P1 | No integration/E2E or completed CI, type-checking, security scanner, dependency audit, or wheel validation evidence exists. | Before this standards change the repository had unittest files and shell/Python installers, but no CI workflow, pyproject, or quality tool configuration. This task adds those configurations; CI and the non-Ruff static/security/package checks have not run. |
| P1 | No Phase 3 install/upgrade/rollback evidence exists. | The canary first-install script refuses existing destinations. The Phase 3 development guide now contains a manual canary update and rollback procedure, but it has not been exercised on a disposable host or the home server. |
| P1 | No live schema 2 decision evidence exists. | Prior canary operation reports concern the earlier installed implementation. The current schema 2 code and policy have not been verified on the server. |
| P2 | There was an identical compatibility test method defined twice. | `GatewayRequestTests` contained duplicate `test_legacy_shared_module_path_remains_a_compatibility_facade` definitions; the later method shadowed the earlier one. One duplicate has been removed. |
| P2 | `resolve_principal` is unused. | The evaluator resolves the principal inline instead. Remove the dead helper or make it the single canonical resolver when Phase 3 is refactored. |

## Security assessment

### Verified safeguards

- Gateway request parsing remains exact and does not pass caller shell text to
  privileged commands.
- Unknown accounts, operations, resources, and unmatched rules deny in the
  schema 2 evaluator.
- Matching explicit deny overrides allows across assigned roles.
- Policy file loading is bounded, rejects duplicate keys, uses `O_NOFOLLOW`,
  and validates file type, link count, mode, and effective owner after open.
- Restart still requires the existing separate single-use approval and checks
  live container identity before restarting the verified full ID.
- The shared `agent` Unix identity is explicitly not represented as individual
  agent authentication.

These are source/test findings, not proof of current server file permissions
or runtime behavior.

### Gaps and residual questions

- The approval record does not bind a canonical request digest, stable policy
  revision, or attributable approver. Current approval scope is fixed to one
  restart and is protected by the existing helper; generalizing it requires a
  deliberate architecture decision.
- Decision events include principal/revision/reason, while later operation
  outcome events omit some of those fields. End-to-end audit correlation and
  retention/integrity are not established.
- Principal mapping is account-based and maps one shared `agent` account. It
  must not be described as per-agent authorization.
- Policy revision is operator-provided text, not signed provenance. Protected
  ownership remains the trust root for current policy.
- Root-controlled path checks are not a substitute for a tested update/promotion
  process. The manual canary update guide needs independent operational review.

## Required refactoring before release

1. Adopt one supported schema and remove the schema 1 runtime migration unless
   a time-bounded server transition is proven necessary. If retained, make its
   owner, scope, and deletion criterion explicit and test the exact deployed
   transition.
2. Define one canonical typed operation/resource request model and one policy
   validation/evaluation path. Avoid encoding operation catalogs separately
   in the parser, evaluator, installer, and migration function.
3. Make approval obligations explicit in the execution contract. A decision
   should either carry the obligation to a single enforcement point or the
   domain must clearly state that a fixed adapter operation always requires
   approval. Do not maintain both as independent rules.
4. Reuse the canonical schema validator during install/config validation, or
   define a tiny standalone validator artifact used by both runtime and
   installer. Keep separate policy content review from schema validation.
5. Remove `resolve_principal` if the canonical resolver is not going to use it.
6. Audit compatibility launchers/facades individually. Preserve them only for
   the administrator-controlled migration of actual installed consumers, not
   because internal tests assert historical layout.

## Missing acceptance evidence

- Decision matrix for each supported principal, operation, resource, role
  conflict, and approval obligation.
- Schema 2 gateway integration success and denial-before-side-effect tests.
- Schema 2 tests for duplicate/oversized/tampered policy, file replacement
  failure, malformed structures, and unknown fields.
- Installed isolated Python package test that runs a staged canary entrypoint
  against temporary policy/approval/command fakes.
- End-to-end allow and deny flow on a disposable Debian test target.
- Tested canary install/update interruption handling and tested rollback from
  the exact candidate revision.
- Security review of principal mapping, approval binding, audit event
  correlation, and policy promotion trust.
- CI execution of all configured checks on the exact candidate revision.
- Review of scanner findings and the full transitive quality-tool dependency
  set; current pins do not constitute a full lockfile.
- Written release record with source revision, artifact hashes, canary result,
  rollback result, reviewer, and residual risks.

## Prioritized remediation plan

| Order | Action | Exit evidence |
|---|---|---|
| 1 | Review and accept the single-schema compatibility decision. Convert schema 1 policy offline; do not change the server in this assessment. | ADR/design records schema 2 as canonical, a migration diff, decision-equivalence fixture, and rollback procedure. |
| 2 | Refactor Phase 3 to one request/policy/obligation path and remove dead/duplicated logic. | Architecture tests and schema 2 end-to-end integration tests pass; no unexplained runtime migration remains. |
| 3 | Exercise install/update/rollback in a disposable Debian environment using the exact canary package artifact. | Captured hashes, owners/modes, allow/deny results, no-side-effect denial, and rollback verification. |
| 4 | Run and resolve local/CI quality gates; review supply-chain inputs. | Green CI, report of all tool findings, pinned action/tool provenance, dependency audit, built wheel inspection. |
| 5 | Complete administrator review and separately authorized canary verification. | Approved exact revision and observed runtime/audit evidence. Production remains a separate release decision. |

## Verification run for this standards change

- `python3 -m unittest discover -s tests -v`: 49 tests passed on Python 3.9.6.
- Ruff 0.17.5 `check` and `format --check`: passed after import/style cleanup.
- `make shell-check`, targeted Python compilation, and `git diff --check`:
  passed.
- `make quality` and CI were not run. The local environment has Python 3.9.6
  and no installed mypy, Bandit, pip-audit, or build commands; the configured
  current mypy and pip-audit toolchain requires a newer Python. No dependency
  audit, security scan, wheel build, E2E, install, or rollback check is claimed.

## Readiness decision

**Not Release Ready.** Local unit tests and the Ruff/shell checks above are
useful evidence, but schema 2 is not yet exercised through the installed
runtime, the schema 1 compatibility path remains, operational upgrade/rollback
is untested, and CI, type, dependency, and security checks have not run for the
candidate. The quality workflow introduced with this assessment is
configuration only until it has executed successfully.
