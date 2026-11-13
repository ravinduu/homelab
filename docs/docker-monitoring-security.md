# Docker monitoring socket security review

**Review date:** 2026-11-12  
**Mode:** Read-only investigation and local planning; no server changes made.

## Verified state

The 2026-11-12 follow-up read of `/home/ravindu/Developer/homelab/monitoring/docker-compose.yaml` and approved live inventory confirmed `fviolence/docker-health-exporter:v1.0` on `monitoring-network`, with no host-published port and `/var/run/docker.sock:/var/run/docker.sock:ro`. The original audit's read-write characterization was incorrect: the wrapper emits Docker `.Mounts[].RW`, and the live exporter mount was `false` (read-only). This does not constrain HTTP methods sent over the socket; the exporter can still reach Docker API endpoints. Prometheus had four active targets (`prometheus`, `node`, `cadvisor`, `docker-health`), all up, with a 15-second scrape interval. cAdvisor was `ghcr.io/google/cadvisor:v0.60.6`, with `privileged: true` and read-only mounts including `/var/run` and `/var/lib/docker`.

The exporter documents five metric families: health and one-hot health status; running state; restart count; and start time. Its source uses Docker SDK operations to list all containers and reload each container's details, then derives image tags and those metrics. This includes stopped containers, unlike the resource view normally used from cAdvisor. Docker API semantic calls therefore include version discovery, listing all containers, and inspecting per-container details; exact HTTP requests depend on the pinned SDK/image implementation and were not captured on the host.

The image's own documentation recommends a socket bind marked `:ro`, and the deployed Compose file does use that flag. A read-only filesystem bind does not make Docker API requests read-only: a client that can connect to the Unix socket may still send mutating API methods. Therefore, changing the mount flag is not a mitigation; an API-filtering proxy or removing the socket consumer is needed to constrain access.

## Limits of this review

The monitoring Compose and Prometheus files are now readable to `agent`. The directory contains three YAML files: the Compose file, Prometheus scrape configuration, and Grafana Prometheus datasource provisioning. No rule or dashboard files were found under that directory. This does not rule out dashboards stored in Grafana's data volume. The live Prometheus API reports all four targets up. It currently has 13 series each for `docker_container_health`, `docker_container_running`, `docker_container_restart_count`, and `docker_container_started_at_seconds`, plus 52 one-hot `docker_container_health_status` series (four status labels for 13 containers). cAdvisor also exposes 13 `container_health_state` series. No claim is made that cAdvisor preserves the exporter's restart-count, start-time, stopped-container coverage, or exact one-hot health status metrics.

## cAdvisor least-privilege review

The verified host is Debian 13 on kernel `6.12.105+deb13-amd64` with unified cgroup v2 (`cgroup2fs`). cAdvisor v0.60.6 is scraping successfully and Prometheus currently has cAdvisor `container_health_state`, `container_start_time_seconds`, `container_last_seen`, `container_tasks_state`, `container_oom_events_total`, CPU, memory, filesystem, and network metric families. The live health gauge values included `1` and `-1`; upstream v0.60.6 code maps healthy to `1`, unhealthy/starting to `0`, and no health check to `-1`.

The existing Compose service has `privileged: true`, no explicit `cap_add` or `cap_drop`, and maps `/dev/kmsg` without restricting device permissions. Its command only sets `--docker_only=true` and `--housekeeping_interval=15s`; it does not enable process metrics. Upstream v0.60.6 docs provide a non-privileged standard Docker setup. They call for privileged mode and host PID only when process metrics are enabled; perf-event collection has separate device/seccomp requirements. Thus privileged mode is not justified by the observed current cAdvisor metric selection. Docker's normal default capability set remains when `privileged` is removed; upstream does not enumerate a narrower exact capability set for this deployment. Do not claim `cap_drop: ALL` works until runtime validation.

The host's `/proc/sys/kernel/dmesg_restrict` is `1`. cAdvisor currently exposes the `container_oom_events_total` metric and its v0.60.6 code reads OOM data through `/dev/kmsg`. Linux documents that reading the kernel log with `dmesg_restrict=1` requires `CAP_SYSLOG`. The proposed candidate therefore adds only `SYSLOG` to the normal Docker capability set and maps `/dev/kmsg` with read-only device permission. This is narrower than privileged mode but grants cAdvisor access to kernel log contents; if that exposure is not acceptable, omit `SYSLOG` and explicitly disable/retire OOM event metrics instead.

| Existing mount/device | Purpose and proposed disposition |
|---|---|
| `/:/rootfs:ro` | Host filesystem/device context for filesystem and machine metrics; keep read-only. |
| `/var/run:/var/run:ro` | Overbroad host runtime directory. cAdvisor's configured default Docker endpoint is `/var/run/docker.sock`; replace with `/var/run/docker.sock:/var/run/docker.sock:ro`. This narrows host files visible, but does **not** filter Docker API methods. |
| `/sys:/sys:ro` | Host cgroup and kernel statistics; keep read-only. Debian 13 cgroup v2 is confirmed and current metrics are present. |
| `/var/lib/docker:/var/lib/docker:ro` | Docker storage/container metadata used by cAdvisor; keep read-only initially to preserve current filesystem/container metrics. |
| `/dev/disk:/dev/disk:ro` | Device/filesystem metadata; preserve initially and remove only after metric comparison shows it is unnecessary. |
| `/dev/kmsg` device | cAdvisor OOM event reader; the metric family is currently exposed. Keep the device with read-only device access (`/dev/kmsg:/dev/kmsg:r`) and add only `CAP_SYSLOG` because host `dmesg_restrict=1`; recheck OOM metrics after migration. |

