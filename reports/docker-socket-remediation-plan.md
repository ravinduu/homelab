# Docker socket exposure remediation plan

**Prepared:** 2026-11-12 (Asia/Colombo)  
**Status:** Proposed only. No remote configuration, permissions, containers, or services were changed.

## Current state and root cause

Follow-up read-only inspection found `/home/ravindu/Developer/homelab/monitoring/docker-compose.yaml` and corrected an audit error: the exporter socket is mounted `:ro`, and the live inventory reports `.Mounts[].RW=false`. This only makes the socket filesystem bind read-only; it does not restrict Docker API methods. The exporter image `fviolence/docker-health-exporter:v1.0` polls the Docker Engine and exports health/status, running state, restart count, and start time. Its documented implementation lists all containers and inspects each container.

The monitoring config is now readable. Prometheus has four active targets (`prometheus`, `node`, `cadvisor`, `docker-health`), all up, at a 15-second scrape interval; the `docker-health` target is `docker-health-exporter:9066`. The Prometheus API currently has 13 series each for `docker_container_health`, `docker_container_running`, `docker_container_restart_count`, and `docker_container_started_at_seconds`, plus 52 `docker_container_health_status` series. cAdvisor has 13 `container_health_state` series. cAdvisor is configured `privileged: true` and mounts `/var/run` read-only, so removing the exporter will not remove the monitoring stack's privileged host/runtime access. No rule/dashboard files were found in the monitoring directory; Grafana's persisted dashboards and external alerting remain unknown. Proposed snippets below can now be reconciled with `/home/ravindu/Developer/homelab/monitoring/docker-compose.yaml` and `prometheus/prometheus.yml`, but are still not applied.

## Options and choice

1. **Preferred for reducing exporter exposure, subject to coverage gate: remove the health exporter and its scrape job; keep cAdvisor and node-exporter.** This removes the exporter's Docker socket access. cAdvisor supplies resource, coarse health-state, and running-container start-time series, but not exact one-hot health status, Docker restart counts, or stopped-container series. cAdvisor's `privileged: true` configuration must also be removed/reviewed.
2. **Endpoint-allowlisted proxy:** closest to current metric coverage but more complex. A generic Docker socket proxy `CONTAINERS=1, POST=0` is not sufficient: `CONTAINERS=1` opens a broad GET namespace, and `GET /containers/{id}/json` can reveal more metadata than the exporter publishes. The current upstream issue/PR status and exact proxy image digest must be reviewed before considering it.
3. **Purpose-built filtered collector:** best way to retain only needed metrics while avoiding a general API exposed to the exporter, but entails implementation and maintenance. No such local or remote component was verified.

**Recommendation:** remove the exporter and its scrape job after confirming no required Grafana panel or external alert depends on exporter-only series. The project directory contains no alert rules or dashboard files, but persisted Grafana dashboards have not been inspected. Do not mistake this change for complete monitoring hardening: separately reduce cAdvisor's privileged mode and Docker/runtime visibility, validating cAdvisor functionality after each least-privilege adjustment. Do not use a read-only socket mount alone as API remediation.

## cAdvisor privilege and mount assessment

Observed host: Debian GNU/Linux 13 (trixie), kernel `6.12.105+deb13-amd64`, unified cgroup v2 (`cgroup2fs`). The deployed cAdvisor is `ghcr.io/google/cadvisor:v0.60.6`. Its current command only selects Docker containers and a 15-second housekeeping interval; it does not enable process metrics. Upstream v0.60.6 documentation includes a standard non-privileged Docker invocation and says host PID plus privileged mode are needed when process metrics are enabled. Perf-event collection has its own device/seccomp requirements and is not enabled here. The host is Debian, not the SELinux/RHEL case described in the docs. cAdvisor v0.60.6 has successfully scraped cgroup v2 CPU/memory/resource metrics on this host.

The Compose file has `privileged: true`, no explicit `cap_add` or `cap_drop`, and maps `/dev/kmsg` as a device. Removing `privileged` drops the broad all-capabilities/all-devices grant and returns the container to Docker's normal default capability profile. Upstream supports non-privileged standard collection but does not give an exact reduced capability list for this deployment. Host `/proc/sys/kernel/dmesg_restrict` is `1`; cAdvisor's OOM parser reads `/dev/kmsg`, and Linux documents that reading the kernel log under this setting requires `CAP_SYSLOG`. The candidate adds only `SYSLOG` to preserve OOM metrics, retains the default capability set, and does not yet use `cap_drop: ALL`; test capability dropping separately before tightening further.

