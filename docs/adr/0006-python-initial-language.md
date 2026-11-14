# ADR-0006: Python is the initial implementation language

- **Status:** Accepted for current scripts; package architecture is proposed
- **Date:** 2026-11-14

## Context

Current gateway, helper, and client are Python scripts using the standard
library; the host has an expected `/usr/bin/python3` runtime.

## Decision

Keep Python for the initial framework and preserve installed script behavior.
Adopt package metadata or a `src/` package only as part of a separately tested
incremental migration.

## Alternatives

Rewrite now in another language or move scripts immediately. Rejected for
foundation work because it adds compatibility and supply-chain risk without a
feature need.

## Consequences

Interpreter, import path, isolated mode, and dependency provenance are part of
the trusted computing base and require explicit verification.

## Reconsider when

Measured security, portability, or maintenance needs justify a migration with
equivalent path/CLI/installer tests and a safe rollback.
