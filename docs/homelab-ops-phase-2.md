# Homelab Operations Phase 2: status and Jellyfin restart

**Implementation state (updated 2026-11-14):** The gateway was already installed on `home-server-01`; the first-install script correctly refused to replace it. The shared approval module was then updated in place with the protected-path stat-result fix. Server logs show status success and two successful Jellyfin restarts after the update; an unapproved request was denied. No sudoers, approval-storage, or Compose configuration changes were made.

**Local source layout:** Python implementation lives in `src/homelab_ops/`; compatibility entrypoint sources live in `packaging/entrypoints/`, while `scripts/homelab-ops` remains the operator CLI. This repository migration has not been installed on the server; reported host behavior refers to the previously installed entry points and does not verify this package layout.

## Scope

Only `status` and `restart jellyfin` are implemented. The Phase 1 approved inventory observed `/jellyfin` running, healthy, and using `jellyfin/jellyfin:latest`; it did not expose Compose labels or a stable container ID. The independent server policy is currently a local proposal and its project/service labels must be verified by an administrator before installation. At restart time, the gateway checks the live name, image, Compose project/service labels, and running state, then restarts by the verified container ID. Deploy, rollback, other services, arbitrary Docker commands, and host reboot are intentionally unsupported.

## Request path and privilege separation

```text
local homelab-ops client
        │ fixed SSH alias and exact arguments
        ▼
sudoers: only gateway status | gateway restart jellyfin
        │ root-owned, non-agent-writable gateway
        ├── status → fixed approved inventory executable
        └── restart jellyfin → root policy + one-use requester-bound approval
                                  → inspect fixed service identity → restart verified ID
```

The client defaults to dry-run. Its `--send` flag only transports the request; sudoers and the gateway independently validate it. `agent` receives no Docker group membership, Docker socket access, sudo shell, direct Docker command, approval-helper access, or authority over approval storage.

The gateway accepts exact argument arrays only: `status` or `restart jellyfin`. It uses fixed absolute paths, Python isolated mode, a fixed child environment that redirects Docker CLI config/home lookups away from root's credentials, `subprocess.run` with argument arrays and `shell=False`, bounded execution time, and generic errors. Status delegates to `/usr/local/sbin/homelab-inventory`, whose clean worker also uses `/nonexistent` for `HOME` and `DOCKER_CONFIG`. Restart loads `/etc/homelab-ops/gateway-policy.json`, verifies the live container against its fixed mapping, and restarts only the full verified Docker ID.

## One-use approval

An administrator-only helper creates a single JSON approval bound to operation, service, requester (`agent`), random nonce, and expiry 120 seconds from creation. It publishes the file atomically into root-owned mode-`0700` directories and refuses to replace an existing pending approval. The record is mode `0600`, root-owned, and the agent cannot write or traverse the storage directory.

The gateway opens with `O_NOFOLLOW`, validates owner, mode, file type, link count, size, exact JSON keys, request binding, nonce, and the short expiry. It atomically renames the pending record into a protected consumed directory before running Docker. A missing, expired, mismatched, malformed, reused, or concurrently consumed approval fails closed. Failed or timed-out Docker execution still consumes the record.

## Audit and failure behavior

Requests and outcomes log caller, fixed operation/service, and result to authpriv syslog; approval creation is logged separately. Approval JSON, environment values, and Docker output are not logged. Status returns only the existing inventory wrapper output. Timeouts are 185 seconds for status and 35 seconds for restart. Exit codes distinguish malformed request (`64`), approval/policy denial (`77`), timeout (`124`), and underlying command errors (nonzero).

## Validation performed locally

Unit tests use temporary approval directories and mocked command runners. They cover exact operation allowlists, malformed arguments, status command and environment, policy permission failure, live identity/Compose ownership checks, fixed restart argv, requester mismatch, missing/expired/mismatched/reused approvals, concurrent consumption, protected file modes/owners, approval creation refusing overwrite, timeouts, command errors, and approver argument rejection. No Docker daemon or SSH call is made by the tests.

Run:

```sh
python3 -m unittest discover -s tests -p 'test_homelab_ops_gateway.py' -v
```

The full local suite passes 34 tests. Python bytecode compilation, parsing of both policy JSON files, and `git diff --check` passed. The client is exercised in dry-run mode only. Host-side `visudo` validation, installed-file permission checks, live Compose label verification, and runtime status/restart verification remain pending because installation is explicitly out of scope.

The repository `.gitignore` now excludes Python caches/virtual environments, `.env` files, `secrets/`, and planned `ops/runtime-env/` and `ops/approvals/` state; `.env.example` remains trackable. `git check-ignore` verified these rules without opening any environment files.

The one-time root-only bootstrap is [scripts/install-homelab-ops.sh](../scripts/install-homelab-ops.sh). Its local validation is limited to shell syntax, embedded Python syntax, the non-root refusal path, and the existing 34-test gateway/project suite; it has not been executed against a Debian host.

## Local development and testing

Run these commands from the repository root. Python 3 is the only requirement; the gateway tests use the standard library and temporary directories, and mock Docker/SSH command execution.

Run the gateway regression suite:

```sh
python3 -m unittest discover -s tests -p 'test_homelab_ops_gateway.py' -v
```

Run all local tests, including the client and inventory tests:

```sh
python3 -m unittest discover -s tests -v
```

Print the client request without sending it over SSH:

```sh
python3 scripts/homelab-ops status
python3 scripts/homelab-ops restart jellyfin
```

These commands only show the SSH command that would be issued. The `--send` option is a remote operation: it contacts `home-server-agent` and invokes the installed gateway on `home-server-01`. It is not needed for local testing. Status is read-only; `--send restart jellyfin` can restart Jellyfin only if the server has a valid administrator-created approval, so use it only as part of the approved restart procedure above.

The privileged gateway itself is designed to run as a protected root-owned installation on Debian, not directly from a developer checkout. Its behavior is exercised locally through mocked tests. The approval storage under `/var/lib/homelab-ops` and the server policy under `/etc/homelab-ops` are not created or modified by these local commands.

After the November 14 patch, the gateway-specific suite passed all 17 tests locally. On the server, the administrator confirmed successful status and restart outcomes in the `homelab-ops` journal. The restart at 19:19:47 followed a separately approved request; the 19:19:33 unapproved request was denied. These are the recorded runtime results; no new sudoers rule or installer run was performed.

See [the administrator installation checklist](homelab-ops-installation.md) for the original first-install procedure and [the Phase 3 policy-engine specification](../specs/phases/phase-03-policy-engine/spec.md) for the proposed next phase.
