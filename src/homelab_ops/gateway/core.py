#!/usr/bin/python3 -I
"""Root-owned, fixed-scope gateway for supervised Docker lifecycle requests."""

from __future__ import annotations

import json
import os
import re
import stat
import subprocess
import sys
import syslog
from pathlib import Path
from typing import Callable

from ..approvals.store import ApprovalError, check_protected_path, consume_restart_approval
from .policy import PolicyError, PolicyRequest, evaluate, migrate_schema1, validate_policy

syslog.openlog("homelab-ops", syslog.LOG_PID, syslog.LOG_AUTHPRIV)

GATEWAY_PATH = Path("/usr/local/sbin/homelab-ops")
COMMON_PATH = Path("/usr/local/sbin/homelab_ops_common.py")
PACKAGE_DIR = Path("/usr/local/lib/homelab_ops")
INVENTORY = "/usr/local/sbin/homelab-inventory"
INVENTORY_PATH = Path(INVENTORY)
DOCKER = "/usr/bin/docker"
POLICY_PATH = Path("/etc/homelab-ops/gateway-policy.json")
STATUS_TIMEOUT_SECONDS = 185
RESTART_TIMEOUT_SECONDS = 35
SAFE_CALLER_RE = re.compile(r"\A[A-Za-z0-9_.-]{1,64}\Z")
CONTAINER_ID_RE = re.compile(r"\A[0-9a-f]{64}\Z")
MAX_POLICY_BYTES = 65536
IDENTITY_FORMAT = (
    "{{.Id}}|{{.Name}}|{{.Config.Image}}|"
    '{{index .Config.Labels "com.docker.compose.project"}}|'
    '{{index .Config.Labels "com.docker.compose.service"}}|{{.State.Status}}'
)
FIXED_ENV = {
    "PATH": "/usr/sbin:/usr/bin:/sbin:/bin",
    "LANG": "C",
    "LC_ALL": "C",
    "HOME": "/nonexistent",
    "DOCKER_CONFIG": "/nonexistent",
    "DOCKER_HOST": "unix:///var/run/docker.sock",
}


class RequestError(Exception):
    """Malformed or unsupported request."""


def parse_request(argv: list[str]) -> tuple[str, str | None]:
    if argv == ["status"]:
        return "status", None
    if argv == ["restart", "jellyfin"]:
        return "restart", "jellyfin"
    raise RequestError("unsupported request")


def caller_name(environment: dict[str, str] | None = None) -> str:
    env = os.environ if environment is None else environment
    candidate = env.get("SUDO_USER", "unknown")
    return candidate if SAFE_CALLER_RE.fullmatch(candidate) else "invalid-caller"


def load_server_policy(path: Path | None = None) -> dict[str, object]:
    selected_path = POLICY_PATH if path is None else path
    check_protected_path(selected_path, file_mode=0o640)
    descriptor = -1
    try:
        descriptor = os.open(
            selected_path, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        )
        info = os.fstat(descriptor)
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.geteuid()
            or stat.S_IMODE(info.st_mode) != 0o640
            or info.st_nlink != 1
            or info.st_size > MAX_POLICY_BYTES
        ):
            raise ApprovalError("server policy is unavailable or invalid")
        with os.fdopen(descriptor, "rb", closefd=False) as policy_file:
            raw = policy_file.read(MAX_POLICY_BYTES + 1)
        if len(raw) > MAX_POLICY_BYTES:
            raise ApprovalError("server policy is unavailable or invalid")
        decoded = raw.decode("utf-8")
        policy = json.loads(decoded, object_pairs_hook=_unique_policy_keys)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        raise ApprovalError("server policy is unavailable or invalid") from error
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    try:
        if isinstance(policy, dict) and policy.get("schema") == 1:
            return migrate_schema1(policy)
        return validate_policy(policy)
    except PolicyError as error:
        raise ApprovalError("server policy is unavailable or invalid") from error


def _unique_policy_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate policy key")
        result[key] = value
    return result


def log_event(
    operation: str,
    service: str,
    caller: str,
    result: str,
    *,
    principal: str = "unknown",
    revision: str = "unknown",
    reason: str = "unknown",
) -> None:
    # Never log request arguments beyond the fixed parsed operation/service,
    # approval contents, environment, command output, or exception text.
    syslog.syslog(
        syslog.LOG_AUTHPRIV | syslog.LOG_NOTICE,
        f"homelab-ops caller={caller} principal={principal} operation={operation} "
        f"service={service} policy_revision={revision} decision_reason={reason} result={result}",
    )


