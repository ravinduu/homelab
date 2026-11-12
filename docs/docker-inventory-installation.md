# Docker inventory installation and rollback plan

## Status

Implementation approved; privileged host installation remains pending manual administrator action. No remote files have been changed. The planned changes install one root-owned inventory script and one exact sudoers rule; they do not change Docker configuration, containers, volumes, media, networking, or SSH settings.

## Preconditions

1. Connect only with `ssh home-server-agent`, as `agent`; verify hostname and OS before applying anything.
2. Confirm `/usr/bin/docker`, `/usr/bin/env`, `/usr/bin/timeout` (GNU coreutils), `/bin/sh`, `/var/run/docker.sock`, sudo, and `visudo` locations and versions. The audited agent account could not access the Docker socket; do not test by using `sudo docker` or changing group membership.
3. Inspect `id agent` and `sudo -l -U agent` from an authorized administrative session. Confirm the proposed permission does not conflict with an existing broad grant. If broad sudo is already granted, this wrapper cannot remove that separate authority; stop and report it.
4. Confirm `/usr/local/sbin` is root-owned and not writable by `agent`; confirm no existing script or sudoers drop-in at the destination. Never overwrite an existing file without separately reviewing and explicitly approving the replacement.
5. Agree on the exposed metadata. The script omits environment variables, labels, commands, logs, health-check output, mount source paths, and file contents; it does reveal container names, image references, lifecycle state, published ports, network names, and mount destinations/type/read-write status.

## Installation procedure (for a separately approved deployment)

1. Preserve a secure copy of any preexisting sudoers policy if one is being intentionally replaced. Prefer stopping if either destination already exists. Do not back up secrets into this repository.
2. Transfer the reviewed `scripts/homelab-inventory` to a staging location that `agent` cannot use to replace the final privileged file during installation.
3. As an authorized administrator with the required narrow administrative access, install the reviewed file at `/usr/local/sbin/homelab-inventory` with owner `root:root`, mode `0755`. Do not install it through a path writable by `agent` or leave a writable staging file referenced by sudoers.
4. Create `/etc/sudoers.d/homelab-inventory` with owner `root:root`, mode `0440`, containing exactly:

   ```sudoers
   agent ALL=(root) NOPASSWD: /usr/local/sbin/homelab-inventory ""
   ```

   The `""` argument match allows only an invocation without arguments. Do not grant sudo permission to Docker itself or a shell.

5. Validate the proposed policy with `visudo -cf /etc/sudoers.d/homelab-inventory` and the full policy with `visudo -c`. Stop immediately on any parse error; do not weaken or bypass validation.
6. Verify owner, group, mode, and non-writable parent directories for the executable and sudoers file. Confirm `id agent` still shows no Docker group membership.
7. From `agent`, run `sudo -n /usr/local/sbin/homelab-inventory` and review the output for the documented allowlist only. Each Docker CLI call is capped at 15 seconds; the whole inventory is capped at 180 seconds. The list request is bounded to 101 newest IDs, with at most 100 inspected. This command reads Docker metadata and does not alter containers.

## Validation and security tests

Run the local mocked regression suite before deployment with `python3 -m unittest discover -s tests -v`. It covers containers with and without health checks (health emits the Docker health status or `null`), invalid IDs, list and inspect failures, per-command and overall timeouts, the 100-container cap and truncation message, fixed command arguments, and caller argument rejection. The 10 tests do not connect to Docker or the server.

After installation, run the following checks without changing Docker or host access controls:

1. **Policy syntax:** `visudo -cf /etc/sudoers.d/homelab-inventory` and `visudo -c` both succeed.
2. **Positive path:** as `agent`, `sudo -n /usr/local/sbin/homelab-inventory` succeeds and returns container inventory (or the explicit no-containers message). If the result reports truncation, it represents the 100 newest containers, not a complete host inventory.
3. **No arguments:** as `agent`, `sudo -n /usr/local/sbin/homelab-inventory --help` is rejected by sudo policy. If invoked directly as root in an isolated validation, the script itself must exit 64 on any argument.
4. **No arbitrary commands:** as `agent`, `sudo -n /usr/bin/docker ps` and `sudo -n /bin/sh` remain denied unless independently authorized by a preexisting policy; investigate any success as a preexisting broader sudo grant, not as part of this design.
5. **Direct socket denied:** as `agent`, an ordinary `docker ps` remains denied. Do not use sudo for this check and do not change group membership.
6. **No sensitive fields:** review output and confirm it contains no environment values, labels, commands, host mount source paths, volume names, health-check output, or file contents. Compare the fields to the allowlist in `docs/docker-inventory-security.md`.
7. **Filesystem protections:** verify `stat` shows root ownership and expected modes and that `agent` cannot write to the script or its parent directories.
8. **Read-only behavior:** compare container state before and after; no lifecycle, network, volume, configuration, or data operation should have occurred. The script makes only list and inspect API calls.
9. **Timeout and error handling:** confirm a timed out run exits nonzero (GNU `timeout` status 124) and any nonzero Docker list/inspect result exits nonzero. Treat all partial stdout from a failed run as incomplete.

If any test fails or output contains an unapproved field, stop using the wrapper and follow rollback. Do not improvise a broader grant.

## Rollback

