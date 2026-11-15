# Side-by-side gateway canary: tasks

**Status:** Local tooling and runbook complete. No server install performed.

1. [x] Define disjoint paths, same-host risk, exact request set, and rollback.
2. [x] Add canary gateway and approval launchers that load the local package
   without importing or changing the current installed package.
3. [x] Add canary client dry-run targeting only the canary gateway.
4. [x] Add first-install-only canary bootstrap with protected staging,
   reviewed hashes, exact sudoers, and canary-only cleanup.
5. [x] Add tests for canary path separation, launchers, dry-run behavior,
   filesystem checks, and installer source validation.
6. [x] Publish an operator runbook with copy/stage, hash comparison, install,
   read-only verification, optional approved restart, and rollback steps.
7. [x] Run full local tests, shell syntax checks, bytecode compilation, Markdown
   link checks, and `git diff --check`. Do not contact the server.

## Verification evidence

- `python3 -m unittest discover -s tests -v`: 42 tests passed.
- `sh -n` passed for both gateway installers and the inventory wrapper.
- Python bytecode compilation passed for `src/`, packaging entrypoints, and
  both client scripts; cache output was directed to `/tmp`.
- 59 Markdown files checked; all local links resolve.
- `git diff --check` passed.
- No server connection, installation, or production operation was performed.