| Resource | Current setting | Candidate and expected effect |
|---|---|---|
| `privileged` | `true` | Remove. Standard CPU, memory, filesystem, network and health collection is documented without privileged mode; process metrics are disabled by default. Runtime success must still be verified after approval. |
| Linux capabilities | No explicit `cap_add`/`cap_drop`; privileged mode grants broad capabilities | Add only `SYSLOG` to retain `/dev/kmsg` OOM events with host `dmesg_restrict=1`; otherwise use normal Docker defaults. `cap_drop: ALL` is not included because exact cAdvisor requirements have not been proven on this host. `SYSLOG` exposes kernel log contents to cAdvisor. |
| `/` to `/rootfs` | Read-only | Keep; cAdvisor uses host filesystem context for filesystem/machine metrics. |
| `/var/run` | Whole directory read-only | Replace with only `/var/run/docker.sock:/var/run/docker.sock:ro`. cAdvisor's Docker discovery uses the socket; this reduces exposed host runtime files but still allows broad Docker API methods. |
| `/sys` | Read-only | Keep for cgroup/kernel resource metrics; cgroup v2 and metrics were observed working. |
| `/var/lib/docker` | Read-only | Keep initially for Docker metadata and filesystem metrics. |
| `/dev/disk` | Read-only | Keep initially; compare filesystem/device series before considering removal. |
| `/dev/kmsg` | Device mapping with default permissions | Restrict to read permission (`/dev/kmsg:/dev/kmsg:r`) and add `SYSLOG` to preserve cAdvisor's OOM event reader while removing device write/mknod grants. Recheck OOM metrics after deployment. |
| network | Private `monitoring-network`, no published cAdvisor port | Keep unchanged. |

## Monitoring dependencies and expected metric changes

Accessible Prometheus rules API returned no loaded rule groups, and no rule files exist under the monitoring project directory. The Grafana dashboard search endpoint returned HTTP 401; only a Prometheus datasource provisioning file was found in the project tree, so dashboards stored in Grafana's data volume could not be reviewed. The monitoring directory also contains `.env`; it was not opened or read.

The live Prometheus API currently reports 13 series each for exporter metrics `docker_container_health`, `docker_container_running`, `docker_container_restart_count`, and `docker_container_started_at_seconds`, plus 52 one-hot `docker_container_health_status` series. cAdvisor currently emits 13 `container_health_state`, `container_start_time_seconds`, `container_last_seen`, and `container_oom_events_total` series; `container_tasks_state` has 65 series. Twelve named running containers appear in the cAdvisor health output, while the exporter has a stopped one-off container series as well.

| Exporter metric | cAdvisor replacement | Expected impact |
|---|---|---|
| `docker_container_health` | `container_health_state` | Similar coarse state for discovered containers, with different name/labels and values. |
| `docker_container_health_status` | `container_health_state` | Loses one-hot labels; cAdvisor maps healthy to `1`, starting/unhealthy to `0`, and no check to `-1`. |
| `docker_container_running` | `container_tasks_state` / `container_last_seen` | No exact Docker running boolean; stopped containers are not represented in cAdvisor's current health/start-time series. |
| `docker_container_restart_count` | None verified | Restart count monitoring is lost. |
| `docker_container_started_at_seconds` | `container_start_time_seconds` | Similar start-time information for containers cAdvisor currently discovers; series and labels differ, and stopped-container coverage is lost. |

The proposed Prometheus file removes only the `docker-health` job, changing target count from four to three (`prometheus`, `node`, `cadvisor`). Those three jobs remain unchanged and are currently up. Any Grafana panels or external alerting that require the exporter metrics must be migrated or accepted as retired before deployment.

## Prepared local candidate and validation

Local, non-deployed candidate files:

- `proposed/monitoring/docker-compose.yaml` — cAdvisor service fragment only; removes privileged mode, narrows the runtime mount to the Docker socket, makes `/dev/kmsg` read-only, adds only `SYSLOG` to preserve OOM collection, and adds `no-new-privileges`.
- `proposed/monitoring/prometheus.yml` — three-scrape-job Prometheus configuration, omitting only `docker-health`.

Validation performed locally with Ruby Psych 3.1: both YAML files parsed; Compose assertions confirmed no `privileged: true`, only `SYSLOG` explicitly added, the read-only individual socket bind, no whole `/var/run` bind, read-only `/dev/kmsg` device permission, and no exporter service. Prometheus assertions confirmed exactly the `prometheus`, `node`, and `cadvisor` jobs and no exporter target. No Docker Compose CLI or `promtool` is installed locally, so full Compose schema resolution and Prometheus-native `promtool check config` were unavailable. No remote test container was created because deployment/runtime testing is not authorized.

The candidate is syntactically and structurally validated, not runtime validated. Expected runtime checks after a separately approved deployment: cAdvisor health stays healthy; Prometheus retains three `up` targets; cAdvisor resource, health, start-time and OOM metric families remain present; no container restarts or scrape errors appear; any expected loss of exporter-only metrics is reflected in dashboards/alerts; cAdvisor startup logs show no permission/device errors. Do not infer from the static check that `cap_drop: ALL` or the read-only `/dev/kmsg` device works at runtime.

