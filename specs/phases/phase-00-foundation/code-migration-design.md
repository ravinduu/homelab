# Code layout migration: technical design

**Status:** Accepted; local source migration implemented, production installation remains out of scope.

## Proposed architecture

Move Python implementation modules into `src/homelab_ops/` by responsibility:

```text
src/homelab_ops/
  __init__.py
  client.py
  approvals/{__init__.py,store.py}
  gateway/{__init__.py,core.py,cli.py,approval_cli.py}
```

Keep shell inventory and administrator bootstrap in `scripts/`. Keep the
operator CLI at `scripts/homelab-ops`. Place privileged installed-path
launchers and the legacy common-module facade in `packaging/entrypoints/`;
the installer installs them at existing absolute paths. Do not add unused
identity, policy, adapter, or transport packages or package metadata yet.

## Components and interfaces

- `client.main(argv)` preserves `--send`, dry-run formatting, SSH alias,
  operation parsing, and allowlist behavior.
- `gateway.core` owns gateway parsing, policy, status/restart dispatch, and
  stable constants/error behavior.
- `approvals.store` owns protected approval files and current storage API.
- `gateway.approval_cli.main(argv)` owns administrator approval CLI.
- Installed launchers preserve filenames; privileged launchers validate
  installed package ownership/modes before importing from a fixed path.
- Installed Python package lives under `/usr/local/lib/homelab_ops`; legacy
  executable/module locations under `/usr/local/sbin` remain stable.

## Data flow and trust boundaries

The local client shim resolves the repository's `src/` for development. The
privileged installed shim never imports from the current directory or
environment: it verifies the root-owned package tree, adds only
`/usr/local/lib`, imports the implementation, then retains the existing
gateway checks. Administrator install stages an exact reviewed package file
set in a root-only directory and installs it root-owned. Request arguments,
policy, approval, executor and audit behavior remain unchanged.

## Security considerations

Keep Python isolated mode for installed privileged entry points. Validate all
package files and package directories before import; package files must be
regular, root-owned, exact mode, single-link, and under non-writable
root-owned parents. The installer must reject missing, extra, symlinked,
hard-linked, writable, or unowned staged files and refuse existing
destinations. No shell execution or policy expansion is introduced.

## Alternatives and tradeoffs

- Leave all code in `scripts/`: lowest risk but does not establish the
  requested `src/` package boundary.
- Move all current scripts into packages and rename installed executables:
  rejected because this breaks sudoers/install paths and CLI compatibility.
- Use package metadata/system installation now: deferred because runtime
  dependency and release requirements are not yet specified.

## Compatibility implications

Preserve local command `scripts/homelab-ops`, installed executables
`/usr/local/sbin/homelab-ops` and
`/usr/local/sbin/homelab-ops-approve-restart`, legacy import path
`/usr/local/sbin/homelab_ops_common.py`, gateway argv, approval schema, policy
schema, timeouts, audit and error behavior. The bootstrap remains
first-install-only and refuses an already-installed host. No server update is
part of this migration.
