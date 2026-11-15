# Side-by-side gateway canary: technical design

**Status:** Local implementation proposal. Server installation requires a
separate administrator-run procedure; this work does not install it.

## Goal and non-goals

Allow an administrator to test the new package on `home-server-01` without
replacing or sharing state with the current gateway. The first live request is
read-only status. The canary may expose the same fixed Jellyfin restart
operation behind its own single-use approval. It does not update, upgrade,
uninstall, or alter the current installation, policy, state, or sudoers file.

## Fixed canary namespace

| Purpose | Canary path |
|---|---|
| Gateway | `/usr/local/sbin/homelab-ops-canary` |
| Approval helper | `/usr/local/sbin/homelab-ops-approve-restart-canary` |
| Package root | `/usr/local/lib/homelab-ops-canary/homelab_ops` |
| Policy | `/etc/homelab-ops-canary/gateway-policy.json` |
| Approval state | `/var/lib/homelab-ops-canary/approvals/{pending,consumed}` |
| Sudoers drop-in | `/etc/sudoers.d/homelab-ops-canary` |

The client is `scripts/homelab-ops-canary`, defaults to dry-run, and targets
only the canary gateway path. It reuses the existing SSH alias and account.
No environment variable or request argument selects the namespace.

## Architecture and trust boundaries

Canary entrypoints validate the root-owned canary package before importing
it, load from a canary-only `sys.path` parent, and set fixed canary constants
for policy, approval state, and entrypoint checks. The imported implementation
is the same reviewed `src/homelab_ops/` source. The approval module receives
canary-only paths before any command dispatch. Both implementations may act on
the same production Jellyfin container, but they do not share pending approval
files. The canary installer adds a separate exact-argument sudoers rule and
does not edit the current rule.

## Installation behavior

The root-only first-install bootstrap accepts one exact staged package subset,
checks source/destination ownership, modes, links, paths, policy schema, live
Jellyfin identity, existing inventory authorization, and sudoers syntax; it
prints hashes and requires the interactive phrase `INSTALL CANARY`. It refuses
any pre-existing canary destination. Failure cleanup disables only its own
sudoers entry before deleting only paths created by that invocation.

## Verification and impact

Local tests cover namespace separation, dry-run target, isolated imports,
protected package checks, exact source list parsing, and installer embedded
Python syntax. Server-side installation and status are manual steps. Status
uses the existing read-only inventory. A canary restart interrupts production
Jellyfin and remains a separate explicit operation after reviewing its
impact; it is guarded by a separately created canary approval.

## Rollback

As administrator, remove only `/etc/sudoers.d/homelab-ops-canary`, run
`visudo -c`, verify canary requests are denied, then inspect and remove only
the canary entrypoints, package, and policy. Preserve canary approval/audit
state until retention is decided. Never touch the current gateway paths or
state during canary rollback.
