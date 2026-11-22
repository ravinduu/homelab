# Docker stacks

Ansible deploys these to `/opt/stacks/<stack>` on Debian.

| Stack | Services | Data |
|---|---|---|
| `arr` | qBittorrent, Prowlarr, Radarr, Sonarr, Unpackerr | `/var/lib/homelab/arr`, `/mnt/media` |
| `jellyfin` | Jellyfin | `/var/lib/homelab/jellyfin`, `/mnt/media/jellyfin-media` |
| `pihole` | Pi-hole | `/mnt/old-hdd/docker/pihole/etc-pihole` |
| `monitoring` | Prometheus, Grafana, node-exporter, cAdvisor, Docker health exporter | `prometheus_data`, `grafana_data` volumes |

Use [Ansible](../ansible/README.md) to deploy. `.env.example` files list each
stack's settings for manual use. Keep Pi-hole's Compose project name `pi-hole`.

Arr and monitoring images use pinned digests; Pi-hole and Jellyfin use `latest`.
Media services need `/mnt/media` mounted; Jellyfin also needs `/dev/dri/renderD128`.
Monitoring uses host devices and the Docker socket, so it runs on the Debian host.

Access Grafana and Prometheus from the Mac:

```sh
ssh -N -L 3000:127.0.0.1:3000 -L 9090:127.0.0.1:9090 homelab-terraform
```

Open `http://localhost:3000` or `http://localhost:9090`.