## Deployment gate, risks, and rollback

- **Risks:** `SYSLOG` gives cAdvisor access to kernel log contents. cAdvisor may lose OOM events or filesystem/device metrics if access is too narrow; dropping privileged mode may reveal an undocumented runtime dependency. The socket remains a broad Docker API capability for cAdvisor. Exporter removal drops restart counts and stopped-container status; Grafana dashboards remain unknown.
- **Pre-deployment:** owner reviews dashboards and monitoring requirements, records a recoverable copy/revision of both deployed files, validates the full Compose model and Prometheus config, and explicitly approves the exact service/configuration operations. Never access `.env` for this work.
- **Apply scope after approval only:** edit the remote cAdvisor service according to the local fragment, remove the exporter service, remove only the `docker-health` scrape job, validate both configs, then recreate only cAdvisor and Prometheus as required. No such operations are authorized or performed in this task.
- **Verification:** confirm all three remaining Prometheus targets are up; compare cAdvisor metric families and OOM event collection; review cAdvisor logs for denied access; verify Grafana panels and alert outcomes; confirm the exporter container is no longer running and the exporter socket bind is absent. Docker API access through cAdvisor remains and should be reported as residual risk.
- **Rollback:** restore the exact saved Compose and Prometheus files; validate them; recreate only the affected monitoring services; confirm all four targets return up and exporter metrics reappear. Restoring the exporter restores its broad Docker API access even though its socket bind is `:ro`, so record that residual risk and keep the exporter disabled until the endpoint/API approach is accepted.

**Approval boundary:** local candidate preparation and static validation are complete. Any remote deployment, container recreation, or restart requires separate explicit approval. No remote changes were made.

## Proposed configuration edits (not applied)

The files are now accessible at `/home/ravindu/Developer/homelab/monitoring/docker-compose.yaml` and `/home/ravindu/Developer/homelab/monitoring/prometheus/prometheus.yml`. Preserve project structure, image pins, and unrelated settings. The proposed Compose edit is to delete the complete `docker-health-exporter` service at lines 115-132, including its socket mount, environment, network, restart policy, and `no-new-privileges` setting. The exporter has no host-published port.

```yaml
services:
  docker-health-exporter:
    image: fviolence/docker-health-exporter:v1.0
    container_name: docker-health-exporter
    environment:
      PORT: 9066
      SCRAPE_INTERVAL: 10
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - monitoring
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
```

Delete this service block from the Compose file; do not change the exporter mount to `:rw` or assume `:ro` constrains API methods.

The exporter Compose service currently includes `PORT: 9066`, `SCRAPE_INTERVAL: 10`, the read-only socket bind, and `security_opt: no-new-privileges:true`. Keep the existing cAdvisor service and target unchanged for the initial migration. Note that cAdvisor is configured `privileged: true` with `/var/run:/var/run:ro`; removing the exporter does not remove that existing privileged host/runtime access.

Remove only the following exact `docker-health` scrape job from the current Prometheus file (global scrape interval is 15 seconds):

```diff
-  - job_name: docker-health
-    static_configs:
-      - targets:
-          - docker-health-exporter:9066
```

Delete that block only. Preserve the existing `prometheus`, `node`, and `cadvisor` jobs verbatim. Prometheus API currently returns all four targets `up`; cAdvisor emits 13 `container_health_state` samples. Search Grafana's persisted dashboards and any external rules for `docker_container_health`, `docker_container_health_status`, `docker_container_running`, `docker_container_restart_count`, and `docker_container_started_at_seconds`; migrate or explicitly retire dependencies before removing the target. No rule/dashboard files were found in the monitoring project directory, but the Grafana API inventory was unavailable without credentials.

### Conditional proxy design if the coverage gate fails

Do not deploy until exact API calls are confirmed against the image and an integration test proves route behavior and response data minimization. Any proxy must:

