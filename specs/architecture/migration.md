# Incremental code migration strategy

**Status:** Local source organization and compatibility tests implemented;
phase release verification remains pending. The production gateway package
migration is not recorded. The separate canary installation was reported by
the user and was not independently rechecked in this review.

## Target repository organization

Adopt this incrementally as real code and deployment workflows move. Omit
directories until they contain maintained files; do not create placeholder
packages. Python client, gateway, approval commands, and approval store have
moved into `src/homelab_ops/`; `packaging/entrypoints/` contains the minimal
legacy-path launchers/facade used by the installer. `scripts/` retains the
operator CLI, shell inventory, and administrator installer. `tests/`, `infra/`, `docs/`, and
`.agents/skills/` remain in their established locations.

```text
AGENTS.md                 repository contract
specs/                    product, architecture, phase plans, templates
src/homelab_ops/          shared and current Python implementation
  gateway/                current narrow gateway and approval CLI
  approvals/              current protected approval storage
  client.py               current local client implementation
  (identity/policy/audit/execution/adapters/transport added when implemented)
config/                   schemas and safe examples, never secrets
packaging/entrypoints/    small installed-path compatibility launchers
scripts/                  operator CLI, inventory and admin tooling
tests/                    unit, integration, security and compatibility tests
docs/                     installation, operations, security, ADRs
infra/                    reviewed desired-state proposals, not release input
.agents/skills/           repeatable project procedures
```

Keep approval state and runtime secrets outside Git in administrator-owned
host paths. Do not add a committed `ops/runtime-env/` or approval directory.

Preserve installed paths `/usr/local/sbin/homelab-ops`,
`homelab-ops-approve-restart`, `homelab_ops_common.py`,
`homelab-inventory`; `/etc/homelab-ops/gateway-policy.json`;
`/var/lib/homelab-ops/approvals/{pending,consumed}`; sudoers exact-argument
entries; and `scripts/homelab-ops`. Entry-point sources live in
`packaging/entrypoints/` and preserve the installed executable names. The
updated first-install script installs the
protected server package at `/usr/local/lib/homelab_ops`, retaining the legacy
shared-module facade in `/usr/local/sbin`. It remains first-install-only and
refuses existing destinations. The production gateway installation has not
been migrated or revalidated. Preserve CLI argv, policy schema, file modes,
and error codes during a reviewed transition.

Migration result:

1. Implementation modules are in `src/homelab_ops/`; only installed-path
   launchers/facade remain under `packaging/entrypoints/`.
2. `scripts/` contains the local CLI, shell inventory, and administrator
   installer; it no longer contains privileged Python gateway sources.
3. The installer accepts an exact protected package subset and refuses
   existing destinations. Local tests/syntax checks pass; production package
   migration is unverified.
4. Any live package update requires separate review, exact hashes,
   administrator approval, verification, and a rollback plan.

No unused package directories were created. Compatibility tests cover package
APIs, old command paths, isolated imports, package permissions, and existing
policy behavior. The local move does not imply production migration.
