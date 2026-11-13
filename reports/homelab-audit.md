# Homelab Infrastructure Audit

**Inspection date:** 2026-11-12 (Asia/Colombo)  
**Host/account:** `home-server-01`, SSH as `agent`  
**Method:** Read-only SSH inspection and the approved `/usr/local/sbin/homelab-inventory` wrapper. No remote configuration or service changes were made.

## 1. Executive Summary

The Debian 13 server was operational during inspection: Docker and containerd were active, `systemctl --failed` listed no failed units, memory and filesystem capacity were comfortable, and all four Prometheus scrape targets were up. The approved inventory returned 12 running containers and one exited `hello-world` container. Four running containers report Docker health `healthy`; the other eight have no configured Docker health state.

The main risks to address are:

| Priority | Finding |
|---|---|
| **High** | `docker-health-exporter` can access the Docker API through its mounted socket. Follow-up review confirmed the socket file is bind-mounted read-only, but that does not restrict Docker API methods; the earlier read-write mount characterization was incorrect. |
| **High** | Prometheus and several application/admin services bind to every host interface. Host firewall rules and router forwarding could not be verified. |
| **High** | `/mnt/media` contains root-like system directories as well as media/download data; the separate Samba `Old-HDD` share actually resolves to the OS root filesystem. Storage/data placement needs owner review. |
| **Medium** | No host backup schedule, backup tool, destination, or restore evidence was visible to `agent`; media persistence and recovery are therefore unverified. |
| **Medium** | The point-in-time Linux I/O pressure snapshot was elevated even though capacity is ample. Repeat measurement is needed to determine whether this reflects a sustained storage bottleneck. |
| **Medium** | Eight running containers have no Docker health check; their `health=null` state is unknown, not a failure. |

These observations do **not** establish internet exposure: router/NAT rules and external reachability were not inspected.

## 2. Hardware and Operating System

| Item | Verified observation |
|---|---|
| OS/kernel | Debian GNU/Linux 13.6 (trixie); Linux `6.12.105+deb13-amd64`, x86_64 |
| CPU | Intel Core i5-7200U, 2 cores / 4 threads, 2.50 GHz base, reported maximum 3.10 GHz |
| Memory | 11 GiB total; 1.8 GiB used, 8.0 GiB free, 9.8 GiB available at collection |
| Swap | 6.2 GiB configured, none used |
| Uptime/load | About 1 h 20 min; load averages 0.13, 0.26, 0.31 |
| Systemd | Docker, containerd, SSH, Samba, cron, timesyncd and core system services active; no failed units reported |
| Journal | 16 MiB reported for active and archived journals |

The host showed no current CPU or memory capacity pressure. `/proc/pressure` showed memory full pressure at zero, while I/O pressure reported `avg60=24.22` and `avg300=19.62` in the captured sample. This may indicate recent I/O waiting, but a single short snapshot is not enough to establish a persistent bottleneck.

## 3. Storage Architecture

| Device/mount | Observed layout and usage |
|---|---|
| `/dev/sda` (`DIGIRICH DGSSDM22`, 119.2 GiB) | EFI partition, ext4 root (`/dev/sda2`, 110 GiB; 11 GiB used, 94 GiB available), and 6.2 GiB swap |
| `/dev/sdb` (`TOSHIBA MQ01ABD100`, 931.5 GiB) | ext4 `/dev/sdb2` mounted read-write at `/mnt/media`, 916 GiB filesystem; 153 GiB used (18%), 717 GiB available |
| `/boot/efi` | `/dev/sda1`, 975 MiB; 1% used |

The `/mnt/media` root is owned by `root:root`. Its top level includes `arr-downloads` (`ravindu:ravindu`, 5.6 GiB) and `jellyfin-media` (`root:root`, 3.8 GiB), but also directories named `etc`, `home`, `root`, `var`, `usr`, `opt`, `srv`, and other root-filesystem-like paths. The agent account cannot read some of those paths. A broad size walk was stopped after permission errors; file contents were not inspected. The unexplained layout and the gap between the two named media directories (9.4 GiB combined) and total used space warrant owner review before relying on this disk as a media-only volume.

The Samba `[Old-HDD]` share is configured with path `/mnt/old-hdd`, writable mode, and `valid users = ravindu`. That path exists but `findmnt` resolves it to `/dev/sda2` (`/`), not a separate HDD mount. Samba also sets `force user/group = ravindu` and create/directory masks to `0777`. Confirm the intended backing storage and whether these permissive creation masks are needed.

