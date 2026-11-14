"""Compatibility facade for the former installed shared module path."""

from __future__ import annotations

import sys
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[2] / "src"
if Path(__file__).absolute() == Path("/usr/local/sbin/homelab_ops_common.py"):
    sys.path.insert(0, "/usr/local/lib")
else:
    sys.path.insert(0, str(SOURCE_ROOT))

from homelab_ops.approvals.store import *  # noqa: F403
