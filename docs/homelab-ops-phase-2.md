# Homelab Operations Phase 2: status and Jellyfin restart

**Implementation state (2026-11-13):** Local gateway and mocked tests are implemented. Server installation is pending administrator action. No remote files, permissions, or containers were changed.

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

See [the administrator installation checklist](homelab-ops-installation.md) for protected staging requirements, the exact administrator invocation, sudoers policy, live-identity preflight, first safe test, approved restart procedure, and uninstall instructions. No server-side installation or restart has been performed.
