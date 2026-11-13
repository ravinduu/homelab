# Infrastructure Overview

**Last observed:** 2026-11-12 (Asia/Colombo)  
**Source:** [Read-only homelab audit](../reports/homelab-audit.md)

The audit observed `home-server-01` running Debian GNU/Linux 13.6 on x86_64, with Docker/containerd, Samba, and system services active. The host had an SSD-backed root filesystem and a 1 TB-class HDD mounted at `/mnt/media`. These are dated observations, not guarantees of current state.

## Verified layout

- Docker networks observed: `monitoring-network`, `arr-network`, and `jellyfin_default`; Pi-hole used host networking.
- Prometheus, Grafana, cAdvisor, node-exporter, and a Docker health exporter formed the monitoring stack.
- Jellyfin and the ARR/download services were separated across the observed Docker networks.
- The Samba `Old-HDD` share path `/mnt/old-hdd` resolved to the root filesystem during inspection, not a separate HDD mount.

## Items requiring owner review

- Follow-up inspection found the Docker health exporter socket bind is `:ro`; Docker API calls through the mounted Unix socket are still not restricted to read-only methods. cAdvisor also runs `privileged: true` with read-only host runtime mounts, so the monitoring trust boundary needs review.
- The monitoring Compose and Prometheus config are now readable to `agent` under `/home/ravindu/Developer/homelab/monitoring`; the approved inventory still hides host bind sources. Other accessible Compose files under `/mnt/media/home/ravindu` include a LocalStack socket bind, but no LocalStack container appeared in the live inventory, so that file's deployment status is unverified. See [Docker monitoring security review](docker-monitoring-security.md) and [remediation plan](../reports/docker-socket-remediation-plan.md).
- Several service ports listened on all host interfaces; firewall and router/NAT exposure were not verified.
- `/mnt/media` contained root-like directory names and more used space than the two named media directories accounted for. No data was changed or inspected beyond accessible metadata.
- Backup schedules, destinations, coverage, and restore success were not verified.
- A single captured I/O pressure sample was elevated; persistence was not established.

See the audit for detailed evidence, limitations, and prioritized recommendations. Recheck time-sensitive observations before making operational decisions.
