# `homelab-ops` Phase 2 administrator installation checklist

**Status:** Local implementation and tests are ready for review. Nothing has been installed or executed on the server. Installation requires an authorized administrator; `agent` cannot write privileged locations and must not gain Docker or general sudo access.

## Scope and privilege boundary

The root-owned gateway supports only:

- `status`, which calls `/usr/local/sbin/homelab-inventory` with no arguments.
- `restart jellyfin`, which consumes an administrator-created, one-use approval, verifies the live container's name, image, running state, and Compose project/service labels against a separate root-owned policy, then restarts that verified container ID.

The Phase 1 inventory observed `/jellyfin` running and healthy with image `jellyfin/jellyfin:latest`. It did not expose Compose labels or a stable container ID. Therefore the proposed values in `infra/policy/server-policy.json` are not live-verified: an administrator must verify the current identity and Compose ownership in the preflight below, then update the policy snapshot if needed before transfer. Deploy, rollback, other service names, arbitrary Docker commands, host reboot, and caller-supplied arguments are rejected.

The gateway and approval helper are root-owned and executable only by root. A separate exact sudoers allowlist lets `agent` invoke only the two gateway argument strings. The approval directory is root-owned mode `0700`; approval records are root-owned mode `0600`. `agent` cannot run the approval helper through sudo, create or edit approval files, or access the Docker socket directly.

## Administrator preflight

From an authorized administrator session, confirm:

1. The target is `home-server-01`, Debian 13, and `/usr/bin/python3`, `/usr/bin/docker`, and `/usr/local/sbin/homelab-inventory` exist.
2. `/usr/local/sbin/homelab-inventory` is a trusted root-owned regular executable with mode `0755`; `/usr/bin/docker` is root-owned and not writable by `agent`.
3. Inspect the live Jellyfin identity and ownership using the administrator's Docker access. Confirm output matches the policy's container name, image, Compose project, Compose service, and `running` state:

   ```sh
   sudo /usr/bin/docker container inspect --format '{{.Id}}|{{.Name}}|{{.Config.Image}}|{{index .Config.Labels "com.docker.compose.project"}}|{{index .Config.Labels "com.docker.compose.service"}}|{{.State.Status}}' jellyfin
   ```

   Compare the values with `infra/policy/server-policy.json`. Edit that local proposed policy before review/transfer if the live values differ. Stop if the Compose ownership labels are missing or unexpected. The gateway rechecks these fields at every restart and uses the verified full container ID, avoiding a name-only restart target.
4. `id agent` has no `docker` or `sudo` group membership. Inspect `sudo -l -U agent`; remove/resolve any broad preexisting authority through a separate admin change before continuing.
5. The exact destination files, `/etc/homelab-ops`, and `/var/lib/homelab-ops` do not already exist. If any exist, stop and inspect/backup them; do not overwrite or chmod unknown policy/state.
6. Review the gateway, shared module, approval helper, server policy, bootstrap installer, and tests against this document.

No environment files, credentials, or Compose files are part of this installation.

## Install files and protected approval storage

Using the administrator's trusted transfer route, place exactly these reviewed files in `/root/homelab-ops-phase2/`: `install-homelab-ops.sh`, `homelab-ops-gateway`, `homelab_ops_common.py`, `homelab-ops-approve-restart`, and `server-policy.json`. The directory must be `root:root 0700`; the installer must be `root:root 0700`; the other source files must be `root:root 0600`. The installer rejects symlinks, non-root ownership, hard-linked files, group/world-accessible source files, and unsafe parent paths. Do not use an `agent`-writable path as privileged input.

On the local reviewed checkout, obtain expected hashes with:

```sh
shasum -a 256 scripts/install-homelab-ops.sh scripts/homelab-ops-gateway scripts/homelab_ops_common.py scripts/homelab-ops-approve-restart infra/policy/server-policy.json
```

The installer prints target-side hashes for all five files before making changes. Compare them byte-for-byte with these local values and stop on any mismatch. Then the administrator runs the installer from the protected staging directory:

```sh
sudo /root/homelab-ops-phase2/install-homelab-ops.sh
```

Run that command from the administrator's `ravindu` account on `home-server-01`. After it prints the five protected source hashes, compare them with the local reviewed hashes and type `INSTALL` at its prompt. The installer requires root, accepts no arguments, revalidates the protected source and destination paths, verifies the live Jellyfin mapping, requires the current inventory sudoers rule to remain present and valid, and refuses to overwrite any existing destination. On a failed step its exit handler removes only paths created by that run and disables the new sudoers entry first. If cleanup reports incomplete, stop and inspect those exact paths as administrator.

The local server policy is a proposal independent of the client `infra/policy/allowlist.json`. Install it as `/etc/homelab-ops/gateway-policy.json` (`root:root 0640`). The gateway checks its own file (`root:root 0750`), shared module (`root:root 0640`), policy, inventory wrapper (`root:root 0755`), and every parent path for root ownership, non-symlink components, and no group/world write permission. The approval helper checks its executable and shared module before creating an approval.

## Exact sudoers policy

The installer creates `/etc/sudoers.d/homelab-ops` with exactly this rule. It first validates a root-owned mode `0440` hidden candidate with `visudo -cf`, then publishes it atomically and validates the full sudoers configuration. It does not modify `/etc/sudoers.d/homelab-inventory`:

