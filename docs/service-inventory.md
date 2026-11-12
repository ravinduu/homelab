# Service Inventory

**Last observed:** 2026-11-12 (Asia/Colombo)  
**Source:** [Read-only homelab audit](../reports/homelab-audit.md)

The audit observed 12 running containers and one exited `hello-world` container. Four running containers reported Docker health `healthy`; eight had no configured Docker health check, which means health was unknown rather than failed.

| Service group | Observed services | Notes |
|---|---|---|
| Media | Jellyfin | Healthy container; media mount was read-only. Published TCP 8096 and UDP 7359 on all interfaces. |
| ARR/downloads | qBittorrent, Prowlarr, Radarr, Sonarr, Unpackerr | On `arr-network`; several web interfaces and torrent ports were published on all interfaces. Images used mutable `latest` tags. |
| Monitoring | Prometheus, Grafana, cAdvisor, node-exporter, docker-health-exporter | Four Prometheus targets were up. Grafana was loopback-bound; Prometheus was published on all interfaces. Exporter had read-write Docker socket access. Compose and scrape configuration remain inaccessible to `agent`; see [Docker monitoring security review](docker-monitoring-security.md). |
| DNS | Pi-hole | Host networking; DNS and HTTP(S) listeners were observed. |
| One-off | `sleepy_gagarin` (`hello-world`) | Exited; no service impact observed. |

This is a dated snapshot, not a live inventory. The audit wrapper intentionally omitted host bind source paths, volume names, environment variables, labels, and command lines. Refer to the report for exact observed image references, ports, health state, evidence, limitations, and risk findings.
