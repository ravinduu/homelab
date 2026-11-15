# Phase 3 policy engine: local and server canary development test

**Purpose:** Validate schema 2 policy code in unit tests and, after separate
administrator review, exercise it in the already installed canary namespace.
This procedure does not update the production gateway. It does not authorize a
restart or other production change.

## Local checks

From the repository root:

```sh
python3 -m unittest discover -s tests -v
sh -n scripts/install-homelab-ops-canary.sh
git diff --check
```

The suite covers schema validation, unknown principals/operations/resources,
exact scope, role composition, explicit-deny precedence, required approval,
schema 1 decision migration, and gateway no-execution on denial. The canary
first-install script validates the reviewed schema 2 baseline and installs
only its namespace.

## Server canary update boundary

The existing `install-homelab-ops-canary.sh` is first-install-only and refuses
the canary paths already present on `home-server-01`. Do not rerun it and do
not copy files over the active gateway while its sudoers rule is enabled.
The Phase 3 update below requires an administrator to approve and perform a
canary-only maintenance window. `agent` receives no new privilege. Keep the
original gateway, policy, approval data, and sudoers entry untouched.

The canary status request is read-only. The deny test swaps only the canary
policy to [`dev-deny-status.json`](../../infra/policy/dev-deny-status.json),
which denies status without invoking inventory. Do not use restart for
development testing: it points to live Jellyfin and requires separate impact
review and explicit approval.

### 1. Prepare reviewed files and hashes locally

Run the local checks above, review `git diff`, and calculate hashes for the
canary launcher, changed package modules, both policies, and the approval
helper:

```sh
shasum -a 256 \
  packaging/entrypoints/homelab-ops-canary \
  packaging/entrypoints/homelab-ops-approve-restart-canary \
  src/homelab_ops/gateway/core.py \
  src/homelab_ops/gateway/policy.py \
  infra/policy/server-policy.json \
  infra/policy/dev-deny-status.json
```

Transfer those files to the authorized `agent` upload area as described in
the [canary installation guide](homelab-ops-canary.md). An administrator must
copy the currently installed package into a new root-owned mode-0700 staging
directory, then replace staged `gateway/core.py` and add `gateway/policy.py`
from the reviewed upload. Stage the new canary wrapper and both policy files
from that same upload. Use unchanged installed approval modules as the
baseline; compare hashes for every uploaded file and stop on any mismatch.
Do not use the old first-install staging directory as an update mechanism.

For this update, the transfer commands are:

```sh
scp packaging/entrypoints/homelab-ops-canary home-server-agent:/home/agent/homelab-ops-canary-upload/homelab-ops-canary
scp src/homelab_ops/gateway/core.py home-server-agent:/home/agent/homelab-ops-canary-upload/core.py
scp src/homelab_ops/gateway/policy.py home-server-agent:/home/agent/homelab-ops-canary-upload/policy.py
scp infra/policy/server-policy.json home-server-agent:/home/agent/homelab-ops-canary-upload/server-policy.json
scp infra/policy/dev-deny-status.json home-server-agent:/home/agent/homelab-ops-canary-upload/dev-deny-status.json
```

After the files have been transferred to the documented agent upload
directory, the administrator prepares the protected staging tree:

```sh
sudo install -d -o root -g root -m 0700 /root/homelab-ops-phase3
sudo cp -a /usr/local/lib/homelab-ops-canary/homelab_ops /root/homelab-ops-phase3/
sudo install -o root -g root -m 0600 /home/agent/homelab-ops-canary-upload/homelab-ops-canary /root/homelab-ops-phase3/homelab-ops-canary
sudo install -o root -g root -m 0600 /home/agent/homelab-ops-canary-upload/core.py /root/homelab-ops-phase3/homelab_ops/gateway/core.py
sudo install -o root -g root -m 0600 /home/agent/homelab-ops-canary-upload/policy.py /root/homelab-ops-phase3/homelab_ops/gateway/policy.py
sudo install -o root -g root -m 0600 /home/agent/homelab-ops-canary-upload/server-policy.json /root/homelab-ops-phase3/server-policy.json
sudo install -o root -g root -m 0600 /home/agent/homelab-ops-canary-upload/dev-deny-status.json /root/homelab-ops-phase3/dev-deny-status.json
```

Upload the files under those names and verify the staged tree and hashes before
continuing. The wrapper expects `gateway/policy.py` in its fixed package list.

### 2. Back up and temporarily disable only the canary request rule

The administrator confirms no canary operation is in progress, backs up the
current canary launcher, package, policy, and exact sudoers include, and
records hashes and modes. Verify the saved sudoers file contains only the
expected canary alias and `agent` rule. Then disable only that include and
verify `visudo` succeeds and `agent` no longer has canary access:

```sh
sudo install -d -o root -g root -m 0700 /root/homelab-ops-phase3-backup
sudo cp -a /usr/local/sbin/homelab-ops-canary /root/homelab-ops-phase3-backup/
sudo cp -a /usr/local/lib/homelab-ops-canary/homelab_ops /root/homelab-ops-phase3-backup/
sudo cp -a /etc/homelab-ops-canary/gateway-policy.json /root/homelab-ops-phase3-backup/
sudo cp -a /etc/sudoers.d/homelab-ops-canary /root/homelab-ops-phase3-backup/
sudo sha256sum /usr/local/sbin/homelab-ops-canary /usr/local/lib/homelab-ops-canary/homelab_ops/gateway/core.py /etc/homelab-ops-canary/gateway-policy.json /etc/sudoers.d/homelab-ops-canary
sudo rm -- /etc/sudoers.d/homelab-ops-canary
sudo visudo -c
sudo -l -U agent
```