```sudoers
Cmnd_Alias HOMELAB_OPS_PHASE2 = /usr/local/sbin/homelab-ops status, /usr/local/sbin/homelab-ops restart jellyfin
agent ALL=(root) NOPASSWD: HOMELAB_OPS_PHASE2
```

After installation, verify the include and both rules:

```sh
sudo stat -c '%U:%G %a %n' /etc/sudoers.d/homelab-ops /etc/sudoers.d/homelab-inventory
sudo visudo -cf /etc/sudoers.d/homelab-ops
sudo visudo -c
sudo -l -U agent
```

The two command specifications include exact arguments and no wildcards. Do not add `SETENV`, `/usr/bin/docker`, a shell, the approval helper, or a broader command alias. If sudo reports a broader preexisting grant, stop; this policy does not revoke it.

In sudoers, specified command-line arguments must match the request; omitting arguments can allow arbitrary arguments. Confirm the installed sudo version's behavior with its [`sudoers(5)` reference](https://manpages.debian.org/testing/sudo/sudoers.5.en.html) and validate on the host with `visudo` before enabling the rule.

## First safe verification

The first post-install request must be read-only status:

```sh
scripts/homelab-ops --send status
```

Confirm the inventory output is returned, and review the `homelab-ops` authpriv journal records. Verify as `agent` that direct `docker ps`, `sudo -n /usr/bin/docker ps`, `sudo -n /bin/sh`, `sudo -n /usr/local/sbin/homelab-ops restart pihole`, and requests with extra arguments are denied. These negative checks must not affect containers.

Verify an unapproved restart is denied and does not invoke Docker:

```sh
scripts/homelab-ops --send restart jellyfin
```

Expected result: nonzero denial (`77` from the gateway) and an approval-denied journal record. The local mocked tests additionally verify that missing/expired approvals and reused approvals do not invoke Docker.

## Approved restart procedure

Restarting Jellyfin can interrupt media sessions. Each restart requires a separate explicit administrator approval:

1. The administrator confirms the exact service and timing with the owner.
2. Immediately before the authorized request, the administrator runs `sudo /usr/local/sbin/homelab-ops-approve-restart`. This creates one root-owned `0600` record bound to operation `restart`, service `jellyfin`, requester `agent`, a random nonce, and a 120-second expiry. An existing pending record is never overwritten.
3. The requester runs `scripts/homelab-ops --send restart jellyfin` before expiry.
4. The gateway validates the approval and atomically renames it from `pending/` into `consumed/` before executing Docker. Concurrent/repeated requests cannot consume it twice. Failure or timeout also consumes the approval; issue a fresh approval only after reviewing the outcome.
5. Check status and Jellyfin availability after the restart. A timeout can leave the operation outcome uncertain; inspect state before requesting anything again.

The approval helper is not in the agent sudoers policy. Only an administrator can create the pending approval.

## Logs and failure behavior

The gateway logs caller, fixed operation/service, and result to syslog `authpriv` under tag `homelab-ops`; the helper logs approval creation. It does not log approval contents, environment, command output from Docker, or secrets. The inventory wrapper emits its documented selected metadata to the requesting terminal.

Status is capped at 185 seconds (the inventory wrapper's own maximum is 180 seconds). Restart is capped at 35 seconds and uses Docker's fixed 10-second stop grace. Malformed input exits `64`, authorization/approval denial exits `77`, timeout exits `124`, and Docker/inventory failures return nonzero. An approval is consumed before Docker execution, including on command failure or timeout.

## Recovery if installation validation fails

Do not enable the sudoers include until the root-owned files and server policy pass the documented ownership, mode, hash, and syntax checks. If the new sudoers rule was added and any subsequent validation fails, disable only that new include, then validate sudoers and confirm the administrator session still has its normal access:

```sh
sudo rm -- /etc/sudoers.d/homelab-ops
sudo visudo -c
sudo -l -U agent
```

After confirming the include is absent, remove only the newly installed gateway/helper/module/policy files. Preserve any preexisting paths or approval state for administrator inspection. Do not modify the existing inventory sudoers rule, Docker membership/socket permissions, or containers as part of recovery.

## Uninstall

1. Disable the sudoers rule first: inspect the exact file, then remove only `/etc/sudoers.d/homelab-ops` as administrator and run `visudo -c`. Do not edit the existing inventory rule.
2. Confirm `sudo -l -U agent` no longer lists the Phase 2 gateway and that no request can reach it.
3. Remove the installed gateway, approval helper, shared module, and policy only after the sudoers rule is disabled:

   ```sh
   sudo rm -- /usr/local/sbin/homelab-ops
   sudo rm -- /usr/local/sbin/homelab-ops-approve-restart
   sudo rm -- /usr/local/sbin/homelab_ops_common.py
   sudo rm -- /etc/homelab-ops/gateway-policy.json
   ```

4. Preserve `consumed/` records for the administrator's chosen audit-retention period. Let any pending approval expire or remove it manually as administrator after confirming uninstall; never grant `agent` directory access. Remove the approval directories only when empty and when retained records have been archived according to the owner's retention policy.
5. Confirm `agent` remains outside Docker and sudo groups and Docker socket permissions are unchanged.
6. Remove `/etc/homelab-ops` only if empty and no other administrator policy uses it. Preserve approval state according to the chosen audit-retention policy.

No container restart is part of installation, verification, or uninstall. The only restart occurs later through the separately approved one-time procedure above.
