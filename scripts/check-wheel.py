#!/usr/bin/env python3
"""Check that a built wheel contains the canonical importable package."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

REQUIRED = {
    "homelab_ops/__init__.py",
    "homelab_ops/client.py",
    "homelab_ops/approvals/__init__.py",
    "homelab_ops/approvals/store.py",
    "homelab_ops/gateway/__init__.py",
    "homelab_ops/gateway/core.py",
    "homelab_ops/gateway/policy.py",
    "homelab_ops/gateway/approval_cli.py",
}


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: check-wheel.py WHEEL", file=sys.stderr)
        return 2
    wheel = Path(argv[1])
    try:
        with zipfile.ZipFile(wheel) as archive:
            members = set(archive.namelist())
    except (OSError, zipfile.BadZipFile) as error:
        print(f"check-wheel.py: cannot read wheel: {error}", file=sys.stderr)
        return 1
    missing = REQUIRED - members
    if missing:
        print("check-wheel.py: wheel is missing: " + ", ".join(sorted(missing)), file=sys.stderr)
        return 1
    print(f"wheel package contents verified: {wheel.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