def run_status(
    *,
    caller: str,
    command_runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> int:
    try:
        result = command_runner(
            [INVENTORY],
            stdin=subprocess.DEVNULL,
            stdout=None,
            stderr=subprocess.DEVNULL,
            env=FIXED_ENV.copy(),
            timeout=STATUS_TIMEOUT_SECONDS,
            check=False,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        log_event("status", "all", caller, "timeout")
        print("homelab-ops: status timed out", file=sys.stderr)
        return 124
    except OSError:
        log_event("status", "all", caller, "execution-error")
        print("homelab-ops: status command failed", file=sys.stderr)
        return 1
    result_code = int(result.returncode)
    log_event("status", "all", caller, "success" if result_code == 0 else "failed")
    if result_code:
        print("homelab-ops: inventory failed", file=sys.stderr)
    return result_code


def run_restart(
    service: str,
    *,
    caller: str,
    command_runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
    approval_consumer: Callable[..., dict[str, object]] = consume_restart_approval,
    policy: dict[str, object] | None = None,
) -> int:
    selected_policy = policy
    if selected_policy is None:
        try:
            selected_policy = load_server_policy()
        except ApprovalError:
            log_event("restart", service, caller, "policy-denied")
            print("homelab-ops: protected server policy unavailable", file=sys.stderr)
            return 77
    services = selected_policy["services"]
    service_policy = services.get(service) if isinstance(services, dict) else None
    if not isinstance(service_policy, dict):
        log_event("restart", "unknown", caller, "denied")
        print("homelab-ops: unsupported service", file=sys.stderr)
        return 64
    try:
        approval_consumer(requester=caller)
    except ApprovalError as error:
        result = "approval-expired" if "expired" in str(error) else "approval-denied"
        log_event("restart", service, caller, result)
        print(f"homelab-ops: {error}", file=sys.stderr)
        return 77
    try:
        inspected = command_runner(
            [
                DOCKER,
                "container",
                "inspect",
                "--format",
                IDENTITY_FORMAT,
                service_policy["container_name"],
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            env=FIXED_ENV.copy(),
            timeout=RESTART_TIMEOUT_SECONDS,
            check=False,
            shell=False,
        )
        if inspected.returncode != 0:
            log_event("restart", service, caller, "identity-check-failed")
            print("homelab-ops: service identity verification failed", file=sys.stderr)
            return 77
        fields = inspected.stdout.rstrip("\n").split("|")
        if (
            len(fields) != 6
            or not CONTAINER_ID_RE.fullmatch(fields[0])
            or fields[1] != "/" + service_policy["container_name"]
            or fields[2] != service_policy["image"]
            or fields[3] != service_policy["compose_project"]
            or fields[4] != service_policy["compose_service"]
            or fields[5] != "running"
        ):
            log_event("restart", service, caller, "identity-check-failed")
            print("homelab-ops: service identity verification failed", file=sys.stderr)
            return 77
        result = command_runner(
            [DOCKER, "container", "restart", "--time", "10", fields[0]],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=FIXED_ENV.copy(),
            timeout=RESTART_TIMEOUT_SECONDS,
            check=False,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        log_event("restart", service, caller, "timeout")
        print("homelab-ops: restart timed out", file=sys.stderr)
        return 124
    except OSError:
        log_event("restart", service, caller, "execution-error")
        print("homelab-ops: restart command failed", file=sys.stderr)
        return 1
    result_code = int(result.returncode)
    log_event("restart", service, caller, "success" if result_code == 0 else "failed")
    if result_code:
        print("homelab-ops: restart failed", file=sys.stderr)
    return result_code


def dispatch(
    argv: list[str],
    *,
    caller: str = "unknown",
    command_runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
    approval_consumer: Callable[..., dict[str, object]] = consume_restart_approval,
    policy: dict[str, object] | None = None,
) -> int:
    try:
        operation, service = parse_request(argv)
    except RequestError:
        log_event("invalid", "none", caller, "denied")
        print("usage: homelab-ops status | homelab-ops restart jellyfin", file=sys.stderr)
        return 64
    if policy is None:
        log_event(operation, service or "all", caller, "policy-denied", reason="policy_unavailable")
        print("homelab-ops: protected server policy unavailable", file=sys.stderr)
        return 77
    try:
        normalized = (
            migrate_schema1(policy) if policy.get("schema") == 1 else validate_policy(policy)
        )
    except (PolicyError, AttributeError):
        log_event(operation, service or "all", caller, "policy-denied", reason="invalid_policy")
        print("homelab-ops: protected server policy unavailable", file=sys.stderr)
        return 77
    resource = "host:local" if operation == "status" else f"service:{service}"
    decision = evaluate(normalized, PolicyRequest(caller, operation, resource))
    if not decision.allowed:
        log_event(
            operation,
            service or "all",
            caller,
            "policy-denied",
            principal=decision.principal,
            revision=decision.revision,
            reason=decision.reason,
        )
        print("homelab-ops: operation denied by server policy", file=sys.stderr)
        return 77
    log_event(
        operation,
        service or "all",
        caller,
        "requested",
        principal=decision.principal,
        revision=decision.revision,
        reason=decision.reason,
    )
    if operation == "status":
        return run_status(caller=caller, command_runner=command_runner)
    assert service is not None
    return run_restart(
        service,
        caller=caller,
        command_runner=command_runner,
        approval_consumer=approval_consumer,
        policy=normalized,
    )


def main(argv: list[str] | None = None) -> int:
    if os.geteuid() != 0:
        print(
            "homelab-ops: must be invoked through the approved administrator policy",
            file=sys.stderr,
        )
        return 77
    try:
        check_protected_path(GATEWAY_PATH, file_mode=0o750)
        check_protected_path(COMMON_PATH, file_mode=0o640)
        for module_path in (
            PACKAGE_DIR / "__init__.py",
            PACKAGE_DIR / "approvals" / "__init__.py",
            PACKAGE_DIR / "approvals" / "store.py",
            PACKAGE_DIR / "gateway" / "__init__.py",
            PACKAGE_DIR / "gateway" / "core.py",
            PACKAGE_DIR / "gateway" / "policy.py",
            PACKAGE_DIR / "gateway" / "approval_cli.py",
        ):
            check_protected_path(module_path, file_mode=0o640)
        check_protected_path(INVENTORY_PATH, file_mode=0o755)
        policy = load_server_policy()
    except ApprovalError:
        print("homelab-ops: executable ownership or mode check failed", file=sys.stderr)
        return 77
    caller = caller_name()
    return dispatch(sys.argv[1:] if argv is None else argv, caller=caller, policy=policy)


if __name__ == "__main__":
    raise SystemExit(main())
