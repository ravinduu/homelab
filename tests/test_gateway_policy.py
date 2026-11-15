from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from homelab_ops.gateway.policy import (
    PolicyError,
    PolicyRequest,
    evaluate,
    migrate_schema1,
    validate_policy,
)


def representative_policy() -> dict:
    return json.loads((REPO / "infra/policy/server-policy.json").read_text(encoding="utf-8"))


class PolicyValidationTests(unittest.TestCase):
    def test_representative_policy_has_expected_allow_and_approval_obligation(self) -> None:
        policy = validate_policy(representative_policy())
        status = evaluate(policy, PolicyRequest("agent", "status", "host:local"))
        restart = evaluate(policy, PolicyRequest("agent", "restart", "service:jellyfin"))
        self.assertTrue(status.allowed)
        self.assertFalse(status.require_approval)
        self.assertTrue(restart.allowed)
        self.assertTrue(restart.require_approval)
        self.assertEqual(restart.principal, "unix:agent")
        self.assertEqual(restart.revision, "phase3-canary-1")

    def test_unknown_account_operation_and_resource_deny(self) -> None:
        policy = validate_policy(representative_policy())
        self.assertEqual(
            evaluate(policy, PolicyRequest("other", "status", "host:local")).reason,
            "unknown_principal",
        )
        self.assertEqual(
            evaluate(policy, PolicyRequest("agent", "deploy", "host:local")).reason,
            "unknown_operation",
        )
        self.assertEqual(
            evaluate(policy, PolicyRequest("agent", "restart", "service:other")).reason,
            "unknown_resource",
        )

    def test_explicit_deny_overrides_allow_across_assigned_roles(self) -> None:
        policy = representative_policy()
        policy["roles"]["blocked"] = {
            "permissions": [
                {
                    "effect": "deny",
                    "operation": "status",
                    "resource": "host:local",
                    "require_approval": False,
                }
            ]
        }
        policy["principals"]["agent"]["roles"].append("blocked")
        decision = evaluate(validate_policy(policy), PolicyRequest("agent", "status", "host:local"))
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "explicit_deny")

    def test_scope_is_exact_and_unmatched_permission_denies(self) -> None:
        policy = representative_policy()
        policy["roles"]["operator"]["permissions"].pop(0)
        status = evaluate(validate_policy(policy), PolicyRequest("agent", "status", "host:local"))
        self.assertFalse(status.allowed)
        self.assertEqual(status.reason, "no_matching_permission")

    def test_validation_rejects_unknown_keys_references_and_bad_obligations(self) -> None:
        cases = []
        extra = representative_policy()
        extra["unexpected"] = True
        cases.append(extra)
        unknown_role = representative_policy()
        unknown_role["principals"]["agent"]["roles"] = ["missing"]
        cases.append(unknown_role)
        bad_resource = representative_policy()
        bad_resource["roles"]["operator"]["permissions"][0]["resource"] = "host:*"
        cases.append(bad_resource)
        bad_obligation = representative_policy()
        bad_obligation["roles"]["operator"]["permissions"][0]["require_approval"] = 1
        cases.append(bad_obligation)
        for candidate in cases:
            with self.subTest(candidate=candidate), self.assertRaises(PolicyError):
                validate_policy(candidate)

    def test_schema1_migration_preserves_phase2_agent_decisions(self) -> None:
        old = {
            "schema": 1,
            "operations": ["status", "restart"],
            "services": representative_policy()["services"],
        }
        migrated = migrate_schema1(old)
        self.assertTrue(evaluate(migrated, PolicyRequest("agent", "status", "host:local")).allowed)
        restart = evaluate(migrated, PolicyRequest("agent", "restart", "service:jellyfin"))
        self.assertTrue(restart.allowed)
        self.assertTrue(restart.require_approval)
        self.assertEqual(
            evaluate(migrated, PolicyRequest("other", "status", "host:local")).reason,
            "unknown_principal",
        )


if __name__ == "__main__":
    unittest.main()
