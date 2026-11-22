# Homelab Compose

This directory is the desired configuration for the existing **Debian server**.
Edit it on the Mac; run the services on Debian. Pi-hole host networking, hardware
transcoding, host metrics and the absolute data paths depend on that Linux host.

Four independent projects retain their live identities. Do not combine them
under a new project name: existing containers, networks and management policies
refer to these identities.

| Directory | Compose project | Services | Persistent storage |
|---|---|---|---|
| `arr/` | `arr` | qBittorrent, Prowlarr, Radarr, Sonarr, Unpackerr | `/var/lib/homelab/arr`, `/mnt/media` |
| `jellyfin/` | `jellyfin` | Jellyfin | `/var/lib/homelab/jellyfin`, read-only `/mnt/media/jellyfin-media` |
| `pihole/` | `pi-hole` | Pi-hole | `/mnt/old-hdd/docker/pihole/etc-pihole` |
| `monitoring/` | `monitoring` | Prometheus, Grafana, node-exporter, cAdvisor, Docker health exporter | Existing `prometheus_data`, `grafana_data` volumes |

## Live assessment — 2026-11-22

Read-only SSH inspection found 12 running services and an exited `hello-world`
test container. All four Prometheus scrape targets were up. Grafana, Pi-hole,
Jellyfin and cAdvisor reported healthy. No server configuration was changed.

The active server source files are under
`/home/ravindu/Developer/homelab/{arr,jellyfin,monitoring,pi-hole}/`, using legacy
`docker-compose.yaml`/`docker-compose.yml` filenames. The Mac tree uses the layout
above; stage the monitoring configuration alongside its Compose file.

Changes from the inspected setup:

- Images are pinned to repository digests of the **running containers**. Tags
  remain readable, but the digest fixes actual content. This is a reproducibility
  baseline, not a vulnerability assessment or image upgrade.
- Explicit project names preserve `pi-hole` even though its directory is `pihole`.
  Existing container names, internal service DNS and Compose-owned networks stay.
- Every service uses the rotating `local` log driver, with `10m` and three files.
  Unpackerr logs to stdout instead of its separate unbounded log file.
- Bind mounts use `create_host_path: false`, so missing paths fail instead of
  creating empty directories. This does not detect an existing but unmounted
  `/mnt/media`; run the host preflight before adoption.
- Unpackerr's standalone watcher for the missing
  `/data/arr-downloads/complete/radar` directory is removed. Radarr/Sonarr API
  integration and existing extraction settings remain. The live config file had
  no separate folder or log-file setting. Check extraction after adoption.
- node-exporter's systemd collector returned
  `node_scrape_collector_success{collector="systemd"}=0`. Its flag is removed;
  this configuration does **not** provide systemd unit metrics. It avoids adding
  host D-Bus access. Existing process and host filesystem collectors remain.
- Host-root mounts retain the `rslave` propagation seen in running containers,
  which was missing from the old source snapshot.
- Prometheus gains a readiness check and defaults to `127.0.0.1:9090`; Grafana
  remains at `127.0.0.1:3000` and waits for Prometheus readiness.
- Arr web interfaces and Jellyfin HTTP bind to `WEB_BIND_IP` (default
  `192.168.1.10`), rather than every host interface. Torrent port 6881 and
  Jellyfin UDP discovery retain their current bindings. Pi-hole uses host
  networking; redundant port mappings are removed. Its DNS/web listeners still
  need appropriate host/router firewall rules.
- Existing monitoring volumes are external. Compose requires them to exist and
  will not remove them with `down --volumes`.

The media filesystem is `/dev/sdb2` at `/mnt/media`. The Pi-hole path currently
resides on the root filesystem, despite the `old-hdd` name. Jellyfin uses
`/dev/dri/renderD128`, group `render` GID 992. Arr uses UID/GID 1000:1000.

cAdvisor retains its current privileged mode, `/dev/kmsg` and host mounts.
The health exporter retains the Docker socket. A read-only socket bind still
allows Docker API requests; these services remain trusted host-level components.
Reducing those privileges requires separate runtime validation.

Terraform owns the separate, unused-by-these-stacks `homelab-media` and
`homelab-monitoring-v2` networks. Compose continues to own `arr-network` and
`monitoring-network`. Switching network ownership requires an explicit migration.
No Terraform state was modified.

## Environment and secrets

Each project has a tracked `.env.example`. Copy it into an administrator-protected
file **on the server**, fill in existing credentials and set permissions to 0600.
Keep the parent directory administrator-owned. Empty required secrets cause
Compose validation to fail.

