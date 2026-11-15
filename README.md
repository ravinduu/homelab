# homelab-ops

`homelab-ops` is a supervised infrastructure operations framework in
specification and incremental development. Its current implementation is a
personal Debian/Docker foundation: a restricted inventory wrapper and a
root-controlled gateway with a deliberately small operation set.

Agents and automation are requesters, not trusted execution authorities. A
server-side boundary must authenticate the transport principal, evaluate
protected policy, apply any required human approval, and execute only bounded
operations. The client is never the authorization boundary.

The [product goal and v1.0 success criteria](specs/product/vision.md) describe
the complete inspect → explain → recommend → approve → execute → verify →
audit workflow. The seven phase releases and current status are in the
[roadmap](specs/product/roadmap.md).

## Current status

Phases 0–3 contain local implementation and prior operational reports, but
remain **Verification Pending** under the current production Definition of
Done. No CI run or current live-server verification is claimed here. Phase 3
is implemented locally; its architecture and quality assessment is in
[`reports/phase-03-quality-assessment.md`](reports/phase-03-quality-assessment.md).
Phases 4–7 are planned.

## Development

Read [`AGENTS.md`](AGENTS.md), then [`specs/README.md`](specs/README.md) and the
active phase documents before changing implementation. The quality toolchain
is documented in [`specs/product/quality-standards.md`](specs/product/quality-standards.md).
Create an ignored project-local environment with Python 3.11, install the
pinned development tools, then run the checks:

```sh
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-quality.txt
make quality
```

The standard-library suite can also run without the optional quality tools:

```sh
python3 -m unittest discover -s tests -v
```

The client prints requests without sending them by default. `--send` contacts
the configured SSH alias and is a remote operation. Never use it as a local
test shortcut.

## Repository map

- `specs/`: product, architecture, phases, and development templates.
- `pyproject.toml`, `requirements-quality.txt`, `Makefile`: package metadata and
  local quality gates; the package declares no runtime dependencies.
- `src/homelab_ops/`: Python client, gateway, and approval implementation.
- `scripts/`: operator CLI, read-only shell inventory wrapper, and administrator
  bootstrap installer.
- `packaging/entrypoints/`: compatibility entrypoint sources installed at the
  legacy privileged command paths.
- [Canary install runbook](docs/operations/homelab-ops-canary.md): separate
  first-install namespace for trying the new package beside the current one.
- [Phase 3 canary development test](docs/operations/phase-03-policy-engine-dev-test.md):
  local checks and administrator-led policy evaluation on the existing canary.
- `infra/`: local policy proposals and sanitized Compose snapshots, not
  implicitly deployable releases.
- `docs/`, `reports/`: operational documentation and evidence-based reviews.
- `tests/`: local unit/regression tests; remote SSH and Docker actions are
  mocked where described by the test suite.

The local implementation migration and compatibility boundary are documented
in [`specs/architecture/migration.md`](specs/architecture/migration.md).
The user-reported canary installation is separate from the production gateway;
production package migration and Phase 3 schema 2 installation are not claimed
by this repository status. Existing installed command paths remain a
transition constraint until a reviewed migration explicitly changes them.
