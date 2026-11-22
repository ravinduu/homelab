#!/bin/sh
# Read-only preflight for the existing Debian host; no mkdir/chown/pulls.
set -eu

fail() {
    printf 'preflight: %s\n' "$*" >&2
    exit 1
}

[ "$(uname -s)" = Linux ] || fail 'run this on the Debian Docker host'
[ "$(docker info --format '{{.OSType}}')" = linux ] || fail 'Linux Docker is required'
mountpoint -q /mnt/media || fail '/mnt/media must be mounted before starting media services'

for directory in \
    /var/lib/homelab/arr/qbittorrent \
    /var/lib/homelab/arr/prowlarr \
    /var/lib/homelab/arr/radarr \
    /var/lib/homelab/arr/sonarr \
    /var/lib/homelab/arr/unpackerr \
    /var/lib/homelab/jellyfin/config \
    /var/lib/homelab/jellyfin/cache \
    /mnt/media/jellyfin-media \
    /mnt/old-hdd/docker/pihole/etc-pihole \
    /proc /sys /var/run /var/lib/docker /dev/disk
do
    [ -d "$directory" ] || fail "missing directory: $directory"
done

[ -c /dev/dri/renderD128 ] || fail 'Jellyfin render device is missing'
[ -c /dev/kmsg ] || fail 'cAdvisor kernel message device is missing'
[ -S /var/run/docker.sock ] || fail 'Docker socket is missing'
render_gid=$(stat -c '%g' /dev/dri/renderD128)
[ "$render_gid" = "${RENDER_GID:-992}" ] || fail "set RENDER_GID to $render_gid in jellyfin.env"

for volume in prometheus_data grafana_data; do
    docker volume inspect "$volume" >/dev/null || fail "missing existing volume: $volume"
done

printf '%s\n' 'Host paths, media mount, devices, render group and existing monitoring volumes passed.'
printf '%s\n' 'Application credentials, backups, free space and database integrity require separate verification.'