Docker's persistent targets visible through the approved inventory include Grafana `/var/lib/grafana` and Prometheus `/prometheus` named volumes, plus service bind mounts. Host-side bind source paths and volume names are intentionally omitted by the inventory, so their exact locations, owners, and backup coverage could not be verified. `smartctl` and `iostat` were unavailable to the agent; disk health and detailed device throughput were not assessed.

## 4. Docker Infrastructure

`docker.service` and `containerd.service` were active. Docker client version reported by the denied direct CLI attempt was `29.8.0`; the daemon version could not be queried directly. The approved wrapper was executable through the exact no-argument sudo rule and completed successfully. It returns selected metadata only, excluding environment variables, labels, command lines, host mount sources, volume names, and secrets. At initial audit time, deployment files were not found in the accessible `/home/agent`, `/opt`, or `/srv` search scope and `/home/ravindu` was inaccessible. Follow-up permissions made `/home/ravindu/Developer/homelab/monitoring` readable to `agent`; the monitoring Compose and Prometheus files were subsequently reviewed without reading `.env`.

| Container | Image reference | State / health | Restart | Network | Host-published ports / notes |
|---|---|---|---|---|---|
| `grafana` | `grafana/grafana:13.2.1` | Running / healthy | `unless-stopped` | `monitoring-network` | `127.0.0.1:3000` only; Grafana data volume; provisioning bind is read-only |
| `cadvisor` | `ghcr.io/google/cadvisor:v0.60.6` | Running / healthy | `unless-stopped` | `monitoring-network` | No host binding; host `/rootfs`, `/sys`, `/dev/disk`, `/var/run`, `/var/lib/docker` mounts are read-only |
| `prometheus` | `prom/prometheus:v3.14.0` | Running / no health check | `unless-stopped` | `monitoring-network` | `0.0.0.0:9090` and `[::]:9090`; config bind read-only; data volume |
| `docker-health-exporter` | `fviolence/docker-health-exporter:v1.0` | Running / no health check | `unless-stopped` | `monitoring-network` | No host port binding; socket file bind is read-only (`:ro`), but Docker API methods are not constrained by that mount flag |
| `node-exporter` | `prom/node-exporter:v1.12.1` | Running / no health check | `unless-stopped` | `monitoring-network` | No host binding; host proc/root/sys mounts are read-only |
| `qbittorrent` | `lscr.io/linuxserver/qbittorrent:latest` | Running / no health check | `unless-stopped` | `arr-network` | TCP/UDP 6881 and TCP 8080 on all IPv4/IPv6 interfaces; `/config` and `/data` read-write |
| `prowlarr` | `lscr.io/linuxserver/prowlarr:latest` | Running / no health check | `unless-stopped` | `arr-network` | TCP 9696 on all IPv4/IPv6 interfaces; `/config` read-write |
| `radarr` | `lscr.io/linuxserver/radarr:latest` | Running / no health check | `unless-stopped` | `arr-network` | TCP 7878 on all IPv4/IPv6 interfaces; `/config` and `/data` read-write |
| `sonarr` | `lscr.io/linuxserver/sonarr:latest` | Running / no health check | `unless-stopped` | `arr-network` | TCP 8989 on all IPv4/IPv6 interfaces; `/config` and `/data` read-write |
| `unpackerr` | `golift/unpackerr:latest` | Running / no health check | `unless-stopped` | `arr-network` | No host port binding; `/config` and `/data` read-write |
| `pihole` | `pihole/pihole:latest` | Running / healthy | `unless-stopped` | Host network | Host listeners include DNS 53 TCP/UDP and HTTP(S) 80/443 |
| `jellyfin` | `jellyfin/jellyfin:latest` | Running / healthy | `unless-stopped` | `jellyfin_default` | TCP 8096 and UDP 7359 on all IPv4/IPv6 interfaces; `/media` read-only, `/cache` and `/config` read-write |
| `sleepy_gagarin` | `hello-world` | Exited / no health check | `no` | `bridge` | One stopped one-off container; no service impact observed |

The network memberships show separation between monitoring, ARR, and Jellyfin, while Pi-hole uses host networking. They establish shared network visibility, not application ordering or explicit service dependencies. The inventory does not expose `depends_on`, Compose project paths, network options, or network-level access rules, so those were not verified. Eight running containers have `health=null`, meaning no health status was available.

Several application images use the mutable `latest` tag (Pi-hole, Jellyfin, qBittorrent, Prowlarr, Radarr, Sonarr, and Unpackerr). Their precise deployed build cannot be inferred from that tag alone; use a deliberate update process and record explicit versions/digests.