Stop if the include differs from the expected canary-only rule or if any
unrelated sudoers validation fails.

### 3. Install the reviewed Phase 3 canary files

With canary access disabled, the administrator replaces the launcher and
these root-owned mode-0640 modules under
`/usr/local/lib/homelab-ops-canary/homelab_ops/`:

- `gateway/core.py`
- `gateway/policy.py`

The existing canary wrapper must also include `gateway/policy.py` in its
fixed package file list, so install the reviewed
`packaging/entrypoints/homelab-ops-canary` as root:root mode 0750. Install
`infra/policy/server-policy.json` as root:root mode 0640 at
`/etc/homelab-ops-canary/gateway-policy.json`. Keep the approver, approval
directories, existing production gateway, and production policy unchanged.
Recheck ownership, modes, links, and hashes against the locally reviewed
values. Restore the saved canary sudoers include as root:root mode 0440 and
run `sudo visudo -c` before testing.

For the protected staging directory `/root/homelab-ops-phase3`, the reviewed
file replacement commands are:

```sh
sudo install -o root -g root -m 0750 /root/homelab-ops-phase3/homelab-ops-canary /usr/local/sbin/homelab-ops-canary
sudo install -o root -g root -m 0640 /root/homelab-ops-phase3/homelab_ops/gateway/core.py /usr/local/lib/homelab-ops-canary/homelab_ops/gateway/core.py
sudo install -o root -g root -m 0640 /root/homelab-ops-phase3/homelab_ops/gateway/policy.py /usr/local/lib/homelab-ops-canary/homelab_ops/gateway/policy.py
sudo install -o root -g root -m 0640 /root/homelab-ops-phase3/server-policy.json /etc/homelab-ops-canary/gateway-policy.json
sudo sha256sum /usr/local/sbin/homelab-ops-canary /usr/local/lib/homelab-ops-canary/homelab_ops/gateway/core.py /usr/local/lib/homelab-ops-canary/homelab_ops/gateway/policy.py /etc/homelab-ops-canary/gateway-policy.json
sudo install -o root -g root -m 0440 /root/homelab-ops-phase3-backup/homelab-ops-canary /etc/sudoers.d/homelab-ops-canary
sudo visudo -c
```

Confirm the installed wrapper lists `gateway/policy.py` before restoring
canary authorization. If installation or validation fails, leave authorization
disabled and restore the saved canary files:

```sh
sudo install -o root -g root -m 0750 /root/homelab-ops-phase3-backup/homelab-ops-canary /usr/local/sbin/homelab-ops-canary
sudo cp -a /root/homelab-ops-phase3-backup/homelab_ops/. /usr/local/lib/homelab-ops-canary/homelab_ops/
sudo install -o root -g root -m 0640 /root/homelab-ops-phase3-backup/gateway-policy.json /etc/homelab-ops-canary/gateway-policy.json
sudo sha256sum /usr/local/sbin/homelab-ops-canary /usr/local/lib/homelab-ops-canary/homelab_ops/gateway/core.py /etc/homelab-ops-canary/gateway-policy.json
sudo install -o root -g root -m 0440 /root/homelab-ops-phase3-backup/homelab-ops-canary /etc/sudoers.d/homelab-ops-canary
sudo visudo -c
```

Never roll back the production gateway as part of this canary procedure.

### 4. Verify allowed status and a policy denial

From the operator machine, inspect the request first, then run read-only
status:

```sh
scripts/homelab-ops-canary status
scripts/homelab-ops-canary --send status
```

Confirm inventory is returned and the journal contains a canary decision with
principal `unix:agent`, revision `phase3-canary-1`, and reason `allowed`.
The administrator can inspect recent events with:

```sh
sudo journalctl -t homelab-ops-canary -n 50 --no-pager
```

Use the administrator session to install the staged
`dev-deny-status.json` at the canary policy path with root:root mode 0640. Then
run:

```sh
scripts/homelab-ops-canary --send status
```

It must exit nonzero without inventory output. Confirm the canary journal
records revision `phase3-deny-status-test` and reason `explicit_deny`. Restore
the reviewed baseline policy and verify recovery:

```sh
sudo install -o root -g root -m 0640 /root/homelab-ops-phase3/server-policy.json /etc/homelab-ops-canary/gateway-policy.json
sudo sha256sum /etc/homelab-ops-canary/gateway-policy.json
scripts/homelab-ops-canary --send status
```

The test policy remains root-controlled throughout. Do not grant `agent` write
access to the policy path or approval state. If the policy is not restored or
status does not recover, disable only the canary sudoers rule and restore the
backed-up canary policy before further investigation.

## Evidence to record

Record the reviewed source revision, local and staged hashes, installed file
owners/modes, `visudo -c` result, canary status result, deny-test exit and
journal reason, restored policy hash, and final status result. Distinguish
these canary results from production gateway evidence. No Jellyfin restart is
needed to verify Phase 3 policy evaluation.
