from __future__ import annotations

import ast
import contextlib
import io
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "homelab-ops"
sys.path.insert(0, str(REPO / "src"))
from homelab_ops import client as homelab_ops


class HomelabOpsClientTests(unittest.TestCase):
    def test_installer_embedded_python_blocks_parse(self) -> None:
        for installer_name in ("install-homelab-ops.sh", "install-homelab-ops-canary.sh"):
            installer = (REPO / "scripts" / installer_name).read_text()
            blocks = re.findall(r"<<'PY'\n(.*?)\nPY", installer, flags=re.DOTALL)
            self.assertGreaterEqual(len(blocks), 3, installer_name)
            for index, block in enumerate(blocks):
                with self.subTest(installer=installer_name, block=index):
                    ast.parse(block)

    def test_compatibility_script_preserves_dry_run_entry_point(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "status"], capture_output=True, text=True, check=False
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("DRY RUN", result.stdout)
        self.assertIn("home-server-agent", result.stdout)

    def test_canary_client_targets_only_canary_gateway_by_default(self) -> None:
        canary_script = REPO / "scripts" / "homelab-ops-canary"
        result = subprocess.run(
            [sys.executable, str(canary_script), "status"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("DRY RUN", result.stdout)
        self.assertIn("/usr/local/sbin/homelab-ops-canary", result.stdout)
        self.assertNotIn("/usr/local/sbin/homelab-ops status", result.stdout)

    def test_status_is_dry_run_by_default(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output), patch.object(homelab_ops.subprocess, "run") as run:
            self.assertEqual(homelab_ops.main(["status"]), 0)
        run.assert_not_called()
        self.assertIn("DRY RUN", output.getvalue())
        self.assertIn("home-server-agent", output.getvalue())

    def test_restart_request_is_limited_to_allowlisted_service(self) -> None:
        request, send = homelab_ops.parse_request(["restart", "jellyfin"])
        self.assertFalse(send)
        self.assertEqual(request.remote_argv()[-2:], ["restart", "jellyfin"])

    def test_client_allowlist_matches_project_policy_file(self) -> None:
        policy = homelab_ops.POLICY["projects"]
        self.assertTrue(set(policy))
        self.assertEqual(set(homelab_ops.POLICY["operations"]), {"status", "restart"})
        self.assertEqual(
            homelab_ops.RESTART_SERVICES, frozenset(homelab_ops.POLICY["restart_services"])
        )

    def test_send_flag_is_the_only_path_that_invokes_ssh(self) -> None:
        with patch.object(
            homelab_ops.subprocess, "run", return_value=type("R", (), {"returncode": 0})()
        ) as run:
            self.assertEqual(homelab_ops.main(["--send", "restart", "jellyfin"]), 0)
        argv = run.call_args.args[0]
        self.assertEqual(argv[:3], ["ssh", "--", "home-server-agent"])
        self.assertEqual(
            argv[-5:], ["sudo", "-n", "/usr/local/sbin/homelab-ops", "restart", "jellyfin"]
        )

    def test_no_shell_or_arbitrary_remote_argument_is_accepted(self) -> None:
        for request in (
            ["restart", "grafana;id"],
            ["restart", "pihole"],
            ["restart", "jellyfin", "extra"],
            ["deploy", "monitoring"],
        ):
            with self.subTest(request=request), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    homelab_ops.parse_request(request)
                self.assertEqual(error.exception.code, 2)


class ComposeSnapshotTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("ruby"), "Ruby YAML parser unavailable")
    def test_compose_and_monitoring_yaml_parse(self) -> None:
        repo = SCRIPT.parents[1]
        files = [
            repo / "infra/compose/arr/compose.yaml",
            repo / "infra/compose/jellyfin/compose.yaml",
            repo / "infra/compose/pihole/compose.yaml",
            repo / "infra/compose/monitoring/compose.yaml",
            repo / "infra/compose/monitoring/prometheus/prometheus.yml",
            repo / "infra/compose/monitoring/grafana/provisioning/datasources/prometheus.yml",
        ]
        result = subprocess.run(
            ["ruby", "-e", 'require "yaml"; ARGV.each { |f| YAML.load_file(f) }', *map(str, files)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_secret_settings_are_required_external_variables(self) -> None:
        repo = SCRIPT.parents[1]
        pihole = (repo / "infra/compose/pihole/compose.yaml").read_text()
        monitoring = (repo / "infra/compose/monitoring/compose.yaml").read_text()
        self.assertEqual(pihole.count("FTLCONF_webserver_api_password:"), 1)
        self.assertIn("${PIHOLE_WEBPASSWORD:?", pihole)
        self.assertIn("${GRAFANA_ADMIN_PASSWORD:?", monitoring)


if __name__ == "__main__":
    unittest.main()
