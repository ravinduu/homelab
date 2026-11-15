# Phase 4 — Remote access security

**Status:** Planned.

## Objective and scope

Give each authorized principal managed credentials and restricted, authenticated transport with rotation, revocation, and isolation. Scope includes SSH restrictions, private-network assumptions, host-key verification, credential lifecycle, and incident procedures. Out of scope: public administrative API and unapproved firewall/SSH changes.

## Dependencies

Phase 3 principal and authorization contracts; administrator-controlled host access and recovery procedures.

## Requirements and security

SR-007 plus new per-principal credential requirements. Separate authentication from authorization/approval. Restrict forwarding/PTY/commands; never expose secrets to clients or logs; support immediate revocation and safe rotation overlap; rate-limit and bound connection/request resources. Network controls need separate high-risk admin procedure.

## Architecture considerations

SSH remains initial transport unless evidence supports a replacement. Decide credential issuer/owner, principal binding, host keys, known-host distribution, authorized-key lifecycle, shared `agent` transition, and emergency break-glass access.

## Deliverables / acceptance

Credential and threat design, least-privilege SSH configuration proposal, rotation/revocation procedure, migration plan, integration/negative tests. Acceptance: revoked credential is denied, each active credential maps to one principal, shell/forwarding bypasses fail, host identity is verified, and existing inventory/gateway behavior remains available during staged cutover.

## Verification

Test auth matrix, stolen/revoked credential response, forced-command restrictions, key rotation, concurrency limits, host-key mismatch, and recovery without exposing secrets.

## Migration / rollback

Add new credential path alongside current restricted account, test, then disable old authorization only through separately approved admin action. Define rollback that restores access without broadening privilege.

## Open questions

Credential authority, private network, host-key distribution, multi-agent account design, and break-glass owner.

## Vertical slice and release evidence

- **User-visible capability:** An operator can authenticate a uniquely mapped
  principal and revoke/rotate its credential without granting shell or host
  administration.
- **Functional scope:** Select one credential enrollment and rotation path;
  identify, authenticate, revoke, and recover. Other transports/credential
  authorities require separate accepted increments.
- **Security invariants:** Host-key verification, one credential-to-principal
  mapping, server-side policy, no PTY/forwarding/command bypass, revocation
  denial, secret non-disclosure, and a tested break-glass path.
- **Architecture/refactoring:** Replace shared-account identity claims only
  after the selected per-principal path is tested; remove obsolete identity
  mapping code after controlled cutover. Do not add transport abstraction
  without a second justified implementation.
- **Tests:** Unit identity mapping; SSH integration tests for auth/host keys,
  revoked credentials, forced-command restrictions, shell/forwarding denial;
  isolated E2E rotation/recovery and negative tests.
- **Installation:** Administrator-controlled staged key/authorized-key update;
  no agent sudo/group changes. Include exact host-key and credential inventory.
- **Runtime verification:** Verify new principal identity and operation
  decisions, revoke the test credential and verify denial, then confirm the
  old supported path remains only for the documented transition window.
- **Rollback:** Restore the prior restricted access credential without
  widening permissions; prove revocation/rollback behavior in a test host.
- **Acceptance / Definition of Done:** All quality-standard checks and staged
  runtime/rollback evidence pass. Firewall and SSH changes still require the
  separate high-risk administrator procedure.
