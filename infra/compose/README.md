# Compose source tree

These files are sanitized local representations of the Compose configurations read from the server on 2026-11-12. They are **not approved deployment releases**. Pi-hole's configured web password is represented by a required external variable, and all Compose-time variables must be supplied from administrator-protected env files outside Git.

Before using any project for deployment, compare it with the then-current remote file, review the diff, confirm bind paths and backups, and promote the reviewed commit into an immutable root-owned release. Do not run `docker compose` against this writable working tree on the server.

Suggested protected env files for future root-owned release runs:

| Project | Runtime file | Required variables |
|---|---|---|
| `arr` | `/etc/homelab-ops/runtime-env/arr.env` | `PUID`, `PGID`, `TZ`, `UN_RADARR_API_KEY`, `UN_SONARR_API_KEY` |
| `pihole` | `/etc/homelab-ops/runtime-env/pihole.env` | `PIHOLE_WEBPASSWORD` |
| `monitoring` | `/etc/homelab-ops/runtime-env/monitoring.env` | `GRAFANA_ADMIN_USER`, `GRAFANA_ADMIN_PASSWORD` |
| `jellyfin` | none declared | none |

The env file path must be fixed by root-owned policy, never supplied by the request client. Validation must not print rendered Compose configuration.