## 5. Service Inventory

| Service | Purpose / deployment | Operational evidence | Issue or limitation |
|---|---|---|---|
| Jellyfin | Media server; Docker container on `jellyfin_default` | Container healthy; local HTTP probe on 8096 returned 302; TCP 8096 and UDP 7359 published on all interfaces | Media source is a read-only bind, but host source path is intentionally hidden; no application health beyond its container check was assessed |
| Pi-hole | DNS filtering/local resolver; host-network Docker container | Container healthy; direct DNS query to `127.0.0.1` resolved `pi.hole` to `127.0.0.1`; host DNS listeners on 53; ports 80/443 returned 403 | Server `/etc/resolv.conf` points to router `192.168.1.1`, not Pi-hole; whether the router forwards DNS to Pi-hole is unknown |
| Prometheus | Metrics collection; Docker on `monitoring-network` | API build info returned v3.14.0; 4 active targets, all `up`; TCP 9090 bound to all interfaces | No container health check; target configuration file is not accessible to `agent`; API/UI authentication policy beyond local observations was not assessed |
| Grafana | Metrics dashboards; Docker on `monitoring-network` | Container healthy; `/api/health` reported database `ok`, version 13.2.1; TCP 3000 bound only to loopback | Dashboard search returned HTTP 401, so dashboard inventory was not available without credentials; no credentials were requested or used |
| ARR stack | Prowlarr indexer management, Radarr movies, Sonarr series, qBittorrent downloads, Unpackerr extraction | All five containers running on shared `arr-network`; local web probes returned 302 for Prowlarr/Radarr/Sonarr and 200 for qBittorrent 8080 | Interfaces bind all host IPv4/IPv6 interfaces; no health checks; dependencies beyond shared network and shared `/data` mounts are not visible |

No reverse proxy or VPN was positively identified. Ports 80/443 answered 403; process-name inspection showed Pi-hole FTL and Samba but did not reliably map every listening socket to a process. The host has one physical LAN interface (`192.168.1.10/24`), Docker bridges `172.17.0.0/16` through `172.22.0.0/16`, and default gateway `192.168.1.1`. No active VPN interface appeared in the interface listing; VPN configuration was not inspected.

## 6. Networking Architecture

- Host interface: `enp1s0`, `192.168.1.10/24`; default route via `192.168.1.1`.
- Host DNS resolver: `192.168.1.1`. Pi-hole itself answers on host port 53 and responds to a direct local query, but gateway-to-Pi-hole forwarding was not verified.
- Docker bridges: networks observed from interface/routes include `172.17.0.0/16` through `172.22.0.0/16`; several bridges were down. The approved inventory showed attached service network names `monitoring-network`, `arr-network`, `jellyfin_default`, `host`, and `bridge`.
- Host TCP listeners included wildcard ports 22, 53, 80, 443, 139, 445, 6881, 7878, 8080, 8096, 8989, 9090, and 9696. Grafana's 3000 listener was loopback-only.
- Host UDP listeners included wildcard 53, 123, 6881, and 7359; NetBIOS 137/138 and DHCP client 68 were also present.
- The direct Docker API was denied to `agent`; only the approved inventory wrapper was used for container metadata.
- Router port forwarding, VLANs, Wi-Fi/client isolation, and reachability from outside the LAN were not checked.

## 7. Security Assessment

**HIGH — Broad Docker API access from monitoring containers.** Follow-up inspection confirmed `docker-health-exporter` mounts `/var/run/docker.sock:/var/run/docker.sock:ro`, but the read-only bind only protects the socket filesystem entry; it does not make the Docker HTTP API read-only. A compromised exporter can still attempt Docker API operations allowed by the daemon. The exporter has no host-published port, but shares `monitoring-network`; Prometheus is published on all host interfaces. cAdvisor also mounts `/var/run` read-only and runs with `privileged: true`, so the broader monitoring trust boundary must be reviewed. The earlier report's read-write mount wording was incorrect.

**HIGH — Wide service bindings with firewall state unknown.** Prometheus 9090, qBittorrent 8080/6881, Prowlarr 9696, Radarr 7878, Sonarr 8989, Jellyfin 8096/7359, DNS, SSH, and SMB listeners bind wildcard IPv4/IPv6 addresses. `nft`, `iptables`, `ufw`, and `firewalld` were unavailable/inactive to the audit account. This does not prove that no kernel filtering exists, but the effective host policy could not be verified. Restrict listeners to intended LAN/VLANs and verify router filtering/forwarding before assuming they are private.

