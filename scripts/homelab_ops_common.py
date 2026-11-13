"""Shared fixed paths and approval-file primitives for homelab-ops tools."""

from __future__ import annotations

import json
import os
import re
import stat
import time
import uuid
from pathlib import Path

APPROVAL_ROOT = Path("/var/lib/homelab-ops/approvals")
PENDING_DIR = APPROVAL_ROOT / "pending"
CONSUMED_DIR = APPROVAL_ROOT / "consumed"
PENDING_RESTART = PENDING_DIR / "restart-jellyfin.json"
APPROVAL_TTL_SECONDS = 120
MAX_APPROVAL_BYTES = 4096
NONCE_RE = re.compile(r"\A[0-9a-f]{32}\Z")


class ApprovalError(Exception):
    """Approval absent, invalid, expired, or already consumed."""


def validate_component(
    info: os.stat_result,
    *,
    root_uid: int = 0,
    expected: str = "parent",
    file_mode: int | None = None,
) -> None:
    if stat.S_ISLNK(info.st_mode) or info.st_uid != root_uid or info.st_mode & 0o022:
        raise ApprovalError("protected path ownership or mode check failed")
    if expected == "directory" and not stat.S_ISDIR(info.st_mode):
        raise ApprovalError("protected path is not a directory")
    if expected == "file" and (
        not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != file_mode
    ):
        raise ApprovalError("protected file type or mode check failed")
    if expected not in {"parent", "directory", "file"}:
        raise ApprovalError("invalid protected path check")


def check_protected_path(path: Path, *, root_uid: int = 0, file_mode: int | None = None) -> os.stat_result:
    """Require every path component to be root-owned and non-writable by others."""
    absolute = path.absolute()
    chain = list(reversed((absolute, *absolute.parents)))
    for component in chain:
        try:
            info = component.lstat()
        except OSError as error:
            raise ApprovalError("protected path unavailable") from error
        expected = "parent" if component != absolute else ("directory" if file_mode is None else "file")
        validate_component(info, root_uid=root_uid, expected=expected, file_mode=file_mode)
    return chain[0]


def check_approval_directories(*, root_uid: int = 0) -> None:
    for directory in (APPROVAL_ROOT, PENDING_DIR, CONSUMED_DIR):
        info = check_protected_path(directory, root_uid=root_uid)
        if stat.S_IMODE(info.st_mode) != 0o700:
            raise ApprovalError("approval directory must have mode 0700")


def _unique_json(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def consume_restart_approval(
    *, requester: str, now: int | None = None, root_uid: int = 0
) -> dict[str, object]:
    """Atomically move the pending approval out of the requestable slot first."""
    check_approval_directories(root_uid=root_uid)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(PENDING_RESTART, flags)
    except FileNotFoundError as error:
        raise ApprovalError("restart approval is missing or already consumed") from error
    except OSError as error:
        raise ApprovalError("restart approval cannot be opened safely") from error

    try:
        info = os.fstat(descriptor)
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != root_uid
            or stat.S_IMODE(info.st_mode) != 0o600
            or info.st_nlink != 1
            or info.st_size > MAX_APPROVAL_BYTES
        ):
            raise ApprovalError("restart approval ownership or mode check failed")
        with os.fdopen(descriptor, "rb", closefd=False) as approval_file:
            raw = approval_file.read(MAX_APPROVAL_BYTES + 1)
    except ApprovalError:
        raise
    except OSError as error:
        raise ApprovalError("restart approval could not be read safely") from error
    finally:
        os.close(descriptor)

    # Source and destination are on the same protected filesystem. Competing
    # callers race on this rename; only one can remove the pending pathname.
    consumed_path = CONSUMED_DIR / (uuid.uuid4().hex + ".json")
    try:
        os.rename(PENDING_RESTART, consumed_path)
    except FileNotFoundError as error:
        raise ApprovalError("restart approval is missing or already consumed") from error
    except OSError as error:
        raise ApprovalError("restart approval could not be consumed") from error
    try:
        for directory in (PENDING_DIR, CONSUMED_DIR):
            descriptor = os.open(directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
    except OSError as error:
        raise ApprovalError("consumed approval could not be synchronized") from error

    if len(raw) > MAX_APPROVAL_BYTES:
        raise ApprovalError("restart approval is invalid")
    try:
        approval = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_json)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise ApprovalError("restart approval is invalid") from error
    required = {"schema", "operation", "service", "requester", "expires_at", "nonce"}
    if not isinstance(approval, dict) or set(approval) != required:
        raise ApprovalError("restart approval is invalid")
    if (
        type(approval["schema"]) is not int
        or approval["schema"] != 1
        or approval["operation"] != "restart"
        or approval["service"] != "jellyfin"
        or approval["requester"] != requester
        or type(approval["expires_at"]) is not int
        or not isinstance(approval["nonce"], str)
        or not NONCE_RE.fullmatch(approval["nonce"])
    ):
        raise ApprovalError("restart approval does not match this request")
    current = int(time.time()) if now is None else now
    if approval["expires_at"] <= current:
        raise ApprovalError("restart approval has expired")
    if approval["expires_at"] > current + APPROVAL_TTL_SECONDS:
        raise ApprovalError("restart approval expiry exceeds the allowed window")
    return approval


def create_restart_approval(
    *, requester: str, now: int | None = None, root_uid: int = 0, root_gid: int = 0
) -> Path:
    """Create one short-lived approval; never replace an existing request."""
    check_approval_directories(root_uid=root_uid)
    current = int(time.time()) if now is None else now
    approval = {
        "schema": 1,
        "operation": "restart",
        "service": "jellyfin",
        "requester": requester,
        "expires_at": current + APPROVAL_TTL_SECONDS,
        "nonce": uuid.uuid4().hex,
    }
    temporary_path = PENDING_DIR / ("." + approval["nonce"] + ".tmp")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(temporary_path, flags, 0o600)
    except OSError as error:
        raise ApprovalError("restart approval could not be created safely") from error
    try:
        os.fchmod(descriptor, 0o600)
        os.fchown(descriptor, root_uid, root_gid)
        with os.fdopen(descriptor, "w", encoding="utf-8", closefd=False) as approval_file:
            approval_file.write(json.dumps(approval, sort_keys=True) + "\n")
            approval_file.flush()
            os.fsync(descriptor)
    except Exception as error:
        os.close(descriptor)
        try:
            temporary_path.unlink()
        except OSError:
            pass
        if isinstance(error, ApprovalError):
            raise
        raise ApprovalError("restart approval could not be written safely") from error
    else:
        os.close(descriptor)
    try:
        os.link(temporary_path, PENDING_RESTART, follow_symlinks=False)
    except FileExistsError as error:
        temporary_path.unlink(missing_ok=True)
        raise ApprovalError("a restart approval is already pending; do not overwrite it") from error
    except OSError as error:
        temporary_path.unlink(missing_ok=True)
        raise ApprovalError("restart approval could not be published safely") from error
    temporary_path.unlink()
    try:
        directory_fd = os.open(PENDING_DIR, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except OSError as error:
        try:
            PENDING_RESTART.unlink()
        except OSError:
            pass
        raise ApprovalError("restart approval could not be synchronized") from error
    return PENDING_RESTART
