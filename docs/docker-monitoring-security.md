# Docker monitoring socket security review

**Review date:** 2026-11-12  
**Mode:** Read-only investigation and local planning; no server changes made.

## Verified state

The 2026-11-12 audit records `fviolence/docker-health-exporter:v1.0` on `monitoring-network`, with no published host port and a read-write bind of `/var/run/docker.sock`. Prometheus had four active targets (`prometheus`, `node`, `cadvisor`, `docker-health`), all up. cAdvisor was `ghcr.io/google/cadvisor:v0.60.6`, on `monitoring-network`, with read-only mounts for host runtime/system paths including `/var/run` and `/var/lib/docker`.

The exporter documents five metric families: health and one-hot health status; running state; restart count; and start time. Its source uses Docker SDK operations to list all containers and reload each container's details, then derives image tags and those metrics. This includes stopped containers, unlike the resource view normally used from cAdvisor. Docker API semantic calls therefore include version discovery, listing all containers, and inspecting per-container details; exact HTTP requests depend on the pinned SDK/image implementation and were not captured on the host.

The image's own documentation recommends a socket bind marked `:ro`, but a read-only filesystem bind does not make Docker API requests read-only. A client that can connect to the Unix socket may still send mutating API methods. The audited read-write mount is therefore materially overprivileged, and changing only `:rw` to `:ro` is not an adequate mitigation.

## Limits of this review

The initial follow-up SSH attempts on 2026-11-12 timed out, but a subsequent read-only SSH connection succeeded. `agent` could not use Docker Compose directly because Docker API access was denied; the approved inventory wrapper returned live container metadata while withholding host bind source paths. A filename-only search of accessible paths found Compose files for LocalStack and Minecraft and Prometheus configs in two application projects, but none mapped to the running monitoring stack. `/home/ravindu` itself is mode `0700` and inaccessible. The accessible `/mnt/media/home/ravindu/localstack/docker-compose.yaml` declares a `/var/run/docker.sock` bind; the live inventory did not show a LocalStack container, so whether that file is active is unverified. The actual monitoring Compose source, socket mount syntax, scrape interval/job block, current rules/dashboard queries, and cAdvisor metric output remain unverified. Grafana dashboard inventory was unavailable in the audit. No claim is made that removing the exporter preserves every existing alert or panel.

## Architecture options

| Option | Security | Coverage | Complexity and maintenance |
|---|---|---|---|
| Remove the exporter; use cAdvisor + node-exporter | Removes this exporter's Docker socket access. cAdvisor still has read-only host runtime mounts and is itself a privileged monitoring component; this does not establish that the whole stack has no Docker API access. | Good for running-container resource metrics and host metrics. Does not by itself guarantee stopped-container state, restart count, or the exporter's exact health/status series. cAdvisor's pinned build must be checked for needed health metrics. | Simplest service graph and fewest moving parts. Requires updating/removing queries and alerts that depend on `docker_container_*` series. |
| Retain exporter behind an endpoint-allowlisted proxy | Can block write methods and unrelated API areas, but a generic `/containers` allow switch is broad. Container inspect responses can include environment and other sensitive configuration, so transport-level endpoint allowlisting does not redact returned data. | Closest to current metric coverage; exporter needs list-all and per-container inspect semantics and may need version/image metadata calls. | Adds a proxy, image update and API compatibility work. Must maintain and test exact route/method allowlists. |
| Replace with a safer monitoring method | A purpose-built host-side collector can emit only approved fields and avoid giving an application container a general Docker socket. No such collector is currently verified as installed. | Can preserve required metrics if designed for them, including stopped-container state. | Requires development, packaging, and ongoing maintenance; more work than removing an unnecessary exporter. |

### Socket-proxy caveat

The commonly used Tecnativa proxy documents `POST=0` as method restriction, but its `CONTAINERS=1` setting enables the container API namespace. As of this review, upstream issue #182 reports that this broad GET namespace also allows container archive/export/log/top endpoints; its proposed fix is tracked separately as PR #183. A read-only socket mount or `POST=0` alone does not mitigate sensitive GET endpoints. Do not deploy the generic `CONTAINERS=1` configuration as the proposed allowlist. A proxy option requires a reviewed version containing the relevant deny rules (verified by tests) or a custom route policy that allows only the exact exporter calls and denies archive, export, logs, top, attach, exec, and all write methods. Also account for sensitive fields in `GET /containers/{id}/json` responses.

## Recommendation

Use cAdvisor and node-exporter as the default monitoring architecture, and remove `docker-health-exporter` plus its Prometheus scrape job only after a compatibility check confirms no required panel or alert depends on its metrics. This is the simplest way to remove the exporter's direct Docker API path. Preserve cAdvisor's existing scrape target and verify its actual pinned-version output for the required running-container resource and health metrics before changing the scrape configuration.

The audit does not reveal the owner's required dashboard/alert coverage, so cAdvisor-only equivalence cannot be asserted yet. If stopped-container state, restart counts, or exact `docker_container_*` series are required, do not substitute cAdvisor and silently lose those signals. First record the exact queries and define a purpose-built filtered collector or a narrowly tested proxy; the generic proxy's `CONTAINERS=1` setting is not acceptable without fixing and validating its broad GET exposure and response-data leakage.

The recommendation removes the exporter, not every Docker-related access in the monitoring stack. cAdvisor's current read-only runtime mounts and trust boundary need a separate review if the goal expands to eliminating all Docker API or host-runtime visibility from monitoring containers.