**HIGH — SMB exposure deserves explicit boundary review.** Samba listens on 139/445 across interfaces and Docker bridge addresses. The configured `Old-HDD` share is writable for `ravindu` and uses `0777` creation masks. Confirm that SMB is not reachable from untrusted networks and that broad mode bits are intentional.

**MEDIUM — Unexpected data placement on the media disk.** `/mnt/media` contains system-like directories and the named Samba HDD share points at the root SSD. This may be intentional legacy data, but it increases the risk of confusing backup scope, sharing unintended files, or filling the wrong filesystem. Review the layout and share target before changing anything.

**LOW — SSH configuration needs effective-user confirmation.** The readable configuration contains `PasswordAuthentication no`, `PubkeyAuthentication yes`, `KbdInteractiveAuthentication no`, and a top-level `X11Forwarding yes`; a later `Match`-scoped block has different directives. The audit account did not obtain a usable filtered `sshd -T` result for `agent`, so effective per-user settings are not asserted here. Confirm the effective policy with an administrator. SSH accepted the current key-based session.

`agent` is not in `sudo` or `docker` groups. `sudo -n -l` exposed only the no-argument `/usr/local/sbin/homelab-inventory` rule. Direct Docker API access remained denied. No password hashes, credentials, environment variables, or secrets were read.

## 8. Monitoring and Observability

- Prometheus v3.14.0 has four active scrape targets: `prometheus`, `node`, `cadvisor`, and `docker-health`; all four were `up`, with zero dropped targets.
- Grafana v13.2.1 is healthy at the container and database-health levels. Its listener is loopback-only at `127.0.0.1:3000`. Dashboard search returned 401; dashboard names and availability therefore remain unverified.
- cAdvisor and node-exporter are running and share `monitoring-network`; their host mounts are read-only in the approved inventory.
- The Docker health exporter is running, but its own Docker health state is absent. Its socket bind is read-only at the filesystem level, while Docker API methods remain unrestricted (see High finding).
- Follow-up read-only access located the monitoring files at `/home/ravindu/Developer/homelab/monitoring`. Prometheus uses a 15-second scrape interval and targets `prometheus:9090`, `node-exporter:9100`, `cadvisor:8080`, and `docker-health-exporter:9066`; all were up during the follow-up. The project contains no alert rule or dashboard files; Grafana's persisted dashboard inventory remains unavailable without credentials.
- No independent alerting destination or alert rules were verified. Consider host/disk SMART monitoring, backup-job success alerts, container restart alerts, and alerting on targets missing for more than a short interval.

## 9. Backup and Disaster Recovery

No backup timers or accessible backup directories were found in the inspected `/etc/cron.d`, `/etc/cron.daily`, `/home/agent`, `/opt`, or `/srv` scope. Common CLI tools `restic`, `borg`, `kopia`, `duplicity`, and `rclone` were not found in the agent's command path. This does **not** establish that backups do not exist elsewhere or are not managed externally. No backup destination, retention policy, application-consistent database backup, or restore test could be verified.

The media HDD is a single observed data disk; no second local replica was identified in the inspected mount table. Treat recovery coverage for media, downloads, Docker volumes, Pi-hole configuration, and Grafana/Prometheus data as unknown until an owner verifies backup records and a restore test.

## 10. Identified Issues and Risks

1. **High:** Broad Docker API access is available to the health exporter through a read-only socket bind; cAdvisor also has privileged execution and read-only host runtime mounts. A read-only bind is not an API method allowlist.
2. **High:** Multiple administration and application ports bind to all interfaces while firewall/router policy is unknown.
3. **High:** SMB is listening broadly; its writable share uses `0777` creation masks and the configured “Old-HDD” path is on `/`.
4. **Medium:** `/mnt/media` includes root-like directories and substantial unexplained used space; accessible named media folders account for only 9.4 GiB of the 153 GiB reported used.
5. **Medium:** No backup or restore evidence was visible to the audit account; a single media HDD is a data-loss single point of failure if no external backup exists.
6. **Medium:** I/O pressure readings were elevated in one sample; disk capacity is healthy, but latency/throughput health needs a time series.
7. **Medium:** Eight running containers have no Docker health checks, reducing visibility into application-level failure.
8. **Low:** Mutable `latest` image references reduce deployment reproducibility and make it difficult to tell which version is running from this inventory.
9. **Informational:** One exited `hello-world` container remains; no operational effect was observed.

