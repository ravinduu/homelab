# Homelab Infrastructure Management — Phase 1

**Prepared:** 2026-11-12 (Asia/Colombo)  
**Status:** Phase 1 local migration completed. Phase 2's gateway implementation is documented separately in [Phase 2](homelab-ops-phase-2.md). No remote files, permissions, or services were changed.

## Phase 1 outcome

Read-only SSH as `agent` confirmed four Compose projects under `/home/ravindu/Developer/homelab`: `arr`, `jellyfin`, `pi-hole`, and `monitoring`. Compose documents and the Prometheus scrape file were readable. `.env` files and credentials were not opened. The existing `/usr/local/sbin/homelab-inventory` approved wrapper succeeded and returns selected container metadata while intentionally omitting host mount source paths, volume names, environment, and labels.

The repository initially lacked local copies for ARR, Jellyfin, and Pi-hole. Sanitized snapshots have now been added for all four projects under `infra/compose/`. These are based on the files readable to `agent`, with protected values externalized; they are not yet approved deployment releases. The existing monitoring candidate under `proposed/monitoring/` remains a partial security proposal, not a complete representation of the current stack.

Read-only authorization inspection confirmed `agent` belongs to `agent`, `users`, and `homelab`, not `docker` or `sudo`; its only NOPASSWD sudo permission is the no-argument `/usr/local/sbin/homelab-inventory` command. `/usr/local/sbin` and `/etc/sudoers.d` are not writable by `agent`. Therefore server-side gateway installation is not available through the existing authorized account and was not attempted.

## Read-only Compose inventory

| Project | Services | Declared persistent paths / volumes | Networks and notable dependencies |
|---|---|---|---|
| ARR (`arr/docker-compose.yaml`) | qBittorrent, Prowlarr, Radarr, Sonarr, Unpackerr | `/var/lib/homelab/arr/<service>:/config`; `/mnt/media:/data` for qBittorrent, Radarr, Sonarr, Unpackerr | user-defined `arr-network` (`arr-network`); Unpackerr connects to Radarr and Sonarr by service DNS and references their API keys through environment interpolation. No `depends_on` was declared. |
| Jellyfin (`jellyfin/docker-compose.yml`) | Jellyfin | `/var/lib/homelab/jellyfin/config:/config`; `/var/lib/homelab/jellyfin/cache:/cache`; `/mnt/media/jellyfin-media:/media:ro` | Compose default network `jellyfin_default`; `/dev/dri/renderD128` device and numeric supplementary group `992` are declared. |
| Pi-hole (`pi-hole/docker-compose.yml`) | Pi-hole | `/mnt/old-hdd/docker/pihole/etc-pihole:/etc/pihole` | Host networking. Compose includes a web-password setting; its value is deliberately not reproduced here. |
| Monitoring (`monitoring/docker-compose.yaml`) | Prometheus, Grafana, node-exporter, cAdvisor, docker-health-exporter | Named volumes `prometheus_data`, `grafana_data`; read-only host mounts for node-exporter/cAdvisor and Prometheus/Grafana provisioning | `monitoring-network`; Grafana depends on Prometheus. cAdvisor is `privileged: true` and mounts `/var/run` read-only; exporter mounts Docker socket read-only, which does not filter API methods. Prometheus scrapes four targets on a 15-second interval. |

The paths above are what the readable Compose files declare. The approved inventory confirms mount destinations and read/write flags but withholds host source paths and named-volume details. Live source resolution, filesystem ownership, mount health, external Compose overrides, runtime environment resolution, project labels, profiles, and per-project dependencies beyond those explicitly stated are not independently verified. The audit previously observed `/mnt/old-hdd` resolving to the root filesystem; recheck before relying on the Pi-hole path. The Compose file's declared Pi-hole bind and that dated mount observation do not establish current data location.

### Comparison with local Git

- No complete local ARR, Jellyfin, or Pi-hole Compose project existed at the start of this phase. Sanitized Compose snapshots have now been added under `infra/compose/` based on the remote files read in this session.
- The local monitoring files also include a previously prepared partial security proposal under `proposed/monitoring/`. It must not be mistaken for the canonical observed baseline under `infra/compose/monitoring/`.
- Existing `scripts/homelab-inventory` is a read-only inventory tool, not a deployment interface.
- The local changes provide sanitized Compose snapshots, a management request client, tests, and workflow documentation. The snapshots have not been deployed or independently compared against files not readable to `agent`.

Migration-specific sanitization: Compose-time values are required variables with explicit errors and are supplied from protected runtime env files outside Git. Pi-hole's configured password value was omitted and replaced with `PIHOLE_WEBPASSWORD`; it must be populated by the administrator without placing it in Git. File formatting and YAML layout were normalized. No deliberate service, port, network, mount, image, or command changes were made in these baseline snapshots.

## Proposed canonical repository layout

```text
infra/
  compose/
    arr/compose.yaml
    jellyfin/compose.yaml
    pihole/compose.yaml
    monitoring/compose.yaml
    monitoring/prometheus/prometheus.yml
  policy/
    projects.yaml              # service-to-project and operation allowlists
  releases/                    # not committed; immutable, root-owned staged snapshots
ops/
  approvals/                   # administrator-controlled approval records; not agent-writable
  runtime-env/                 # secret-bearing files outside Git; never copied into release
scripts/
  homelab-ops                  # local request client (implemented in this phase)
  homelab-ops-gateway          # future root-owned server executable (not installed or run)
tests/
```