- Mount `/var/run/docker.sock` only into the proxy and keep the exporter on a private monitoring network with no host-published proxy port.
- Allow only required `GET` operations (anticipated semantics: API version, list all containers, inspect each container; verify image-tag resolution against the image's SDK version).
- Deny every write method and dangerous GET routes such as archive, export, logs, top, attach, and exec.
- Avoid exposing unfiltered container inspect environment/config if possible. If response redaction is not feasible, treat the proxy as disclosing those details to a compromised exporter and prefer a filtered collector.
- Use a fixed, reviewed image digest/version and automated positive/negative API tests. `POST=0` plus `CONTAINERS=1` is not an adequate endpoint allowlist.

No ready-to-deploy proxy Compose block is supplied because the exact SDK calls, acceptable metadata exposure, and safe proxy implementation are not verified. A misleading generic proxy config would recreate a broad read API.

## Validation plan (before and after an approved deployment)

### Before change

1. Use the now-readable Compose and Prometheus files at `/home/ravindu/Developer/homelab/monitoring/`; do not open `.env` or record secret-bearing config values.
2. Record `docker compose config` output locally for review only, checking for interpolation that would reveal secrets before capturing it. Record current service names/image IDs, target health, and current metric series without exporting credentials.
3. Inspect Grafana dashboards and alert rules for the five exporter metric families listed above. Dashboard API access may need an owner-provided export; do not seek credentials from the server.
4. Query cAdvisor directly from Prometheus for expected running-container resource series and health-state metrics. Confirm the pinned cAdvisor build actually emits the exact metric names/labels used by required panels.
5. Confirm owner approval for removing exporter-only stopped-container, restart-count, and start-time monitoring, if those signals cannot be reproduced.

### After change

1. Validate Compose syntax/configuration locally against the exact deployment files before any service action.
2. Apply only after separate explicit Execute authorization. Start/recreate only the monitoring services affected by this plan; do not change unrelated services.
3. Confirm Prometheus targets `prometheus`, `node`, and `cadvisor` are `up`; confirm the obsolete `docker-health` target is absent by design and no unintended target became down.
4. Compare expected cAdvisor/node-exporter queries and dashboards to the recorded baseline. Check that no required panels/rules return empty data due to removed `docker_container_*` metrics.
5. Confirm the `docker-health-exporter` container is absent and no exporter mount of `/var/run/docker.sock` remains in the resulting Compose model/container metadata. Do not infer that cAdvisor has no Docker access; its runtime mounts remain separately present.
6. Observe at least one full scrape interval plus the normal dashboard refresh/alert evaluation window; check Prometheus logs/alerts for scrape and rule errors.

## Rollback

1. Restore the exact saved Compose and Prometheus configuration versions from the pre-change backup/revision, including the exporter service and its `docker-health` scrape job.
2. Validate restored Compose and Prometheus configuration before restarting/recreating only the affected monitoring services.
3. Confirm the `docker-health` target returns `up` and its expected metrics reappear; confirm other targets remain `up`.
4. Record the reason for rollback. Restoring the exporter also restores broad Docker API access despite its `:ro` socket bind; owner must explicitly accept that residual risk or keep the exporter disabled until API access is constrained.

No backup of live Compose or Prometheus files was accessible to `agent`; the deployment owner must confirm a recoverable copy/revision before execution. No remote commands beyond read-only SSH inspection are authorized in this task.

## Risks and approvals

- **Risk level:** High until the exporter Docker API path is removed or constrained.
- **Coverage risk:** Medium; exporter metrics may drive dashboards/alerts not visible in this audit.
- **Availability risk:** Low to moderate for a controlled exporter removal, but a Prometheus config error or overlooked dependency can break metrics/alerts.
- **Required approval:** This is a plan only. Any live Compose/config edits, container recreation, or restart requires a later explicit authorization of the exact operations. No change is authorized here.

## Evidence and sources

- Local audit: `reports/homelab-audit.md`, especially Docker inventory, Security Assessment, Monitoring and Observability, and Evidence and Limitations.
- Local architecture: `docs/infrastructure.md`, `docs/service-inventory.md`, and `docs/docker-monitoring-security.md`.
- Exporter image documentation/source: [fviolence/docker-health-exporter](https://github.com/fviolence/docker-health-exporter) describes exported metrics and collection behavior.
- cAdvisor official Prometheus metrics guide: [cAdvisor metrics](https://github.com/google/cadvisor/blob/master/docs/storage/prometheus.md).
- cAdvisor v0.60.6 deployment and runtime documentation: [running cAdvisor](https://github.com/google/cadvisor/blob/v0.60.6/docs/running.md), [runtime options](https://github.com/google/cadvisor/blob/v0.60.6/docs/runtime_options.md).
- cAdvisor v0.60.6 metric implementation: [Prometheus health-state code](https://github.com/google/cadvisor/blob/v0.60.6/lib/metrics/prometheus.go), [OOM parser](https://github.com/google/cadvisor/blob/v0.60.6/utils/oomparser/oomparser.go).
- Linux kernel documentation: [dmesg_restrict and CAP_SYSLOG](https://www.kernel.org/doc/html/latest/admin-guide/sysctl/kernel.html).
- Socket proxy project guidance: [Tecnativa/docker-socket-proxy](https://github.com/Tecnativa/docker-socket-proxy); security report and proposed fix: [issue #182](https://github.com/Tecnativa/docker-socket-proxy/issues/182), [PR #183](https://github.com/Tecnativa/docker-socket-proxy/pull/183). These upstream links are time-sensitive; confirm current status before choosing a proxy.
