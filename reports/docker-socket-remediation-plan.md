# Docker socket exposure remediation plan

**Prepared:** 2026-11-12 (Asia/Colombo)  
**Status:** Proposed only. No remote configuration, permissions, containers, or services were changed.

## Current state and root cause

The 2026-11-12 audit reports `docker-health-exporter` image `fviolence/docker-health-exporter:v1.0` with `/var/run/docker.sock` mounted read-write. The exporter polls the Docker Engine and exports health/status, running state, restart count, and start time. Its documented implementation lists all containers and inspects each container. Socket access exposes a general Docker API control path; Docker socket mount `:ro` only protects mount-file writes and does not enforce HTTP method or endpoint restrictions.

The audit observed four Prometheus targets, all up, including `cadvisor` and `docker-health`. A later read-only SSH session succeeded, but `agent` was denied Docker API access; the approved inventory wrapper hides host bind sources. Filename search found only unrelated accessible Compose/Prometheus files (LocalStack, Minecraft, and two application projects), not the running monitoring stack's configuration. `/home/ravindu` is mode `0700` and inaccessible. One accessible LocalStack Compose file declares a Docker socket bind, but no LocalStack container appeared in the live inventory, so deployment is unverified. The actual monitoring Compose project, scrape config, exporter port configuration, dashboards, rules, and cAdvisor metrics remain inaccessible. Do not treat proposed snippets below as a ready-to-apply patch against the unknown deployment file.

## Options and choice

1. **Preferred, subject to coverage gate: remove the health exporter and its scrape job; keep cAdvisor and node-exporter.** This removes the exporter's Docker socket exposure and simplifies the stack. It preserves resource/host monitoring but may drop health, stopped-container, restart-count, and start-time series.
2. **Endpoint-allowlisted proxy:** closest to current metric coverage but more complex. A generic Docker socket proxy `CONTAINERS=1, POST=0` is not sufficient: `CONTAINERS=1` opens a broad GET namespace, and `GET /containers/{id}/json` can reveal more metadata than the exporter publishes. The current upstream issue/PR status and exact proxy image digest must be reviewed before considering it.
3. **Purpose-built filtered collector:** best way to retain only needed metrics while avoiding a general API exposed to the exporter, but entails implementation and maintenance. No such local or remote component was verified.

**Recommendation:** take option 1 only after the compatibility gate confirms the owner accepts loss of exporter-only metrics and all required panels/alerts work from cAdvisor/node-exporter. If not, pause removal and design a filtered collector or tested proxy. Do not use a read-only socket mount alone as remediation.

## Proposed configuration edits (not applied)

First obtain the actual Compose and Prometheus configuration through an authorized administrator or an approved read-only path. Preserve the existing project structure, image pins, and unrelated settings. The intended Compose edit is to delete the complete `docker-health-exporter` service, including its socket mount, environment, networks, and health/restart settings. In particular, no line equivalent to this should remain:

```yaml
services:
  docker-health-exporter:
    image: fviolence/docker-health-exporter:v1.0
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

Do not paste that abbreviated block over the deployed service; it only identifies the service and risky mount from the audit. Keep the existing cAdvisor service and its current Prometheus target unchanged for the initial migration.

Remove only the Prometheus `docker-health` scrape job after confirming its exact target and labels. The intended change is:

```diff
 scrape_configs:
-  - job_name: docker-health
-    static_configs:
-      - targets: ["<existing-exporter-target>"]
   - job_name: cadvisor
     static_configs:
       - targets: ["<existing-cadvisor-target>"]
```

This is a structural example, not a literal patch: actual keys, target names, relabeling, and config layout are unknown. Preserve the existing cAdvisor job verbatim. Search Grafana dashboards and Prometheus rules for `docker_container_health`, `docker_container_health_status`, `docker_container_running`, `docker_container_restart_count`, and `docker_container_started_at_seconds`; migrate or explicitly retire every dependent panel/rule before removing the target.

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

1. Obtain Compose and Prometheus config without reading secret-bearing env files; redact credentials if configuration snippets are recorded.
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
4. Record the reason for rollback. Do not restore the former read-write socket exposure without owner acknowledgement of the risk and a separately reviewed mitigation; preferred rollback is to restore monitoring availability temporarily while keeping the exporter disabled until its API access is constrained.

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
- Socket proxy project guidance: [Tecnativa/docker-socket-proxy](https://github.com/Tecnativa/docker-socket-proxy); security report and proposed fix: [issue #182](https://github.com/Tecnativa/docker-socket-proxy/issues/182), [PR #183](https://github.com/Tecnativa/docker-socket-proxy/pull/183). These upstream links are time-sensitive; confirm current status before choosing a proxy.
