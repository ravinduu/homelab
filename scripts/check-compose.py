#!/usr/bin/env python3
"""Validate the Mac checkout with Compose locally or over read-only SSH.

Only synthetic environment values and Compose source travel over stdin. This
does not copy files to the server, contact registries, or change containers.
"""

import argparse
import os
from pathlib import Path
import shlex
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ("arr", "jellyfin", "monitoring", "pihole")
VALUES = {
    "PUID": "1000", "PGID": "1000", "TZ": "Asia/Colombo",
    "WEB_BIND_IP": "192.168.1.10", "RENDER_GID": "992",
    "UN_RADARR_API_KEY": "validation-only", "UN_SONARR_API_KEY": "validation-only",
    "PIHOLE_WEBPASSWORD": "validation-only", "GRAFANA_ADMIN_USER": "validation-only",
    "GRAFANA_ADMIN_PASSWORD": "validation-only", "COMPOSE_DISABLE_ENV_FILE": "1",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ssh", metavar="ALIAS", help="use Compose on this SSH host, without writes")
    args = parser.parse_args()
    if args.ssh and args.ssh.startswith("-"):
        parser.error("SSH alias must not begin with a dash")
    for project in PROJECTS:
        directory = ROOT / "docker" / project
        project_directory = (f"/tmp/homelab-compose-validation/{project}"
                             if args.ssh else str(directory))
        compose = ["docker", "compose", "--env-file", "/dev/null", "--project-directory",
                   project_directory, "-f", "-", "config", "--quiet"]
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
        print(f"{project}: Compose configuration valid")
    print("All four stacks validated. No runtime changes made.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"check-compose: {error}", file=sys.stderr)
        sys.exit(1)
