# Code layout migration: task breakdown

**Status:** Local source migration implemented; phase remains Verification
Pending under the production Definition of Done. No production gateway migration
is recorded.

1. [x] Record migration design, target package boundary, and compatibility
   surface.
2. [x] Move approval storage, gateway, approval CLI, and client into
   `src/homelab_ops/`.
3. [x] Keep the operator CLI in `scripts/` and move privileged compatibility
   launcher sources into `packaging/entrypoints/`.
4. [x] Update first-install source validation and packaging for
   `/usr/local/lib/homelab_ops`, preserving legacy paths and overwrite refusal.
5. [x] Add package API and compatibility launcher tests, isolated-mode import
   checks, and package mode/symlink/link-count negative cases.
6. [x] Update repository organization, installation docs, and migration
   evidence; no server change was made.
7. [x] Run full unittest suite, shell syntax/installer checks, bytecode
   compilation, and `git diff --check`; record results and limitations.

Verification: 39 tests passed; installer and inventory shell syntax passed;
Python modules compiled with the bytecode cache redirected to `/tmp`;
`git diff --check` passed. The installer was not executed. No live package
installation was validated.
