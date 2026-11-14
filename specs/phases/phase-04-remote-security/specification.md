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