The Docker socket remains a broad API capability for cAdvisor even after removal of `privileged`; a read-only bind is not an API method filter. If the security objective is to eliminate broad Docker API access from all monitoring containers, a separately tested proxy/filtered API or acceptance of reduced cAdvisor discovery/health coverage is still required.

References: [cAdvisor v0.60.6 running guide](https://github.com/google/cadvisor/blob/v0.60.6/docs/running.md), [cAdvisor v0.60.6 runtime options](https://github.com/google/cadvisor/blob/v0.60.6/docs/runtime_options.md), [cAdvisor v0.60.6 health metric implementation](https://github.com/google/cadvisor/blob/v0.60.6/lib/metrics/prometheus.go), and [Linux `dmesg_restrict` documentation](https://www.kernel.org/doc/html/latest/admin-guide/sysctl/kernel.html).

## Proposed local files

`proposed/monitoring/docker-compose.yaml` is a local cAdvisor service fragment, not a replacement for the complete deployed Compose file. It removes `privileged: true`, narrows `/var/run` to the Docker socket, limits `/dev/kmsg` to read access, adds only `SYSLOG` to preserve current OOM collection, and adds `no-new-privileges`. `proposed/monitoring/prometheus.yml` keeps the existing Prometheus, node-exporter, and cAdvisor jobs and omits only `docker-health`. These files have not been deployed.

## Architecture options

| Option | Security | Coverage | Complexity and maintenance |
|---|---|---|---|
| Remove the exporter; use cAdvisor + node-exporter | Removes this exporter's Docker socket access. cAdvisor can run without `privileged` for standard metrics, but retains Docker API access through its socket; this is not a complete stack-wide API restriction. | Live cAdvisor metrics include health state and `container_start_time_seconds`; resource/health/start-time series cover running containers. It does not expose Docker restart counts or the stopped container present in exporter data. Health gauge folds starting/unhealthy into `0`, unlike one-hot status labels. | Simplest service graph. Prometheus has no loaded rule groups and no rule files were found; dashboards in Grafana's data volume remain unverified. |
| Retain exporter behind an endpoint-allowlisted proxy | Can block write methods and unrelated API areas, but a generic `/containers` allow switch is broad. Container inspect responses can include environment and other sensitive configuration, so transport-level endpoint allowlisting does not redact returned data. | Closest to current metric coverage; exporter needs list-all and per-container inspect semantics and may need version/image metadata calls. | Adds a proxy, image update and API compatibility work. Must maintain and test exact route/method allowlists. |
| Replace with a safer monitoring method | A purpose-built host-side collector can emit only approved fields and avoid giving an application container a general Docker socket. No such collector is currently verified as installed. | Can preserve required metrics if designed for them, including stopped-container state. | Requires development, packaging, and ongoing maintenance; more work than removing an unnecessary exporter. |

### Socket-proxy caveat

The commonly used Tecnativa proxy documents `POST=0` as method restriction, but its `CONTAINERS=1` setting enables the container API namespace. As of this review, upstream issue #182 reports that this broad GET namespace also allows container archive/export/log/top endpoints; its proposed fix is tracked separately as PR #183. A read-only socket mount or `POST=0` alone does not mitigate sensitive GET endpoints. Do not deploy the generic `CONTAINERS=1` configuration as the proposed allowlist. A proxy option requires a reviewed version containing the relevant deny rules (verified by tests) or a custom route policy that allows only the exact exporter calls and denies archive, export, logs, top, attach, exec, and all write methods. Also account for sensitive fields in `GET /containers/{id}/json` responses.

## Recommendation

Removing `docker-health-exporter` and its scrape job removes that service's Docker API path while retaining the verified Prometheus, node, and cAdvisor targets. cAdvisor's pinned build already emits resource, health, and start-time metrics. Before removal, confirm whether Grafana's persisted dashboards or external alerting depend on Docker restart counts, stopped-container visibility, or the exporter's distinct `starting`/`unhealthy` labels. The local candidate also drops cAdvisor's privileged mode and narrows `/var/run` to the Docker socket; its socket still grants broad Docker API access, so this is least privilege for the cAdvisor process/mounts, not an API endpoint allowlist.

The audit does not reveal the owner's required dashboard/alert coverage, so cAdvisor-only equivalence cannot be asserted yet. If stopped-container state, restart counts, or exact `docker_container_*` series are required, do not substitute cAdvisor and silently lose those signals. First record the exact queries and define a purpose-built filtered collector or a narrowly tested proxy; the generic proxy's `CONTAINERS=1` setting is not acceptable without fixing and validating its broad GET exposure and response-data leakage.

The recommendation removes the exporter, not every Docker-related access in the monitoring stack. cAdvisor's current read-only runtime mounts and trust boundary need a separate review if the goal expands to eliminating all Docker API or host-runtime visibility from monitoring containers.
