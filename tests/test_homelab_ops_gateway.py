from __future__ import annotations

import contextlib
import importlib
import io
import importlib.machinery
import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import threading
import types
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
ENTRYPOINTS = REPO / "packaging" / "entrypoints"
sys.path.insert(0, str(REPO / "src"))

common = importlib.import_module("homelab_ops.approvals.store")
gateway = importlib.import_module("homelab_ops.gateway.core")
approver = importlib.import_module("homelab_ops.gateway.approval_cli")


class GatewayRequestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.logs = patch.object(gateway, "log_event")
        self.logs.start()
        self.addCleanup(self.logs.stop)

    def test_only_status_and_exact_jellyfin_restart_are_allowed(self) -> None:
        self.assertEqual(gateway.parse_request(["status"]), ("status", None))
        self.assertEqual(gateway.parse_request(["restart", "jellyfin"]), ("restart", "jellyfin"))
        for arguments in (
            [], ["status", "extra"], ["restart"], ["restart", "pihole"],
            ["restart", "jellyfin", "extra"], ["restart", "jellyfin;id"],
            ["docker", "ps"], ["deploy", "arr", "a" * 40],
        ):
            with self.subTest(arguments=arguments), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(gateway.dispatch(arguments, command_runner=self.fail_runner), 64)

    def test_privileged_compatibility_entry_points_import_package_and_fail_closed(self) -> None:
        for entrypoint, directory in (
            ("homelab-ops-gateway", ENTRYPOINTS),
            ("homelab-ops-approve-restart", ENTRYPOINTS),
            ("homelab-ops-canary", REPO / "packaging" / "entrypoints"),
            ("homelab-ops-approve-restart-canary", REPO / "packaging" / "entrypoints"),
        ):
            with self.subTest(entrypoint=entrypoint):
                result = subprocess.run(
                    [sys.executable, "-I", str(directory / entrypoint)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 77, result.stderr)
                self.assertTrue(result.stderr)

    def test_canary_entrypoint_configuration_uses_disjoint_paths(self) -> None:
        command = (
            "import runpy,sys; runpy.run_path(sys.argv[1]); "
            "from homelab_ops.gateway import core; "
            "from homelab_ops.approvals import store; "
            "assert str(core.GATEWAY_PATH).endswith('homelab-ops-canary'); "
            "assert str(core.POLICY_PATH).startswith('/etc/homelab-ops-canary/'); "
            "assert str(store.APPROVAL_ROOT).startswith('/var/lib/homelab-ops-canary/'); "
            "assert str(core.PACKAGE_DIR).startswith('/usr/local/lib/homelab-ops-canary/')"
        )
        result = subprocess.run(
            [sys.executable, "-I", "-c", command, str(ENTRYPOINTS / "homelab-ops-canary")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_legacy_shared_module_path_remains_a_compatibility_facade(self) -> None:
        path = ENTRYPOINTS / "homelab_ops_common.py"
        name = "homelab_ops_common_compat"
        loader = importlib.machinery.SourceFileLoader(name, str(path))
        spec = importlib.util.spec_from_loader(name, loader)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        self.assertIs(module.ApprovalError, common.ApprovalError)
        self.assertIs(module.consume_restart_approval, common.consume_restart_approval)

    def test_installed_package_mode_symlink_and_link_count_checks(self) -> None:
        name = "homelab_ops_gateway_compat_for_permissions"
        loader = importlib.machinery.SourceFileLoader(name, str(ENTRYPOINTS / "homelab-ops-gateway"))
        spec = importlib.util.spec_from_loader(name, loader)
        wrapper = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(wrapper)

        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp) / "homelab_ops"
            (package / "approvals").mkdir(parents=True)
            (package / "gateway").mkdir()
            package.chmod(0o755)
            (package / "approvals").chmod(0o755)
            (package / "gateway").chmod(0o755)
            for relative in wrapper.PACKAGE_FILES:
                module_path = package / relative
                module_path.write_text("# test module\n")
                module_path.chmod(0o640)

            wrapper.validate_package_tree(package, root_uid=os.getuid(), root_gid=os.getgid())
            bad_mode = package / "gateway" / "core.py"
            bad_mode.chmod(0o644)
            with self.assertRaises(RuntimeError):
                wrapper.validate_package_tree(package, root_uid=os.getuid(), root_gid=os.getgid())
            bad_mode.chmod(0o640)

            module_path = package / "approvals" / "store.py"
            hardlink = package / "approvals" / "store-copy.py"
            os.link(module_path, hardlink)
            with self.assertRaises(RuntimeError):
                wrapper.validate_package_tree(package, root_uid=os.getuid(), root_gid=os.getgid())
            hardlink.unlink()
            (package / "approvals").rename(package / "approvals-real")
            (package / "approvals").symlink_to("approvals-real", target_is_directory=True)
            with self.assertRaises(RuntimeError):
                wrapper.validate_package_tree(package, root_uid=os.getuid(), root_gid=os.getgid())

    def test_legacy_shared_module_path_remains_a_compatibility_facade(self) -> None:
        path = ENTRYPOINTS / "homelab_ops_common.py"
        spec = importlib.util.spec_from_loader(
            "homelab_ops_common_compat",
            importlib.machinery.SourceFileLoader("homelab_ops_common_compat", str(path)),
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        self.assertIs(module.ApprovalError, common.ApprovalError)
        self.assertIs(module.consume_restart_approval, common.consume_restart_approval)

    @staticmethod
    def fail_runner(*args, **kwargs):
        raise AssertionError("malformed request must not execute a command")

    def test_status_uses_only_inventory_with_fixed_environment_and_timeout(self) -> None:
        calls = []

        def runner(argv, **kwargs):
            calls.append((argv, kwargs))
            return subprocess.CompletedProcess(argv, 0)

        self.assertEqual(gateway.dispatch(["status"], caller="agent", command_runner=runner), 0)
        argv, kwargs = calls[0]
        self.assertEqual(argv, ["/usr/local/sbin/homelab-inventory"])
        self.assertIs(kwargs["shell"], False)
        self.assertEqual(kwargs["env"], gateway.FIXED_ENV)
        self.assertEqual(kwargs["timeout"], gateway.STATUS_TIMEOUT_SECONDS)
        self.assertIs(kwargs["stdin"], subprocess.DEVNULL)

    def test_status_failure_and_timeout_fail_closed(self) -> None:
        failed = lambda argv, **kwargs: subprocess.CompletedProcess(argv, 9)
        timed_out = lambda argv, **kwargs: (_ for _ in ()).throw(subprocess.TimeoutExpired(argv, 1))
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(gateway.dispatch(["status"], command_runner=failed), 9)
            self.assertEqual(gateway.dispatch(["status"], command_runner=timed_out), 124)

    def test_policy_default_path_is_selected_at_call_time(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            policy_path = Path(temp) / "policy.json"
            policy_path.write_text(json.dumps({
                "schema": 1,
                "operations": ["status", "restart"],
                "services": {"jellyfin": {
                    "container_name": "jellyfin",
                    "image": "jellyfin/jellyfin:latest",
                    "compose_project": "jellyfin",
                    "compose_service": "jellyfin",
                }},
            }))
            with patch.object(gateway, "POLICY_PATH", policy_path), patch.object(gateway, "check_protected_path") as check:
                policy = gateway.load_server_policy()
            check.assert_called_once_with(policy_path, file_mode=0o640)
            self.assertEqual(policy["schema"], 1)


class ApprovalTests(unittest.TestCase):
    policy = {"schema": 1, "operations": ["status", "restart"], "services": {
        "jellyfin": {"container_name": "jellyfin", "image": "jellyfin/jellyfin:latest",
                     "compose_project": "jellyfin", "compose_service": "jellyfin"}}}
    identity = "a" * 64 + "|/jellyfin|jellyfin/jellyfin:latest|jellyfin|jellyfin|running"
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.pending_dir = root / "pending"
        self.consumed_dir = root / "consumed"
        self.pending_dir.mkdir(mode=0o700)
        self.consumed_dir.mkdir(mode=0o700)
        self.pending = self.pending_dir / "restart-jellyfin.json"
        self.consume_patch = patch.multiple(
            common,
            APPROVAL_ROOT=root,
            PENDING_DIR=self.pending_dir,
            CONSUMED_DIR=self.consumed_dir,
            PENDING_RESTART=self.pending,
            check_approval_directories=lambda **kwargs: None,
        )
        self.consume_patch.start()
        self.addCleanup(self.consume_patch.stop)
        self.now = 2_000_000_000

    def put_approval(self, *, expires_at: int | None = None, operation: str = "restart", service: str = "jellyfin") -> None:
        record = {
            "schema": 1,
            "operation": operation,
            "service": service,
            "requester": "agent",
            "expires_at": self.now + 90 if expires_at is None else expires_at,
            "nonce": "a" * 32,
        }
        self.pending.write_text(json.dumps(record), encoding="utf-8")
        self.pending.chmod(0o600)

    def consumer(self):
        return lambda requester: common.consume_restart_approval(requester=requester, now=self.now, root_uid=os.getuid())

    def test_missing_approval_does_not_run_docker(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            result = gateway.dispatch(
                ["restart", "jellyfin"], command_runner=GatewayRequestTests.fail_runner,
                approval_consumer=self.consumer(),
                policy=self.policy,
            )
        self.assertEqual(result, 77)

    def test_expired_approval_is_consumed_and_does_not_run_docker(self) -> None:
        self.put_approval(expires_at=self.now)
        with contextlib.redirect_stderr(io.StringIO()):
            result = gateway.dispatch(
                ["restart", "jellyfin"], command_runner=GatewayRequestTests.fail_runner,
                approval_consumer=self.consumer(),
                policy=self.policy,
            )
        self.assertEqual(result, 77)
        self.assertFalse(self.pending.exists())
        self.assertEqual(len(list(self.consumed_dir.iterdir())), 1)

    def test_mismatched_operation_or_service_is_consumed_but_denied(self) -> None:
        self.put_approval(service="pihole")
        with contextlib.redirect_stderr(io.StringIO()):
            result = gateway.dispatch(
                ["restart", "jellyfin"], command_runner=GatewayRequestTests.fail_runner,
                approval_consumer=self.consumer(),
                policy=self.policy,
            )
        self.assertEqual(result, 77)
        self.assertFalse(self.pending.exists())

    def test_approval_is_bound_to_requester(self) -> None:
        self.put_approval()
        with self.assertRaises(common.ApprovalError):
            common.consume_restart_approval(requester="other-user", now=self.now, root_uid=os.getuid())

    def test_file_permissions_are_checked_before_approval_use(self) -> None:
        self.put_approval()
        self.pending.chmod(0o644)
        with contextlib.redirect_stderr(io.StringIO()):
            result = gateway.dispatch(
                ["restart", "jellyfin"], command_runner=GatewayRequestTests.fail_runner,
                approval_consumer=self.consumer(),
                policy=self.policy,
            )
        self.assertEqual(result, 77)
        self.assertTrue(self.pending.exists())

    def test_valid_approval_is_atomically_consumed_before_exact_restart(self) -> None:
        self.put_approval()
        calls = []

        def runner(argv, **kwargs):
            calls.append((argv, kwargs, self.pending.exists()))
            if "inspect" in argv:
                return subprocess.CompletedProcess(argv, 0, stdout=self.identity)
            return subprocess.CompletedProcess(argv, 0)

        self.assertEqual(
            gateway.dispatch(["restart", "jellyfin"], caller="agent", command_runner=runner,
                             approval_consumer=self.consumer(), policy=self.policy),
            0,
        )
        inspect_argv = calls[0][0]
        self.assertEqual(inspect_argv[:5], ["/usr/bin/docker", "container", "inspect", "--format", gateway.IDENTITY_FORMAT])
        self.assertEqual(inspect_argv[-1], "jellyfin")
        self.assertNotIn("--type", inspect_argv)
        argv, kwargs, pending_existed_at_execution = calls[1]
        self.assertEqual(argv, ["/usr/bin/docker", "container", "restart", "--time", "10", "a" * 64])
        self.assertFalse(pending_existed_at_execution)
        self.assertIs(kwargs["shell"], False)
        self.assertEqual(kwargs["env"], gateway.FIXED_ENV)
        self.assertEqual(kwargs["timeout"], gateway.RESTART_TIMEOUT_SECONDS)
        self.assertEqual(len(list(self.consumed_dir.iterdir())), 1)

    def test_container_identity_and_compose_owner_must_match_policy(self) -> None:
        self.put_approval()
        calls = []
        def runner(argv, **kwargs):
            calls.append(argv)
            return subprocess.CompletedProcess(argv, 0, stdout=self.identity.replace("|jellyfin|jellyfin|", "|another-project|another-service|"))
        with contextlib.redirect_stderr(io.StringIO()):
            result = gateway.dispatch(["restart", "jellyfin"], caller="agent", command_runner=runner,
                                      approval_consumer=self.consumer(), policy=self.policy)
        self.assertEqual(result, 77)
        self.assertEqual(len(calls), 1)
        self.assertIn("inspect", calls[0])

    def test_approval_cannot_be_reused(self) -> None:
        self.put_approval()
        def runner(argv, **kwargs):
            if "inspect" in argv:
                return subprocess.CompletedProcess(argv, 0, stdout=self.identity)
            return subprocess.CompletedProcess(argv, 0)
        consumer = self.consumer()
        self.assertEqual(gateway.dispatch(["restart", "jellyfin"], caller="agent", command_runner=runner,
                                          approval_consumer=consumer, policy=self.policy), 0)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(gateway.dispatch(["restart", "jellyfin"],
                                              command_runner=GatewayRequestTests.fail_runner,
                                              approval_consumer=consumer, policy=self.policy), 77)

    def test_concurrent_requests_can_consume_only_once(self) -> None:
        self.put_approval()
        barrier = threading.Barrier(2)
        outcomes = []

        def consume():
            barrier.wait()
            try:
                common.consume_restart_approval(requester="agent", now=self.now, root_uid=os.getuid())
                outcomes.append("consumed")
            except common.ApprovalError:
                outcomes.append("denied")

        threads = [threading.Thread(target=consume) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=5)
        self.assertCountEqual(outcomes, ["consumed", "denied"])
        self.assertEqual(len(list(self.consumed_dir.iterdir())), 1)

    def test_restart_timeout_and_command_failure_are_reported(self) -> None:
        self.put_approval()
        timeout = lambda argv, **kwargs: (_ for _ in ()).throw(subprocess.TimeoutExpired(argv, 1))
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(gateway.dispatch(["restart", "jellyfin"], caller="agent", command_runner=timeout,
                                              approval_consumer=self.consumer(), policy=self.policy), 124)
        self.put_approval()
        def failed(argv, **kwargs):
            if "inspect" in argv:
                return subprocess.CompletedProcess(argv, 0, stdout=self.identity)
            return subprocess.CompletedProcess(argv, 125)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(gateway.dispatch(["restart", "jellyfin"], caller="agent", command_runner=failed,
                                              approval_consumer=self.consumer(), policy=self.policy), 125)

    def test_admin_approval_creation_is_fixed_and_refuses_replacement(self) -> None:
        with patch.object(common, "check_approval_directories"), \
             patch.object(common, "APPROVAL_ROOT", self.pending_dir.parent), \
             patch.object(common, "PENDING_DIR", self.pending_dir), \
             patch.object(common, "CONSUMED_DIR", self.consumed_dir), \
             patch.object(common, "PENDING_RESTART", self.pending):
            created = common.create_restart_approval(requester="agent", now=self.now, root_uid=os.getuid(), root_gid=os.getgid())
            record = json.loads(created.read_text())
            self.assertEqual(record["operation"], "restart")
            self.assertEqual(record["service"], "jellyfin")
            self.assertEqual(record["requester"], "agent")
            self.assertEqual(record["expires_at"], self.now + common.APPROVAL_TTL_SECONDS)
            self.assertEqual(stat.S_IMODE(created.stat().st_mode), 0o600)
            with self.assertRaises(common.ApprovalError):
                common.create_restart_approval(requester="agent", now=self.now, root_uid=os.getuid(), root_gid=os.getgid())

    def test_permission_validator_rejects_writable_or_wrong_owner_paths(self) -> None:
        secure_dir = types.SimpleNamespace(st_uid=0, st_mode=stat.S_IFDIR | 0o700)
        common.validate_component(secure_dir, root_uid=0, expected="directory")
        with self.assertRaises(common.ApprovalError):
            common.validate_component(
                types.SimpleNamespace(st_uid=0, st_mode=stat.S_IFDIR | 0o777),
                root_uid=0,
                expected="directory",
            )
        with self.assertRaises(common.ApprovalError):
            common.validate_component(
                types.SimpleNamespace(st_uid=123, st_mode=stat.S_IFREG | 0o600),
                root_uid=0,
                expected="file",
                file_mode=0o600,
            )

    def test_server_policy_permission_failure_is_denied(self) -> None:
        with patch.object(gateway, "check_protected_path", side_effect=common.ApprovalError("unsafe")):
            with self.assertRaises(common.ApprovalError):
                gateway.load_server_policy(Path("/untrusted/policy.json"))


class ApproverArgumentTests(unittest.TestCase):
    def test_approver_rejects_arguments(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(approver.main(["restart", "pihole"]), 64)


if __name__ == "__main__":
    unittest.main()
