# Phase 1 — Infrastructure discovery

**Status:** Verification Pending. Local implementation exists and host behavior
is reported in prior records; current release evidence has not been rechecked.

## Objective and scope

Restricted SSH-based read-only observation and sanitized host/service health
reporting. The initial supported slice uses the existing bounded Docker
inventory to identify observed running/unhealthy/missing states. Explain only
what the data supports, cite source and observation time, and recommend only a
documented supported action; do not execute it in this phase. Repository
evidence includes `scripts/homelab-inventory`, its tests, installation/security
docs, audit report, and local CLI.

Out of scope: direct Docker access for `agent`, secrets/environment capture, service changes, unrestricted discovery, fresh live claims without observation, and gateway deployment.

## Requirements and security

FR-003, OR-004, SR-005, SR-009, CR-003. Reject arguments; use fixed executable and Docker calls; enforce timeouts and a 100-container cap; do not bypass OS permissions. Treat remote results as scoped, timestamped evidence.

## Dependencies and architecture

Designated SSH account, installed root-owned inventory wrapper, narrowly authorized invocation. Local client dry-runs; `--send` contacts the host.

## Deliverables and acceptance

Inventory wrapper, client, health-summary contract, docs, and tests.
Acceptance: report source/time and missing/unhealthy state accurately; an
unhealthy observation maps only to an evidence-backed explanation and
documented recommendation; unauthorized arguments fail before Docker;
limits/timeouts and sanitization hold; local tests pass; administrator
separately verifies the exact remote sudo rule and modes.

## Verification, migration, rollback

Verify wrapper cases, SSH restrictions, and installed mode as administrator. Rollback requires a separate approved change to inventory authorization; do not infer live rollout from code. No migration is proposed.

## Open questions

Current installation, effective SSH restrictions, and output policy should be reconfirmed when operationally needed.

## Vertical slice and release evidence

- **User-visible capability:** An authorized operator receives bounded,
  sanitized, read-only health summary through the documented CLI/wrapper.
  Each reported fact names its source and observation time; diagnosis and
  recommendations are explicitly separated and remain limited to evidence.
- **Functional scope:** Fixed inventory commands, validated bounded output,
  timeouts, truncation behavior, and dry-run/request behavior. No lifecycle
  mutation or secrets.
- **Security invariants:** Reject arguments before Docker; never grant Docker
  socket/general sudo; cap work/time/output; redact host paths, env, labels,
  credentials, and uncontrolled output as specified.
- **Architecture/refactoring:** Reuse the inventory wrapper and client only
  where each remains the single owner of its boundary. Remove future deploy or
  rollback request shapes from this phase if they remain in the client.
- **Tests:** Unit tests for fixed argv, malformed input, bounds, timeout,
  truncation, sanitization, and truthful summary states for missing/stale
  observations; installed-wrapper integration; disposable-host E2E; negative
  unauthorized-argument and secret-redaction tests.
- **Installation:** Administrator-controlled install records exact wrapper
  hash, owner/mode, sudoers invocation, and rollback steps.
- **Runtime verification:** Read-only inventory on an approved test/host;
  verify returned fields and denied paths. Revalidate reported production
  install rather than inferring it from local files.
- **Rollback:** Disable only the inventory authorization through a separate
  approved administrator procedure; verify the request is denied and preserve
  unrelated gateway access.
- **Acceptance / Definition of Done:** All applicable criteria in
  `specs/product/quality-standards.md`, including CI and install/runtime
  evidence. Until recorded, the phase stays Verification Pending.
