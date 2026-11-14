#!/usr/bin/env python3
"""Submit narrowly-scoped requests to the separately installed homelab gateway.

This client is not a security boundary. The root-owned remote gateway must
repeat all validation and enforce restart approval policy independently.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SSH_ALIAS = "home-server-agent"
REMOTE_GATEWAY = "/usr/local/sbin/homelab-ops"
POLICY_FILE = Path(__file__).resolve().parents[2] / "infra" / "policy" / "allowlist.json"
POLICY = json.loads(POLICY_FILE.read_text(encoding="utf-8"))
RESTART_SERVICES = frozenset(POLICY["restart_services"])


@dataclass(frozen=True)
class Request:
    operation: str
    subject: str | None = None

    def remote_argv(self) -> list[str]:
        argv = ["sudo", "-n", REMOTE_GATEWAY, self.operation]
        if self.subject is not None:
            argv.append(self.subject)
        return argv


def parse_request(argv: list[str]) -> tuple[Request, bool]:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--send", action="store_true", help="send request over SSH (default: print only)")
    sub = parser.add_subparsers(dest="operation", required=True)
    sub.add_parser("status", help="request allowlisted service status")
    restart = sub.add_parser("restart", help="request restart of one allowlisted service")
    restart.add_argument("service")

    args = parser.parse_args(argv)
    if args.operation == "status":
        request = Request("status")
    elif args.operation == "restart":
        if args.service not in RESTART_SERVICES:
            parser.error(f"service is not allowlisted: {args.service!r}")
        request = Request("restart", args.service)
    return request, args.send


def main(argv: list[str] | None = None) -> int:
    request, send = parse_request(sys.argv[1:] if argv is None else argv)
    remote_argv = request.remote_argv()
    ssh_argv = ["ssh", "--", SSH_ALIAS, *remote_argv]
    if not send:
        print("DRY RUN: no remote request sent")
        print(" ".join(shlex.quote(part) for part in ssh_argv))
        print("The root-owned gateway must independently enforce policy and approval.")
        return 0
    return subprocess.run(ssh_argv, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
