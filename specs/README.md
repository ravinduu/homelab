# Specification system

This directory is the source of product intent and proposed architecture. It
does not grant authority to alter production. Follow:

**Specification → Technical Design → Task Breakdown → Implementation →
Verification → Review → Release**

For a change, copy the templates to a scoped feature or phase workspace, link
each requirement to acceptance evidence, and maintain the phase status as
implemented, in progress, planned, or unverified. A design or specification
may be draft; label its status and do not treat draft text as an approved
deployment revision.

## Reading order

1. `../AGENTS.md` and `product/{vision,principles,requirements,roadmap}.md`
2. Relevant `architecture/` specifications and accepted ADRs in `../docs/adr/`
3. Exactly the active `phases/phase-NN-*/specification.md`
4. Feature design, tasks, and verification records

## Status vocabulary

- **Observed**: directly present in a reviewed repository artifact.
- **Reported**: recorded in project documentation or operational notes, not
  independently rechecked in this task.
- **Verified**: supported by named executed checks or deployment evidence.
- **Planned**: desired future behavior with no claim of implementation.
- **Unverified**: evidence is absent, stale, incomplete, or out of scope.

Phase specifications describe evidence current to this repository review on
2026-11-14. Revalidate mutable server state before operational decisions.

## Layout policy

Create files when they hold useful content; do not create empty directories or
placeholder packages. Current Python implementation lives in `src/homelab_ops/`;
privileged compatibility entrypoint sources live in `packaging/entrypoints/`.
`scripts/` contains the local CLI, shell inventory, and administrator
installer. The server has not been migrated to this local package layout.