1. If the wrapper behaves unexpectedly, remove only `/etc/sudoers.d/homelab-inventory` using an approved administrative change, then confirm `visudo -c` succeeds and `agent` can no longer invoke the wrapper through sudo.
2. Remove `/usr/local/sbin/homelab-inventory` only if it is the exact file installed by this change and no other approved workflow depends on it. If preservation is needed for review, move it to an administrator-controlled, root-only location outside any executable or sudo-included path.
3. Restore a pre-install version only if one existed and its restoration was explicitly included in deployment approval. Never overwrite unrelated policy files.
4. Recheck `sudo -l -U agent`, the sudoers parse, file ownership/modes, and Docker socket denial. No daemon restart is required.
5. Record the rollback result and reason. Do not modify Docker group membership, socket permissions, firewall rules, or daemon settings as part of rollback.

## Execution boundary

The assistant is restricted to the `agent` SSH account and must stop at administrator-only operations. The commands in the current deployment checkpoint are for the user to review and run manually. After the administrator confirms installation, the assistant may connect again as `agent` to run only the listed positive and negative checks and document their actual results.

## Current deployment checkpoint (2026-11-12)

Preflight was performed over `ssh home-server-agent` as `agent`; no remote files were changed.

- Verified host: `home-server-01`.
- `agent` is a member of `agent` and `users`; it is not in `docker` or `sudo` groups.
- `/usr/bin/docker` and `/usr/bin/timeout` exist. `/usr/local/sbin` and `/etc/sudoers.d` are `root:root`, mode `0755`.
- `/usr/local/sbin/homelab-inventory` and `/etc/sudoers.d/homelab-inventory` were absent at inspection.
- `sudo -n -l` could not list effective sudo policy because a password was required. No password was requested or entered. The current existence of any separately granted sudo rule therefore needs administrator review.
- `visudo` was not found in the `agent` account's current `PATH`; its absolute path has not been verified. On Debian it is commonly `/usr/sbin/visudo`; the administrator must confirm that path before using the commands below.
- Local shell syntax validation and all 9 mocked regression tests passed after the missing-health fix. These checks do not validate the remote sudoers parser or installed runtime.

The script SHA-256 to verify after transfer is (recompute after any further edit):

```text
708c2c419b6388da1630f079eef4f9731ed6cce83788715982e9f27a018788ec
```

## Administrator-run installation, if approved

The following operations require administrator privileges. They are presented for manual review and have **not** been run by the agent. Run them from an administrator session only after confirming the two final destinations and the candidate path are absent. Stop if any destination already exists or if the effective policy grants `agent` broader sudo rights.

1. From the local repository, transfer the script using the configured `agent` SSH alias:

   ```sh
   scp scripts/homelab-inventory home-server-agent:/tmp/homelab-inventory.upload
   ```

2. In the administrator session on `home-server-01`, inspect the effective rights and verify the upload before using it:

   ```sh
   sudo -l -U agent
   sudo test ! -e /usr/local/sbin/homelab-inventory
   sudo test ! -e /etc/sudoers.d/homelab-inventory
   sudo test ! -e /etc/sudoers.d/.homelab-inventory.candidate
   sudo install -o root -g root -m 0600 /tmp/homelab-inventory.upload /root/homelab-inventory.candidate
   sudo sha256sum /root/homelab-inventory.candidate
   sudo /bin/sh -n /root/homelab-inventory.candidate
   ```

   The SHA-256 output must exactly match the value above. If `sudo -l -U agent` shows unrestricted or unrelated privileged commands for `agent`, stop; this narrow drop-in cannot countermand an existing broad grant. Do not add group membership.

3. Install the verified root-owned candidate, create the hidden sudoers candidate, then validate both the isolated candidate and the current active policy **before activation**:

   ```sh
   sudo install -o root -g root -m 0755 /root/homelab-inventory.candidate /usr/local/sbin/homelab-inventory
   printf '%s\n' 'agent ALL=(root) NOPASSWD: /usr/local/sbin/homelab-inventory ""' | sudo tee /etc/sudoers.d/.homelab-inventory.candidate >/dev/null
   sudo chown root:root /etc/sudoers.d/.homelab-inventory.candidate
   sudo chmod 0440 /etc/sudoers.d/.homelab-inventory.candidate
   sudo /usr/sbin/visudo -cf /etc/sudoers.d/.homelab-inventory.candidate
   sudo /usr/sbin/visudo -c
   ```

   If `/usr/sbin/visudo` does not exist, locate the installed `visudo` executable as administrator and substitute its verified absolute path. Stop on any validation error. The candidate name contains dots and is ignored by the standard sudoers `@includedir` scan; the explicit `-f` command validates it directly. Confirm the active sudoers policy includes `/etc/sudoers.d` before proceeding.

4. Activate the already validated policy with a hard link, which fails if the final name exists; validate the full policy again:

   ```sh
   sudo ln /etc/sudoers.d/.homelab-inventory.candidate /etc/sudoers.d/homelab-inventory
   sudo /usr/sbin/visudo -c
   sudo stat -c '%U:%G %a %n' /usr/local/sbin/homelab-inventory /etc/sudoers.d/homelab-inventory
   sudo sha256sum /usr/local/sbin/homelab-inventory
   sudo unlink /etc/sudoers.d/.homelab-inventory.candidate
   ```

   Expected ownership and modes are `root:root 755` for the executable and `root:root 440` for the sudoers rule. If full validation fails, remove only the newly created `/etc/sudoers.d/homelab-inventory`, rerun `visudo -c`, and stop. The Docker daemon does not need a restart.

Do not run the agent tests in the next section until this manual installation succeeds. Once the administrator confirms completion, the agent can verify the positive invocation and negative authorization cases through `ssh home-server-agent` without using sudo to inspect or bypass Docker permissions.
