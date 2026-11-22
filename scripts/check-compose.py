#!/usr/bin/env python3
"""Validate the Mac checkout with Compose locally or over read-only SSH.

Only synthetic environment values and Compose source travel over stdin. This
does not copy files to the server, contact registries, or change containers.
"""

import argparse
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = {
    "arr": {"qbittorrent", "prowlarr", "radarr", "sonarr", "unpackerr"},
    "jellyfin": {"jellyfin"},
    "monitoring": {
        "prometheus", "grafana", "node-exporter", "cadvisor", "docker-health-exporter"
    },
    "pihole": {"pihole"},
}
VALUES = {
    "PUID": "1000", "PGID": "1000", "TZ": "Asia/Colombo",
    "WEB_BIND_IP": "192.168.1.10", "RENDER_GID": "992",
    "UN_RADARR_API_KEY": "validation-only", "UN_SONARR_API_KEY": "validation-only",
    "PIHOLE_WEBPASSWORD": "validation-only", "GRAFANA_ADMIN_USER": "validation-only",
    "GRAFANA_ADMIN_PASSWORD": "validation-only", "COMPOSE_DISABLE_ENV_FILE": "1",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(model, project):
    require(model["name"] == ("pi-hole" if project == "pihole" else project),
            "unexpected project identity")
    services = model["services"]
    require(set(services) == PROJECTS[project], "unexpected service inventory")
    for name, service in services.items():
        require(re.search(r"@sha256:[0-9a-f]{64}$", service["image"]),
                f"{name}: image must be pinned by digest")
        require(service["restart"] == "unless-stopped", f"{name}: restart policy missing")
        logging = service["logging"]
        require(logging["driver"] == "local" and
                logging["options"] == {"max-size": "10m", "max-file": "3"},
                f"{name}: bounded logging missing")
        for mount in service.get("volumes", []):
            if mount["type"] == "bind":
                require(mount.get("bind", {}).get("create_host_path") is False,
                        f"{name}: bind must not create a missing host path")
    if project == "monitoring":
        for volume in ["grafana_data", "prometheus_data"]:
            require(model["volumes"][volume].get("external") is True and
                    model["volumes"][volume]["name"] == volume,
                    f"{volume}: existing data volume must be external and retain its name")
        for service in ["grafana", "prometheus"]:
            require(all(port.get("host_ip") == "127.0.0.1"
                        for port in services[service]["ports"]),
                    f"{service}: management port must bind to localhost")
    if project == "pihole":
        require(services["pihole"]["network_mode"] == "host" and
                not services["pihole"].get("ports"),
                "host-network Pi-hole must not declare port mappings")
    if project == "jellyfin":
        media = next(m for m in services["jellyfin"]["volumes"] if m["target"] == "/media")
        require(media.get("read_only") is True, "Jellyfin media must stay read-only")
    expected_network = {"arr": "arr-network", "monitoring": "monitoring-network"}.get(project)
    if expected_network:
        require(model["networks"][project]["name"] == expected_network,
                "existing Compose network identity changed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ssh", metavar="ALIAS", help="use Compose on this SSH host, without writes")
    args = parser.parse_args()
    if args.ssh and args.ssh.startswith("-"):
        parser.error("SSH alias must not begin with a dash")
    for project in PROJECTS:
        directory = ROOT / "infra" / "compose" / project
        project_directory = (f"/tmp/homelab-compose-validation/{project}"
                             if args.ssh else str(directory))
        compose = ["docker", "compose", "--env-file", "/dev/null", "--project-directory",
                   project_directory, "-f", "-", "config", "--format", "json"]
        if args.ssh:
            # Relative bind paths resolve for schema validation only. No files
            # are written at this synthetic project directory on the server.
            command = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
                       "-o", "StrictHostKeyChecking=yes", args.ssh,
                       shlex.join(["env", "-i", "PATH=/usr/local/bin:/usr/bin:/bin",
                                   *[f"{key}={value}" for key, value in VALUES.items()], *compose])]
            environment = None
        else:
            command = compose
            environment = {key: value for key, value in os.environ.items()
                           if not key.startswith("COMPOSE_")}
            environment.update(VALUES)
        result = subprocess.run(command, input=(directory / "compose.yaml").read_text(),
                                text=True, capture_output=True, env=environment, timeout=45)
        if result.returncode:
            raise ValueError(f"{project}: Compose validation failed\n{result.stderr.strip()}")
        validate(json.loads(result.stdout), project)
        print(f"{project}: Compose schema and storage/logging/network checks passed")
    print("Validated all 12 services. No runtime changes made.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        print(f"check-compose: {error}", file=sys.stderr)
        sys.exit(1)
