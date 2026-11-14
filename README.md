# homelab-ops

`homelab-ops` is a supervised infrastructure operations framework in
specification and incremental development. Its current implementation is a
personal Debian/Docker foundation: a restricted inventory wrapper and a
root-controlled gateway with a deliberately small operation set.

Agents and automation are requesters, not trusted execution authorities. A
server-side boundary must authenticate the transport principal, evaluate
protected policy, apply any required human approval, and execute only bounded
operations. The client is never the authorization boundary.

## Current status

- Phase 0 specifications and local package-layout migration are complete;
  `specs/` records the architecture and compatibility boundary.
- Phase 1 restricted discovery and sanitized inventory are implemented and
  documented; tests exist for the local inventory wrapper.
- Phase 2 gateway, approval helper, bootstrap installer, and regression tests
  exist. The November 14 operations record reports installed server behavior
  for status and approved Jellyfin restarts. This repository inspection did
  not independently contact the server; see the phase specification for
  evidence limits.
- Phase 3 and later are planned. No generalized policy engine is implemented.

## Development

Read [`AGENTS.md`](AGENTS.md), then [`specs/README.md`](specs/README.md) and the
active phase documents before changing implementation. Existing local checks:

```sh
python3 -m unittest discover -s tests -v
```

The client prints requests without sending them by default. `--send` contacts
the configured SSH alias and is a remote operation. Never use it as a local
test shortcut.

## Repository map

- `specs/`: product, architecture, phases, and development templates.
- `src/homelab_ops/`: Python client, gateway, and approval implementation.
- `scripts/`: operator CLI, read-only shell inventory wrapper, and administrator
  bootstrap installer.
- `packaging/entrypoints/`: compatibility entrypoint sources installed at the
  legacy privileged command paths.
- `infra/`: local policy proposals and sanitized Compose snapshots, not
  implicitly deployable releases.
- `docs/`, `reports/`: operational documentation and evidence-based reviews.
- `tests/`: local unit/regression tests; remote SSH and Docker actions are
  mocked where described by the test suite.

The local implementation migration and compatibility boundary are documented
in [`specs/architecture/migration.md`](specs/architecture/migration.md).
Installed command paths remain stable; the new package layout has not been
deployed to the server.
