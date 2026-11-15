# Install and verify the homelab-ops canary

**Purpose:** Try the new package on home-server-01 beside the installed
gateway. This runbook does not authorize the installation or any restart.
The canary installer is first-install-only and refuses existing canary paths.
It adds its own exact sudoers include and does not replace or edit the current
gateway, policy, approval state, or sudoers rule.

## Canary namespace and impact

The separate files use:

- /usr/local/sbin/homelab-ops-canary
- /usr/local/sbin/homelab-ops-approve-restart-canary
- /usr/local/lib/homelab-ops-canary/homelab_ops
- /etc/homelab-ops-canary
- /var/lib/homelab-ops-canary
- /etc/sudoers.d/homelab-ops-canary

The local client is scripts/homelab-ops-canary and defaults to dry-run.

Status calls the existing read-only inventory wrapper. Restart still targets
the production Jellyfin container, so it can briefly interrupt Jellyfin. Use
that operation only after separate explicit approval and impact review.

## Trial record — 2026-11-14

The canary was exercised on `home-server-01` during this session:

- The staged ten-file hashes shown by the installer matched the reviewed
  local hashes. The first installer invocation was cancelled because the
  confirmation entered was `INSTALL`, not the required `INSTALL CANARY`.
- A subsequent `scripts/homelab-ops-canary --send status` succeeded. The
  assistant also ran that read-only request successfully later in the session.
  This confirms the canary gateway was installed and its status operation was
  reachable; the final installer output and installed file modes were not
  captured here.
- The user then invoked `restart jellyfin` through the canary. The output
  showed Jellyfin running but health `starting` about six seconds after the
  restart. A later canary inventory showed Jellyfin `running` and `healthy`.
- The latest inventory contained 12 running containers and one exited
  `hello-world` test container. Grafana, cAdvisor, Pi-hole, and Jellyfin
  reported healthy; the other running containers had no health value in the
  inventory.
- A separate read-only `uptime` query reported the host up for 2 hours 47
  minutes, with load averages 0.67, 0.56, and 0.46. These are host values, not
  per-container runtimes.

The approved inventory does not include container start timestamps, so exact
runtime durations for Jellyfin or other containers remain unknown. The earlier
`Up 6 seconds` observation is only the post-restart snapshot. A suspended
`sudo install` job was also reported in the local Mac shell; it was not verified
as cleared. Inspect it with `jobs -l` locally and terminate that suspended job
if it remains; do not resume it.

The installer is first-install-only and refuses existing canary destinations.
No canary update or upgrade procedure is defined yet. Preserve the current
canary and use a separately reviewed update design before replacing its files.

## Prepare and review the local sources

From the repository root, run the local checks:

    python3 -m unittest discover -s tests -v
    sh -n scripts/install-homelab-ops-canary.sh

The canary installer stages exactly ten files: the installer, two canary
entrypoints, server policy, and six server package modules. It does not stage
the requester CLI. Calculate the local hashes:

    shasum -a 256       scripts/install-homelab-ops-canary.sh       packaging/entrypoints/homelab-ops-canary       packaging/entrypoints/homelab-ops-approve-restart-canary       infra/policy/server-policy.json       src/homelab_ops/__init__.py       src/homelab_ops/approvals/__init__.py       src/homelab_ops/approvals/store.py       src/homelab_ops/gateway/__init__.py       src/homelab_ops/gateway/core.py       src/homelab_ops/gateway/approval_cli.py

## Transfer and stage the files

