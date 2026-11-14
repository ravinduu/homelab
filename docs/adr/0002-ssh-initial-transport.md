# ADR-0002: SSH is the initial transport

- **Status:** Accepted for current single-host implementation; future transport remains open
- **Date:** 2026-11-14

## Context

The current host is reached through a designated SSH alias/account and exact
restricted operations already fit this channel.

## Decision

Use SSH initially. Transport authentication does not imply agent identity,
authorization, or human approval. Keep requests restricted and server-checked.

## Alternatives

Public HTTP gateway, VPN-only generic API, agent-specific protocol. These may
be evaluated later but require additional exposure, identity, lifecycle, and
compatibility design.

## Consequences

Reuse existing access controls and avoid a public listener; shared Unix
identity limits attribution and credential isolation.

## Reconsider when

Per-agent authentication, exposure, revocation, audit, and isolation needs
cannot be met safely by the SSH design.
