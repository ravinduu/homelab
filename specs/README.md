# Specification system

This directory is the source of product intent and proposed architecture. It
does not grant authority to alter production. Follow:

**SPEC → DESIGN → TASKS → BUILD → VERIFY → RELEASE**

Architecture Review is the first part of DESIGN. Each phase directory contains
`spec.md`, `design.md`, `tasks.md`, and `verification.md`. Keep these files
short and actionable, and link detailed runbooks or evidence where they live.

Before a change, inspect current components and record which are reused,
refactored, replaced, or removed. Use the templates in a scoped feature or
phase workspace and link each requirement to evidence. A design or
specification may be draft; label its status and do not treat draft text as an
approved deployment revision.

## Reading order

1. `../AGENTS.md` and `product/{vision,principles,requirements,roadmap}.md`
2. Relevant `architecture/` specifications and accepted ADRs in `../docs/adr/`
3. Exactly the active `phases/phase-NN-*/spec.md`
4. Feature design, tasks, and verification records

## Status vocabulary

Phase and release statuses use the lifecycle in
[`product/quality-standards.md`](product/quality-standards.md): Planned, Design
Approved, In Development, Code Complete, Verification Pending, Release Ready,
Released. Evidence descriptions separately use:

- **Observed**: directly present in a reviewed repository artifact.
- **Reported**: recorded in project documentation or operational notes, not
  independently rechecked in this task.
- **Verified**: supported by named executed checks or deployment evidence.
- **Unverified**: evidence is absent, stale, incomplete, or out of scope.

Do not describe a phase as complete or released based on implementation or
unit tests alone.

For each phase, execute the required order:

1. **SPEC:** Define functional and non-functional requirements, security
   requirements, dependencies, exclusions, measurable acceptance, and one
   working user scenario.
2. **DESIGN:** Inspect the actual implementation. Record reuse/refactor/
   replace/remove decisions, interfaces, trust boundaries, controls,
   alternatives, tradeoffs, migration, and rollback.
3. **TASKS:** Split the approved design into small vertical slices. Each task
   must produce a coherent, testable improvement; avoid speculative scope.
4. **BUILD:** Implement only the reviewed tasks, refactoring or deleting
   obsolete paths where needed. Keep production untouched absent approval.
5. **VERIFY:** Run applicable automated, static, security, integration,
   end-to-end, installation, runtime, and rollback checks. Record exact
   commands, target, revision, results, and limitations.
6. **RELEASE:** Prepare the versioned artifact, installation/configuration,
   operator procedure, verification, rollback, and release evidence. Production
   deployment requires separate explicit authorization.

Phase specifications describe evidence current to their stated review dates;
Phase 3 was updated on 2026-11-15. Revalidate mutable server state before
operational decisions.

## Layout policy

Create files when they hold useful content; do not create empty directories or
placeholder packages. Current Python implementation lives in `src/homelab_ops/`;
privileged compatibility entrypoint sources live in `packaging/entrypoints/`.
`scripts/` contains the local CLI, shell inventory, and administrator
installer. The separate canary was reported installed; the production gateway
has not been migrated to the local package layout.
