"""Strict, deterministic server-side policy validation and evaluation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


class PolicyError(ValueError):
    """Policy is malformed, ambiguous, or uses an unsupported construct."""


SAFE_TOKEN = re.compile(r"\A[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z")
SAFE_ACCOUNT = re.compile(r"\A[A-Za-z_][A-Za-z0-9_.-]{0,63}\$?\Z")
SAFE_REVISION = re.compile(r"\A[A-Za-z0-9][A-Za-z0-9_.-]{0,63}\Z")
SERVICE_KEYS = {"container_name", "image", "compose_project", "compose_service"}
POLICY_KEYS = {"schema", "revision", "principals", "roles", "services"}
PERMISSION_KEYS = {"effect", "operation", "resource", "require_approval"}


@dataclass(frozen=True)
class PolicyRequest:
    unix_account: str
    operation: str
    resource: str


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str
    revision: str
    principal: str
    operation: str
    resource: str
    require_approval: bool = False


def _is_token(value: object) -> bool:
    return isinstance(value, str) and SAFE_TOKEN.fullmatch(value) is not None


def validate_policy(policy: object) -> dict[str, Any]:
    """Validate exact schema 2 structure and all references; return it unchanged."""
    if not isinstance(policy, dict) or set(policy) != POLICY_KEYS:
        raise PolicyError("policy keys are invalid")
    if type(policy["schema"]) is not int or policy["schema"] != 2:
        raise PolicyError("unsupported policy schema")
    if not isinstance(policy["revision"], str) or not SAFE_REVISION.fullmatch(policy["revision"]):
        raise PolicyError("policy revision is invalid")
    principals, roles, services = policy["principals"], policy["roles"], policy["services"]
    if (
        not isinstance(principals, dict)
        or not principals
        or not isinstance(roles, dict)
        or not roles
    ):
        raise PolicyError("principal or role mapping is invalid")
    if not isinstance(services, dict):
        raise PolicyError("service mapping is invalid")
    principal_ids: set[str] = set()
    for account, principal in principals.items():
        if not isinstance(account, str) or not SAFE_ACCOUNT.fullmatch(account):
            raise PolicyError("principal account mapping is invalid")
        if not isinstance(principal, dict) or set(principal) != {"id", "roles"}:
            raise PolicyError("principal entry is invalid")
        principal_id = principal["id"]
        assigned = principal["roles"]
        if not _is_token(principal_id) or principal_id in principal_ids:
            raise PolicyError("principal identifier is invalid or duplicated")
        principal_ids.add(principal_id)
        if (
            not isinstance(assigned, list)
            or not assigned
            or any(not _is_token(role) for role in assigned)
        ):
            raise PolicyError("principal roles are invalid")
        if len(set(assigned)) != len(assigned) or any(role not in roles for role in assigned):
            raise PolicyError("principal references an unknown or duplicate role")
    for name, service in services.items():
        if not _is_token(name) or not isinstance(service, dict) or set(service) != SERVICE_KEYS:
            raise PolicyError("service mapping is invalid")
        if any(
            not isinstance(value, str) or not value or len(value) > 256
            for value in service.values()
        ):
            raise PolicyError("service identity is invalid")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", service["container_name"]):
            raise PolicyError("service container name is invalid")
    for role_name, role in roles.items():
        if not _is_token(role_name) or not isinstance(role, dict) or set(role) != {"permissions"}:
            raise PolicyError("role entry is invalid")
        permissions = role["permissions"]
        if not isinstance(permissions, list) or not permissions or len(permissions) > 128:
            raise PolicyError("role permissions are invalid")
        for permission in permissions:
            if not isinstance(permission, dict) or set(permission) != PERMISSION_KEYS:
                raise PolicyError("permission entry is invalid")
            effect, operation, resource = (
                permission[key] for key in ("effect", "operation", "resource")
            )
            if (
                not isinstance(effect, str)
                or effect not in {"allow", "deny"}
                or not isinstance(operation, str)
                or operation not in {"status", "restart"}
                or not isinstance(resource, str)
            ):
                raise PolicyError("permission effect or operation is invalid")
            if type(permission["require_approval"]) is not bool:
                raise PolicyError("permission approval obligation is invalid")
            if operation == "status" and resource != "host:local":
                raise PolicyError("status resource is invalid")
            if operation == "restart" and (
                not isinstance(resource, str) or not resource.startswith("service:")
            ):
                raise PolicyError("restart resource is invalid")
            if operation == "restart" and resource[8:] not in services:
                raise PolicyError("permission references an unknown service")
            if permission["require_approval"] and operation != "restart":
                raise PolicyError("approval obligation is unsupported for this operation")
            if operation == "restart" and not permission["require_approval"]:
                raise PolicyError("restart permission must require separate approval")
    return policy


def resolve_principal(policy: dict[str, Any], unix_account: str) -> str | None:
    """Resolve only a trusted gateway-provided Unix account, never request data."""
    entry = policy["principals"].get(unix_account)
    return entry["id"] if isinstance(entry, dict) else None


def evaluate(policy: dict[str, Any], request: PolicyRequest) -> Decision:
    unix_account, operation, resource = request.unix_account, request.operation, request.resource
    principal_entry = policy["principals"].get(unix_account)
    if not isinstance(principal_entry, dict):
        return Decision(
            False, "unknown_principal", policy["revision"], "unknown", operation, resource
        )
    principal_id = principal_entry["id"]
    if operation not in {"status", "restart"}:
        return Decision(
            False, "unknown_operation", policy["revision"], principal_id, operation, resource
        )
    if operation == "status" and resource != "host:local":
        return Decision(
            False, "unknown_resource", policy["revision"], principal_id, operation, resource
        )
    if operation == "restart" and (
        not resource.startswith("service:") or resource[8:] not in policy["services"]
    ):
        return Decision(
            False, "unknown_resource", policy["revision"], principal_id, operation, resource
        )
    matches = [
        permission
        for role_name in principal_entry["roles"]
        for permission in policy["roles"][role_name]["permissions"]
        if permission["operation"] == operation and permission["resource"] == resource
    ]
    if any(item["effect"] == "deny" for item in matches):
        return Decision(
            False, "explicit_deny", policy["revision"], principal_id, operation, resource
        )
    allowed = [item for item in matches if item["effect"] == "allow"]
    if not allowed:
        return Decision(
            False, "no_matching_permission", policy["revision"], principal_id, operation, resource
        )
    return Decision(
        True,
        "allowed",
        policy["revision"],
        principal_id,
        operation,
        resource,
        any(item["require_approval"] for item in allowed),
    )


def migrate_schema1(policy: dict[str, Any]) -> dict[str, Any]:
    """Translate the fixed Phase 2 schema to equivalent schema 2 policy data."""
    if (
        set(policy) != {"schema", "operations", "services"}
        or type(policy.get("schema")) is not int
        or policy["schema"] != 1
    ):
        raise PolicyError("legacy policy is invalid")
    if policy["operations"] != ["status", "restart"]:
        raise PolicyError("legacy policy operations are invalid")
    services = policy["services"]
    if not isinstance(services, dict) or set(services) != {"jellyfin"}:
        raise PolicyError("legacy policy services are invalid")
    role_permissions = [
        {
            "effect": "allow",
            "operation": "status",
            "resource": "host:local",
            "require_approval": False,
        },
        {
            "effect": "allow",
            "operation": "restart",
            "resource": "service:jellyfin",
            "require_approval": True,
        },
    ]
    migrated = {
        "schema": 2,
        "revision": "legacy-phase2",
        "principals": {"agent": {"id": "unix:agent", "roles": ["legacy-operator"]}},
        "roles": {"legacy-operator": {"permissions": role_permissions}},
        "services": services,
    }
    return validate_policy(migrated)