## 11. Recommended Improvements

1. **High:** Review and reduce Docker API exposure. A `:ro` socket bind does not restrict API methods. Prefer removing the redundant exporter if its unique series are not required, or use a method- and endpoint-filtered proxy/collector that minimizes response data. Also review cAdvisor's `privileged: true` and `/var/run` mount. Verify monitoring-network reachability as part of that design.
2. **High:** Establish the intended LAN/VLAN exposure matrix for every listener. Confirm host firewall rules and router/NAT policy from an authorized administrative session; restrict Prometheus and ARR/download interfaces to trusted networks and require suitable authentication for any remote access.
3. **High:** Confirm Samba's `Old-HDD` target, backing filesystem, and intended write permissions. Review `0777` masks and verify SMB cannot be reached from untrusted networks.
4. **Medium:** Have the data owner classify the contents of `/mnt/media` and determine whether it is intentionally a root-like archive. Do not delete or move data as part of this audit. Clarify the media/download directory layout and map it against the hidden container bind sources.
5. **Medium:** Document backup scope, off-host destination, schedules, retention, encryption, and last successful restore for Docker volumes, service configuration, and media metadata. Add backup success/failure monitoring.
6. **Medium:** Add suitable health checks to the eight containers with `health=null`, where the application supports a reliable health endpoint. Ensure Prometheus alerting covers target failure and unexpected container stops/restarts.
7. **Medium:** Trend I/O pressure and disk latency before treating the single sample as a bottleneck; obtain disk SMART data and `iostat`/equivalent through an authorized maintenance workflow.
8. **Low:** Replace `latest` tags with reviewed version pins or digests and document the update/rollback process.
9. **Low:** Verify effective SSH settings for `agent`, including X11 forwarding, using an administrator's config test; retain key-based access and confirm password/keyboard-interactive authentication policy.
10. **Informational:** Verify whether the router forwards DNS to Pi-hole, since the server itself uses `192.168.1.1` as its resolver while Pi-hole answers locally.

## 12. Suggested Future Architecture

- Keep the existing separation between monitoring, ARR, and Jellyfin networks, and document which peers require communication. Do not attach unrelated services to shared networks by default.
- Remove broad Docker socket access from application containers; if Docker metadata is required, mediate it through a minimal API allowlist.
- Put administrative UIs behind trusted-network restrictions and authentication; keep Grafana loopback-bound unless a reviewed proxy/access design requires otherwise. Restrict Prometheus and ARR ports instead of exposing all interfaces by default.
- Treat `/mnt/media` as a dedicated data mount with a clear documented directory tree. Keep OS/archive data distinct from media and downloads, and ensure Samba shares point to the intended mounted filesystem.
- Maintain off-host backups for Docker persistent data and important media metadata, with scheduled restore verification and alerting.
- Pin container image versions, add health checks, define Compose project locations/dependencies in documented manifests, and monitor CPU, memory, disk latency, filesystem headroom, SMART health, and backup outcomes.
- Document the DNS flow end to end (server resolver, router DHCP/DNS advertisement, Pi-hole upstream) so local DNS behavior is predictable.

## Evidence and Limitations

Key evidence commands included `hostname`, `id`, `/etc/os-release`, `uname -a`, `uptime`, `lscpu`, `free -h`, `lsblk`, `df -hT`, `findmnt`, `ip -brief address`, `ip route`, `/etc/resolv.conf`, `systemctl --type=service --state=running`, `systemctl --failed`, `ss -tuln`, `systemctl list-timers`, `journalctl --disk-usage`, filtered `sshd_config`/`testparm` output, status-only local HTTP probes, and the approved `sudo -n /usr/local/sbin/homelab-inventory` output. Prometheus `/api/v1/targets` and build-info endpoints were queried locally; Grafana `/api/health` was queried without credentials.

Direct `docker` access remains denied, so no general Docker CLI, Compose listing, network/volume listing, or daemon configuration inspection was performed. The monitoring Compose and Prometheus files were later read through the newly accessible path and queried through the local Prometheus API; the approved inventory still withholds host bind sources. Host firewall rule tables, SMART status, remote internet reachability, router forwarding, external backups, Grafana dashboards, and effective per-user SSH evaluation remain unverified. The follow-up confirmed that the original audit's description of the exporter socket bind as read-write was incorrect: Compose specifies `:ro`, and the inventory reports `.RW=false`; Docker API methods remain unrestricted through that socket.