Upload to a temporary directory owned by the authorized `agent` account. This
is only a transfer location; do not run the installer from there. From the
local repository root:

    ssh home-server-agent 'umask 077; mkdir -p /home/agent/homelab-ops-canary-upload/homelab_ops/approvals /home/agent/homelab-ops-canary-upload/homelab_ops/gateway'
    scp scripts/install-homelab-ops-canary.sh home-server-agent:/home/agent/homelab-ops-canary-upload/
    scp packaging/entrypoints/homelab-ops-canary home-server-agent:/home/agent/homelab-ops-canary-upload/
    scp packaging/entrypoints/homelab-ops-approve-restart-canary home-server-agent:/home/agent/homelab-ops-canary-upload/
    scp infra/policy/server-policy.json home-server-agent:/home/agent/homelab-ops-canary-upload/
    scp src/homelab_ops/__init__.py home-server-agent:/home/agent/homelab-ops-canary-upload/homelab_ops/
    scp src/homelab_ops/approvals/__init__.py home-server-agent:/home/agent/homelab-ops-canary-upload/homelab_ops/approvals/
    scp src/homelab_ops/approvals/store.py home-server-agent:/home/agent/homelab-ops-canary-upload/homelab_ops/approvals/
    scp src/homelab_ops/gateway/__init__.py home-server-agent:/home/agent/homelab-ops-canary-upload/homelab_ops/gateway/
    scp src/homelab_ops/gateway/core.py home-server-agent:/home/agent/homelab-ops-canary-upload/homelab_ops/gateway/
    scp src/homelab_ops/gateway/approval_cli.py home-server-agent:/home/agent/homelab-ops-canary-upload/homelab_ops/gateway/

An administrator must then use their authorized server console/account to
copy the upload into a separate root-owned staging tree. Do not grant `agent`
sudo. First confirm `/root/homelab-ops-canary` does not already exist; stop if
it does. From an administrator-authorized server session, run the following
commands with `sudo` (the upload remains owned by `agent`; root reads it only
to copy into protected staging):

    sudo install -d -o root -g root -m 0700 /root/homelab-ops-canary
    sudo install -d -o root -g root -m 0700 /root/homelab-ops-canary/homelab_ops
    sudo install -d -o root -g root -m 0700 /root/homelab-ops-canary/homelab_ops/approvals /root/homelab-ops-canary/homelab_ops/gateway
    sudo install -o root -g root -m 0700 /home/agent/homelab-ops-canary-upload/install-homelab-ops-canary.sh /root/homelab-ops-canary/install-homelab-ops-canary.sh
    sudo install -o root -g root -m 0600 /home/agent/homelab-ops-canary-upload/homelab-ops-canary /root/homelab-ops-canary/homelab-ops-canary
    sudo install -o root -g root -m 0600 /home/agent/homelab-ops-canary-upload/homelab-ops-approve-restart-canary /root/homelab-ops-canary/homelab-ops-approve-restart-canary
    sudo install -o root -g root -m 0600 /home/agent/homelab-ops-canary-upload/server-policy.json /root/homelab-ops-canary/server-policy.json
    sudo install -o root -g root -m 0600 /home/agent/homelab-ops-canary-upload/homelab_ops/__init__.py /root/homelab-ops-canary/homelab_ops/__init__.py
    sudo install -o root -g root -m 0600 /home/agent/homelab-ops-canary-upload/homelab_ops/approvals/__init__.py /root/homelab-ops-canary/homelab_ops/approvals/__init__.py
    sudo install -o root -g root -m 0600 /home/agent/homelab-ops-canary-upload/homelab_ops/approvals/store.py /root/homelab-ops-canary/homelab_ops/approvals/store.py
    sudo install -o root -g root -m 0600 /home/agent/homelab-ops-canary-upload/homelab_ops/gateway/__init__.py /root/homelab-ops-canary/homelab_ops/gateway/__init__.py
    sudo install -o root -g root -m 0600 /home/agent/homelab-ops-canary-upload/homelab_ops/gateway/core.py /root/homelab-ops-canary/homelab_ops/gateway/core.py
    sudo install -o root -g root -m 0600 /home/agent/homelab-ops-canary-upload/homelab_ops/gateway/approval_cli.py /root/homelab-ops-canary/homelab_ops/gateway/approval_cli.py

Compare staged hashes with the local values before running the installer:

    sudo sha256sum /root/homelab-ops-canary/install-homelab-ops-canary.sh /root/homelab-ops-canary/homelab-ops-canary /root/homelab-ops-canary/homelab-ops-approve-restart-canary /root/homelab-ops-canary/server-policy.json /root/homelab-ops-canary/homelab_ops/__init__.py /root/homelab-ops-canary/homelab_ops/approvals/__init__.py /root/homelab-ops-canary/homelab_ops/approvals/store.py /root/homelab-ops-canary/homelab_ops/gateway/__init__.py /root/homelab-ops-canary/homelab_ops/gateway/core.py /root/homelab-ops-canary/homelab_ops/gateway/approval_cli.py

