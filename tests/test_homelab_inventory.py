#!/usr/bin/env python3
"""Local behavior tests for the privileged inventory wrapper."""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "homelab-inventory"


class InventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="homelab-inventory-test-"))
        self.ids = self.tmp / "ids"
        self.mode = self.tmp / "mode"
        self.calls = self.tmp / "calls"
        self.timeouts = self.tmp / "timeouts"
        self.mode.write_text("ok\n")
        self.calls.write_text("")
        self.timeouts.write_text("")

        docker = self.tmp / "docker"
        docker.write_text(
            textwrap.dedent(
                f"""\
                #!/bin/sh
                set -eu
                shift 2 # fixed --host SOCKET arguments
                printf '%s\\n' "$*" >> {str(self.calls)!r}
                mode=$(cat {str(self.mode)!r})
                if [ "$1" = container ] && [ "${{2-}}" = ls ]; then
                        case "$mode" in
                            ls_fail) printf '%s\\n' 'mock list failure' >&2; exit 7 ;;
                            ls_sleep) /bin/sleep 5 ;;
                        esac
                        cat {str(self.ids)!r}
                elif [ "$1" = inspect ]; then
                        case "$mode" in
                            inspect_fail) printf '%s\\n' 'mock inspect failure' >&2; exit 9 ;;
                            inspect_sleep) /bin/sleep 5 ;;
                            no_health)
                                case "$*" in
                                    *'index .State "Health"'*) printf 'mock inventory record health=null\\n' ;;
                                    *) printf '%s\\n' 'unsafe health template' >&2; exit 11 ;;
                                esac
                                ;;
                            with_health)
                                case "$*" in
                                    *'index .State "Health"'*) printf 'mock inventory record health="healthy"\\n' ;;
                                    *) printf '%s\\n' 'unsafe health template' >&2; exit 11 ;;
                                esac
                                ;;
                        esac
                        if [ "$mode" != no_health ] && [ "$mode" != with_health ]; then
                            printf 'mock inventory record\\n'
                        fi
                else
                    printf '%s\\n' 'unexpected docker command' >&2
                    exit 98
                fi
                """
            )
        )
        docker.chmod(0o755)

        timeout = self.tmp / "timeout"
        timeout.write_text(
            textwrap.dedent(
                f"""\
                #!{sys.executable}
                import os, signal, subprocess, sys
                args = sys.argv[1:]
                while args and args[0].startswith('--'):
                    args.pop(0)
                duration = args.pop(0)
                with open({str(self.timeouts)!r}, 'a') as out:
                    out.write(duration + ' ' + repr(args) + '\\n')
                seconds = float(duration[:-1])
                child = subprocess.Popen(args, start_new_session=True)
                try:
                    result = child.wait(timeout=seconds)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(child.pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                    try:
                        child.wait(timeout=0.2)
                    except subprocess.TimeoutExpired:
                        try:
                            os.killpg(child.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                        child.wait()
                    sys.exit(124)
                sys.exit(result if result >= 0 else 128 - result)
                """
            )
        )
        timeout.chmod(0o755)

        script_text = SOURCE.read_text()
        script_text = script_text.replace("DOCKER=/usr/bin/docker", f"DOCKER={docker}")
        script_text = script_text.replace("TIMEOUT=/usr/bin/timeout", f"TIMEOUT={timeout}")
        script_text = script_text.replace("DOCKER_TIMEOUT=15s", "DOCKER_TIMEOUT=5s")
        script_text = script_text.replace("OVERALL_TIMEOUT=180s", "OVERALL_TIMEOUT=30s")
        self.script = self.tmp / "homelab-inventory"
        self.script.write_text(script_text)
        self.script.chmod(0o755)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([str(self.script), *args], capture_output=True, text=True, timeout=30)

    def set_ids(self, count: int) -> None:
        self.ids.write_text("".join(f"{number:064x}\n" for number in range(1, count + 1)))

    def test_rejects_arguments_before_running_docker(self) -> None:
        result = self.run_script("--help")
        self.assertEqual(result.returncode, 64)
        self.assertIn("arguments are not accepted", result.stderr)
        self.assertEqual(self.calls.read_text(), "")

    def test_rejects_invalid_container_id(self) -> None:
        self.ids.write_text("g" * 64 + "\n")
        result = self.run_script()
        self.assertEqual(result.returncode, 70)
        self.assertIn("invalid container ID", result.stderr)
        self.assertFalse(any("inspect" in line for line in self.calls.read_text().splitlines()))

    def test_docker_list_failure_propagates(self) -> None:
        self.mode.write_text("ls_fail\n")
        result = self.run_script()
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertIn("mock list failure", result.stderr)

    def test_docker_inspect_failure_propagates_without_pipeline_masking(self) -> None:
        self.set_ids(1)
        self.mode.write_text("inspect_fail\n")
        result = self.run_script()
        self.assertEqual(result.returncode, 9)
        self.assertIn("mock inspect failure", result.stderr)

    def test_missing_health_key_uses_safe_lookup_and_outputs_null(self) -> None:
        self.set_ids(1)
        self.mode.write_text("no_health\n")
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("health=null", result.stdout)
        inspect_call = next(
            line for line in self.calls.read_text().splitlines() if line.startswith("inspect ")
        )
        self.assertIn('index .State "Health"', inspect_call)

    def test_present_health_key_is_reported(self) -> None:
        self.set_ids(1)
        self.mode.write_text("with_health\n")
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('health="healthy"', result.stdout)

    def test_each_docker_invocation_has_timeout_and_timeout_fails_nonzero(self) -> None:
        self.mode.write_text("ls_sleep\n")
        self.script.write_text(
            self.script.read_text().replace("DOCKER_TIMEOUT=5s", "DOCKER_TIMEOUT=0.2s")
        )
        result = self.run_script()
        self.assertEqual(result.returncode, 124)
        self.assertIn("0.2s", self.timeouts.read_text())

    def test_overall_timeout_bounds_many_slow_inspections(self) -> None:
        self.set_ids(100)
        self.mode.write_text("inspect_sleep\n")
        self.script.write_text(
            self.script.read_text().replace("OVERALL_TIMEOUT=30s", "OVERALL_TIMEOUT=1.2s")
        )
        result = self.run_script()
        self.assertEqual(result.returncode, 124)
        self.assertIn("1.2s", self.timeouts.read_text())

    def test_caps_at_one_hundred_and_reports_truncation(self) -> None:
        self.set_ids(101)
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        inspect_calls = [
            line for line in self.calls.read_text().splitlines() if line.startswith("inspect ")
        ]
        self.assertEqual(len(inspect_calls), 100)
        self.assertIn("TRUNCATED: at least 101 containers exist", result.stderr)

    def test_reports_fixed_command_and_timeout_arguments(self) -> None:
        self.set_ids(1)
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = self.calls.read_text().splitlines()
        self.assertIn("container ls --all --quiet --no-trunc --last 101", lines)
        self.assertTrue(lines[1].startswith("inspect --type container --format "))


if __name__ == "__main__":
    unittest.main()
