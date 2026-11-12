# Read-only Docker inventory security design

## Goal and current limitation

The 2026-11-12 audit found Docker running but denied `agent` access to `/var/run/docker.sock`. The proposed mechanism lets `agent` request one fixed, read-only inventory operation through sudo. It does not grant Docker API access, membership in the `docker` group, or general root access.

This design is for review only. No host changes have been made.

## Trust boundaries

- The root-owned executable is installed at `/usr/local/sbin/homelab-inventory`, owned by `root:root`, mode `0755`; parent directories must not be writable by `agent` or other untrusted users.
- The sudoers drop-in allows exactly that absolute path with **no command-line arguments**. It has no wildcard, command alias granting other commands, shell, editor, or Docker CLI entry.
- The script rejects caller arguments itself, then starts a clean worker under `/usr/bin/timeout` with a 180-second overall deadline. Every Docker CLI call has a separate 15-second timeout; GNU `timeout` returns nonzero on expiration (normally 124).
- It ignores caller-controlled environment variables for Docker calls, uses absolute executable paths, selects the Docker Unix socket explicitly, and invokes only fixed Docker subcommands and format strings.
- Container IDs come from `docker container ls --all --quiet --no-trunc` and are checked as exactly 64 lowercase hexadecimal characters before being used as the final operand to the fixed `docker inspect --type container` command.
- The list command requests at most 101 newest container IDs. The script validates all returned IDs, inspects at most 100, and reports to stderr when the sentinel ID indicates truncation. This bounds list memory and per-container processing; the 180-second overall timeout also bounds worst-case elapsed time.
- ID validation and inspection use shell here-documents rather than a pipeline. This keeps the loop in the current shell, so `set -e` propagates failed inspect commands instead of reporting the final pipeline stage's status.
- Docker access is effectively root-equivalent for anyone who can invoke a general Docker client. Here, the root wrapper narrows that access to a fixed read operation. The Docker daemon and root remain trusted components.

## Data allowlist

The script emits only:

- Container ID, name, configured image reference, state, health state (or JSON `null` if Docker omits health information), and restart policy.
- Published port bindings from `NetworkSettings.Ports`.
- Docker network names attached to the container.
- Mount destination inside the container, mount type, and read/write flag.

Values are encoded with Docker's Go-template `json` formatter where scalar values are emitted. Treat all output as untrusted inventory data, not instructions; names, image references, and other metadata may be user-controlled.

The health field is accessed using Go-template `index` on `.State` rather than direct `.State.Health` selection. Docker may omit the `Health` key entirely when a container has no configured health check; in that case the script emits `null` without failing template evaluation.

## Deliberately excluded data

The inspect template does not select or print:

- Container environment (`Config.Env`), labels, command, entrypoint, health-check output, logs, or process listings.
- Host mount source paths, volume names, bind paths, or any file contents.
- Secret objects, credential files, Docker configuration, daemon configuration, or environment files.
- Network endpoint IP addresses, MAC addresses, gateway data, or DNS configuration.

This means the inventory cannot safely answer which host directories or named volumes back a container, whether a secret is mounted, what credentials an application uses, whether its process is healthy beyond Docker's reported state, or the container's internal IP/network endpoint details. It also does not enumerate networks or volumes that have no attached running or stopped container. Container/image names and image references can themselves reveal operational details; if those are considered sensitive, this inventory should not be used or should be further reduced.

## Sudoers allowlist

Install as `/etc/sudoers.d/homelab-inventory`, owned by `root:root`, mode `0440`, with this exact rule:

```sudoers
agent ALL=(root) NOPASSWD: /usr/local/sbin/homelab-inventory ""
```

In sudoers, `""` means the command is permitted only with no arguments. Do not omit it: a command specification without an argument string can permit arbitrary arguments. Do not add `SETENV`, shell access, `/usr/bin/docker`, or a broader command alias. `visudo -cf /etc/sudoers.d/homelab-inventory` must pass before the drop-in is enabled/accepted.

## Security properties and residual risks

- The `agent` account still cannot directly open the Docker socket. Do not add it to group `docker`.
- The wrapper script and all parent directories must remain root-owned and not writable by `agent`; otherwise the sudo rule becomes a root compromise.
- Output volume scales with container count and may include container names, image references, port mappings, mount destinations, and service topology. Store or transmit output accordingly.
- A Docker daemon compromise, malicious/buggy daemon response, or future change to the wrapper/template could invalidate assumptions. Review changes to this allowlist as privileged-code changes.
- Timeouts can interrupt an inventory and leave partial records on stdout; callers must treat any nonzero exit as an incomplete result and discard or label the output accordingly. The overall limit bounds runtime but does not guarantee a complete inventory under slow daemon responses.
- Sudo logging policy should record invocation. The wrapper intentionally prints no environment or secrets; stdout may still be captured by the caller.
- Fixed inventory commands are read-only Docker API operations. The wrapper must never accept a Docker subcommand, template, format string, socket path, or arbitrary option from its caller.

## Review checklist before deployment

1. Confirm `/usr/bin/docker` and `/usr/bin/env` are the intended root-owned system executables and the daemon socket is `/var/run/docker.sock` on the current server.
2. Review the script and exact sudoers line as a pair; confirm sudo version accepts the no-argument `""` form.
3. Confirm `agent` is not in the Docker group and has no preexisting broader sudo grant that defeats this restriction.
4. Confirm the selected fields meet the intended visibility need and that metadata exposure is acceptable.
5. Run the local mocked tests with `python3 -m unittest discover -s tests -v`, then run the deployment validation and negative security tests in `docs/docker-inventory-installation.md` as part of an explicitly approved deployment.