Stop on any mismatch. After the copy and comparison, remove the temporary
upload directory as `agent` or have the administrator remove it. The installer
uses only the protected root-owned stage and displays hashes again before
asking for confirmation. The staged files must have these paths:

    /root/homelab-ops-canary/install-homelab-ops-canary.sh
    /root/homelab-ops-canary/homelab-ops-canary
    /root/homelab-ops-canary/homelab-ops-approve-restart-canary
    /root/homelab-ops-canary/server-policy.json
    /root/homelab-ops-canary/homelab_ops/__init__.py
    /root/homelab-ops-canary/homelab_ops/approvals/__init__.py
    /root/homelab-ops-canary/homelab_ops/approvals/store.py
    /root/homelab-ops-canary/homelab_ops/gateway/__init__.py
    /root/homelab-ops-canary/homelab_ops/gateway/core.py
    /root/homelab-ops-canary/homelab_ops/gateway/approval_cli.py

The commands above set the stage and package directories to root:root 0700,
the installer to root:root 0700, and the other source files to root:root 0600.
The installer checks the exact file set, owners, modes, links, active inventory
rule, agent group membership, policy schema, and live Jellyfin identity. It
prints target-side hashes before changing anything. Compare all ten against
the local reviewed values and stop on any mismatch.

## Install the canary

Only after reviewing the proposed scope and confirming every canary
destination is absent, the administrator runs:

    sudo /root/homelab-ops-canary/install-homelab-ops-canary.sh

Compare the installer's ten hashes with the local values. Type the exact phrase
INSTALL CANARY only after they match. The installer validates the existing
sudoers config and live Jellyfin mapping, installs only canary paths, then
validates a separate exact-argument sudoers drop-in with visudo. If it fails,
cleanup removes only paths created by that run and disables only its own
sudoers entry first.

## Verify read-only behavior

First inspect the new access rule and canary file ownership:

    sudo visudo -c
    sudo -l -U agent
    sudo stat -c '%U:%G %a %n'       /usr/local/sbin/homelab-ops-canary       /usr/local/sbin/homelab-ops-approve-restart-canary       /etc/homelab-ops-canary/gateway-policy.json       /etc/sudoers.d/homelab-ops-canary

On the operator machine, inspect the dry-run request:

    scripts/homelab-ops-canary status

It must show /usr/local/sbin/homelab-ops-canary status. Then send the
read-only request:

    scripts/homelab-ops-canary --send status

Confirm the expected inventory output and canary-specific authpriv journal
records. The current gateway and its policy/state should remain unchanged.

## Optional restart test

This is a separate production Jellyfin restart. Review the expected brief
service interruption, current health, and dependent services first. After
explicitly approving that operation, the administrator creates a canary-only
one-use approval:

    sudo /usr/local/sbin/homelab-ops-approve-restart-canary

Within 120 seconds, send:

    scripts/homelab-ops-canary --send restart jellyfin

Verify Jellyfin health and dependent services. The approval is isolated from
the original gateway approval directory. This runbook is not approval to
perform the restart.

## Roll back the canary

As administrator, disable only the canary authorization first:

    sudo rm -- /etc/sudoers.d/homelab-ops-canary
    sudo visudo -c
    sudo -l -U agent

Confirm the canary request is denied. Then inspect and remove only the canary
entrypoints, package, and policy:

    sudo rm -- /usr/local/sbin/homelab-ops-canary
    sudo rm -- /usr/local/sbin/homelab-ops-approve-restart-canary
    sudo rm -r -- /usr/local/lib/homelab-ops-canary
    sudo rm -- /etc/homelab-ops-canary/gateway-policy.json
    sudo rmdir /etc/homelab-ops-canary

Preserve /var/lib/homelab-ops-canary until consumed approvals and audit
retention have been reviewed. Remove it only through a separate administrator
decision. Do not remove or change the current gateway files, package, policy,
approval state, or sudoers include.
