#!/usr/bin/python3 -I
"""Administrator-only creator for one short-lived Jellyfin restart approval."""

from __future__ import annotations

import os
import sys
import syslog
from pathlib import Path

from ..approvals.store import ApprovalError, check_protected_path, create_restart_approval

syslog.openlog("homelab-ops-approval", syslog.LOG_PID, syslog.LOG_AUTHPRIV)

APPROVER_PATH = Path("/usr/local/sbin/homelab-ops-approve-restart")
COMMON_PATH = Path("/usr/local/sbin/homelab_ops_common.py")
PACKAGE_DIR = Path("/usr/local/lib/homelab_ops")


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if arguments:
        print("usage: homelab-ops-approve-restart", file=sys.stderr)
        return 64
    if os.geteuid() != 0:
        print("approval tool must be run by an administrator", file=sys.stderr)
        return 77
    try:
        check_protected_path(APPROVER_PATH, file_mode=0o750)
        check_protected_path(COMMON_PATH, file_mode=0o640)
        for module_path in (
            PACKAGE_DIR / "__init__.py",
            PACKAGE_DIR / "approvals" / "__init__.py",
            PACKAGE_DIR / "approvals" / "store.py",
            PACKAGE_DIR / "gateway" / "__init__.py",
            PACKAGE_DIR / "gateway" / "core.py",
            PACKAGE_DIR / "gateway" / "approval_cli.py",
        ):
            check_protected_path(module_path, file_mode=0o640)
        approval_path = create_restart_approval(requester="agent")
    except ApprovalError as error:
        syslog.syslog(
            syslog.LOG_AUTHPRIV | syslog.LOG_WARNING, "homelab-ops approval creation denied"
        )
        print(f"homelab-ops: {error}", file=sys.stderr)
        return 1
    syslog.syslog(
        syslog.LOG_AUTHPRIV | syslog.LOG_NOTICE,
        "homelab-ops administrator created jellyfin restart approval",
    )
    print(f"Single-use restart approval created; valid for 120 seconds: {approval_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