| Project | Suggested protected file | Settings |
|---|---|---|
| Arr | `/etc/homelab-ops/runtime-env/arr.env` | `PUID`, `PGID`, `TZ`, `WEB_BIND_IP`, both `UN_*_API_KEY` values |
| Jellyfin | `/etc/homelab-ops/runtime-env/jellyfin.env` | `WEB_BIND_IP`, `RENDER_GID` |
| Pi-hole | `/etc/homelab-ops/runtime-env/pihole.env` | `TZ`, `PIHOLE_WEBPASSWORD` |
| Monitoring | `/etc/homelab-ops/runtime-env/monitoring.env` | `GRAFANA_ADMIN_USER`, `GRAFANA_ADMIN_PASSWORD` |

Preserve current API keys and passwords when adopting. Grafana admin variables
bootstrap a new database; editing them does not rotate credentials in the existing
database. Environment secrets remain visible to Docker administrators. Never
commit env files or save rendered `docker compose config` output. Use
`config --quiet` when checking actual runtime credentials.

## Validate from the Mac

With Python 3 and local Docker Compose:

```sh
python3 scripts/check-compose.py
```

Without local Docker, use the server's CLI over the configured SSH alias:

```sh
python3 scripts/check-compose.py --ssh homelab-terraform
ssh homelab-terraform 'sh -s' < scripts/check-compose-host.sh
```

The validator sends each local Compose file on stdin, supplies synthetic secrets,
disables automatic env-file loading and runs `docker compose config`. It writes
no remote files and does not create containers, networks or volumes. It checks
the schema, all 12 services, digests, logging, bind safety and project/storage
identities. It does not prove runtime readiness or that relative configuration
files have been staged on the server. The host preflight separately verifies the
media mount, data directories, devices and external volumes.

Validation performed for this change: all four projects passed the server's
Compose v5.5.1 parser and the checks above; Prometheus configuration passed
`promtool check config` using the running Prometheus binary. Deployment and
post-adoption application checks remain outstanding.

## Adopt on Debian

1. Back up current Compose/config files and env values, Arr databases, Jellyfin
   config, Pi-hole data and both monitoring volumes. Use application backups or
   a coordinated stop/snapshot for consistent databases. Verify restore works.
   Record running images and old source paths.
2. Stage the reviewed tree, including monitoring provisioning/config files, into
   a versioned administrator-owned release such as `/opt/homelab/releases/<revision>`.
   Keep env files separate. Bind source paths refer to the daemon host: using a
   Docker SSH context on the Mac does not transfer repository files to Debian.
   A privileged operations gateway must use its own approved immutable release
   and fixed env paths.
3. Run `sh scripts/check-compose-host.sh` on Debian. Check disk space, permissions,
   UID/GID and `ip -brief address` for `WEB_BIND_IP`. Ensure monitoring's relative
   bind source files exist in the staged release. Arrange boot ordering so media
   services start after `/mnt/media` mounts; Compose restart policies alone do
   not provide that guarantee.
4. From the staged release, check one project with its protected env file:

   ```sh
   docker compose --env-file /etc/homelab-ops/runtime-env/arr.env \
     -f infra/compose/arr/compose.yaml config --quiet
   ```

5. During adoption, run the corresponding command with `up -d` instead of
   `config --quiet`, one project at a time. Preserve explicit project names;
   avoid `down` and volume cleanup. Adopt monitoring early so it can observe the
   other projects. Pi-hole briefly interrupts LAN DNS when recreated; have a
   fallback DNS path. These deployment commands have **not** been run.
6. Check `docker compose ... ps`, recent logs, all Prometheus targets, DNS answers,
   Grafana dashboards, Jellyfin playback/transcoding and an Arr download/import/
   extraction. Existing application settings and health checks do not prove the
   complete download workflow.

For a fresh server only, create external volumes explicitly with
`docker volume create prometheus_data` and `docker volume create grafana_data`,
and provision host directories/permissions before starting. Do not create empty
replacement volumes during adoption if existing data is missing.

Access monitoring from the Mac with:

```sh
ssh -N -L 3000:127.0.0.1:3000 -L 9090:127.0.0.1:9090 homelab-terraform
```

Then open `http://localhost:3000` or `http://localhost:9090`.

To roll back configuration, run the previous Compose files with their existing
env values and the same project names. If an application/database changed,
restore its consistent backup as well; reverting YAML alone cannot reverse a
schema migration. Future image updates should change a tag/digest together in a
reviewed change, with backups and post-update checks.

References: [Compose bind/logging configuration](https://docs.docker.com/reference/compose-file/container-spec/),
[external volumes](https://docs.docker.com/reference/compose-file/volumes/),
[node-exporter container mounts](https://github.com/prometheus/node_exporter#docker),
[Unpackerr configuration](https://unpackerr.zip/docs/install/configuration/).
