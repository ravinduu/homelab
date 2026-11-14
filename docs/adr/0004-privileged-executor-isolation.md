# ADR-0004: Privileged execution stays narrow and isolated

- **Status:** Accepted baseline for Phase 2; target adapter isolation is proposed
- **Date:** 2026-11-14

## Context

Docker and host administration can grant broad host authority. A gateway
should not become a generic root shell.

## Decision

Current gateway uses exact requests, fixed paths/argv/environment, no shell,
timeouts, protected inputs, and a distinct executor path. Future adapters must
declare bounded operations and remain downstream of authorization.

## Alternatives

General command runner, unrestricted Docker group membership, dynamic client
commands. Rejected due to excessive privilege and injection surface.

## Consequences

New capabilities require explicit adapter-specific policy, testing, and
recovery. Docker socket adapters remain high risk even when mounted read-only.

## Reconsider when

Isolation details can change if an alternative reduces trusted code and
privilege while preserving constraints and auditable enforcement.