Keep the deployed/observed baseline distinct from proposed desired state until each Compose project is reviewed and sanitized. Any future Compose file in Git must use externally supplied runtime variables or protected env files, never embed credentials. `.env`, runtime env files, release approvals, rendered Compose output, and secret-bearing backups must remain outside Git. Do not copy the current Pi-hole literal password setting into the repository.

## Operational interface and privilege boundaries

At the end of Phase 1, the local `scripts/homelab-ops` client included future deploy and rollback request shapes. Phase 2 narrows it to the currently implemented scope:

```text
homelab-ops status
homelab-ops restart jellyfin
```

It prints the exact SSH request by default. `--send` is an explicit transport switch; the gateway is still not installed, so it must not be used until an administrator completes the installation checklist. Local client allowlists are usability checks only and are not a security boundary.

The Phase 2 server-side gateway implementation and exact administrator installation procedure are documented in [Phase 2](homelab-ops-phase-2.md) and [the administrator checklist](homelab-ops-installation.md). Deploy and rollback remain out of scope.

The Phase 1 future deployment design (for later phases):

1. Keep `agent` out of the Docker and sudo groups; no Docker socket access is granted.
2. Install a root-owned, non-agent-writable gateway and policy in root-owned directories. Permit only exact gateway invocation through a sudoers rule with fixed arguments constrained by the gateway; never allow `docker`, a shell, arbitrary Compose flags, or wildcard command arguments as separate sudo commands.
3. Expose a fixed service-name allowlist for restart and status. Restart must resolve a service to fixed project/release data and fixed container/service identifiers; reject all extra arguments.
4. For deployment, an administrator independently reviews the Git commit, validates it, stages a clean export under a root-owned release directory, and writes an approval record there. The gateway accepts only a project and full commit ID for which the root-owned release and approval record agree. It verifies ownership/mode, commit identity and content digest, rejects symlinks/unexpected files, and executes Compose only from that immutable staged snapshot. The calling account must not be able to write the release, policy, approval, runtime env, executable, or any parent directory.
5. Approval records are created outside the request client and are bound to project, full commit ID, release digest, and authorized operation. No request may approve itself. Stage a new immutable release rather than changing an approved release in place.
6. Use an administrator-controlled promotion process to move an approved revision into the active release pointer. Keep the previous known-good release and its matching protected runtime environment available for rollback. The gateway must not accept caller-provided file paths, environment file paths, command strings, image build context, arbitrary Compose profiles, or arbitrary service names.

The existing inventory sudo rule is independent and remains read-only. Do not install this or any later gateway rule until reviewed and approved by an administrator.

## Backup, validation, deployment, and rollback design

Before an approved deployment, the administrator should:

1. Verify the exact host, project, commit ID, approved release digest, and change diff.
2. Confirm a restorable backup/snapshot exists for affected persistent data when the change can migrate or alter data. A Compose config rollback alone does not reverse database/schema or application-data migrations.
3. Validate the exact staged release (`docker compose ... config --quiet`) using protected runtime environment without printing rendered configuration. Review image pinning, bind paths, networks, health checks, capability/device changes, and destructive options. Reject `down -v`, volume deletion, or unreviewed build operations.
4. Capture pre-change service status, health, target availability, and relevant application checks; store output securely and redact secrets.
5. Apply only the approved project/revision through the root-owned gateway. Preserve the prior release, backups, and logs.
6. Verify expected containers are running/healthy, only intended containers changed, Prometheus targets remain up, and service-specific DNS/HTTP/media checks pass. Observe through an agreed soak period.
7. If checks fail, explicitly authorize rollback to the named prior approved immutable release; restore data backup only if a data change requires it and after separately confirming recovery scope.

An image update or application migration may make a Compose-only rollback unsafe. Per-project backup and restore commands, schedules, destinations, and successful restore tests are unknown; resolve these before enabling deploy/rollback actions.

## Risks and open verification items

- Full local/remote parity is not established; only Compose documents readable in the authorized scope were reviewed.
- External overrides, runtime interpolation values, and secret files were intentionally not inspected.
- Actual host bind sources, permissions, named-volume paths, free space, backup coverage, and restore viability are unknown or only supported by dated audit observations.
- Mutable `latest` tags remain in several live Compose files; a reproducible release requires digest/version pinning as a separate reviewed change.
- Fixed API allowlists and read-only mounts do not make Docker socket access safe. Existing cAdvisor privileged mode and monitoring socket exposure need their own remediation approval.
- Host-network Pi-hole, published application ports, portainer/other operations, and all external network controls are outside this phase's operational interface.
- `--send` would fail until an administrator separately installs the server gateway and exact policy. It is deliberately not exercised here.

## Verification performed locally

Run from the repository root:

```sh
python3 -m unittest discover -s tests -v
```

Tests cover the inventory wrapper, Compose YAML, client dry-run and allowlist, gateway request validation, approval expiry/consumption/reuse/concurrency, protected permissions, timeouts, and failures. SSH and Docker executions are mocked; see [Phase 2](homelab-ops-phase-2.md) for the gateway-specific test details.

