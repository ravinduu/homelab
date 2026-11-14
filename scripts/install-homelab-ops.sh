#!/bin/sh
# One-time, fail-closed administrator bootstrap for homelab-ops Phase 2.
# Run only from the root-owned /root/homelab-ops-phase2 staging directory.

set -eu
umask 077

STAGE=/root/homelab-ops-phase2
SELF=$STAGE/install-homelab-ops.sh
GATEWAY_SRC=$STAGE/homelab-ops-gateway
COMMON_SRC=$STAGE/homelab_ops_common.py
APPROVER_SRC=$STAGE/homelab-ops-approve-restart
POLICY_SRC=$STAGE/server-policy.json
PACKAGE_SRC=$STAGE/homelab_ops
PACKAGE_DST=/usr/local/lib/homelab_ops
PACKAGE_FILES='__init__.py approvals/__init__.py approvals/store.py gateway/__init__.py gateway/core.py gateway/approval_cli.py'

GATEWAY_DST=/usr/local/sbin/homelab-ops
COMMON_DST=/usr/local/sbin/homelab_ops_common.py
APPROVER_DST=/usr/local/sbin/homelab-ops-approve-restart
POLICY_DIR=/etc/homelab-ops
POLICY_DST=$POLICY_DIR/gateway-policy.json
STATE_DIR=/var/lib/homelab-ops
APPROVALS_DIR=$STATE_DIR/approvals
PENDING_DIR=$APPROVALS_DIR/pending
CONSUMED_DIR=$APPROVALS_DIR/consumed
SUDOERS_DIR=/etc/sudoers.d
SUDOERS_DST=$SUDOERS_DIR/homelab-ops
SUDOERS_CANDIDATE=$SUDOERS_DIR/.homelab-ops.candidate.$$

PYTHON=/usr/bin/python3
ID=/usr/bin/id
ENV=/usr/bin/env
DOCKER=/usr/bin/docker
INSTALL=/usr/bin/install
RM=/usr/bin/rm
RMDIR=/usr/bin/rmdir
LN=/usr/bin/ln
CHOWN=/usr/bin/chown
CHMOD=/usr/bin/chmod
SHA256SUM=/usr/bin/sha256sum
VISUDO=/usr/sbin/visudo

created_gateway=0
created_common=0
created_approver=0
created_package=0
created_policy_dir=0
created_policy=0
created_state_dir=0
created_approvals_dir=0
created_pending_dir=0
created_consumed_dir=0
created_candidate=0
created_sudoers=0
completed=0

fail() {
    printf '%s\n' "install-homelab-ops: $*" >&2
    exit 1
}

cleanup() {
    result=$?
    cleanup_failed=0
    trap - EXIT HUP INT TERM
    if [ "$completed" -ne 1 ]; then
        # Cover a signal arriving after the atomic hard-link publish but before
        # the normal created_sudoers flag assignment.
        if [ "$created_sudoers" -eq 0 ] \
            && { [ -e "$SUDOERS_CANDIDATE" ] || [ -L "$SUDOERS_CANDIDATE" ]; } \
            && { [ -e "$SUDOERS_DST" ] || [ -L "$SUDOERS_DST" ]; } \
            && [ "$SUDOERS_CANDIDATE" -ef "$SUDOERS_DST" ]; then
            created_sudoers=1
        fi
        # Disable the new privilege entry before removing any executable.
        if [ "$created_sudoers" -eq 1 ]; then
            if "$RM" -f -- "$SUDOERS_DST"; then
                created_sudoers=0
                "$VISUDO" -c || cleanup_failed=1
            else
                cleanup_failed=1
            fi
        fi
        if [ "$created_candidate" -eq 1 ]; then "$RM" -f -- "$SUDOERS_CANDIDATE" || cleanup_failed=1; fi
        if [ "$created_sudoers" -eq 0 ]; then
            if [ "$created_approver" -eq 1 ]; then "$RM" -f -- "$APPROVER_DST" || cleanup_failed=1; fi
            if [ "$created_common" -eq 1 ]; then "$RM" -f -- "$COMMON_DST" || cleanup_failed=1; fi
            if [ "$created_gateway" -eq 1 ]; then "$RM" -f -- "$GATEWAY_DST" || cleanup_failed=1; fi
            if [ "$created_policy" -eq 1 ]; then "$RM" -f -- "$POLICY_DST" || cleanup_failed=1; fi
            if [ "$created_package" -eq 1 ]; then "$RM" -rf -- "$PACKAGE_DST" || cleanup_failed=1; fi
            if [ "$created_consumed_dir" -eq 1 ]; then "$RMDIR" "$CONSUMED_DIR" 2>/dev/null || cleanup_failed=1; fi
            if [ "$created_pending_dir" -eq 1 ]; then "$RMDIR" "$PENDING_DIR" 2>/dev/null || cleanup_failed=1; fi
            if [ "$created_approvals_dir" -eq 1 ]; then "$RMDIR" "$APPROVALS_DIR" 2>/dev/null || cleanup_failed=1; fi
            if [ "$created_state_dir" -eq 1 ]; then "$RMDIR" "$STATE_DIR" 2>/dev/null || cleanup_failed=1; fi
            if [ "$created_policy_dir" -eq 1 ]; then "$RMDIR" "$POLICY_DIR" 2>/dev/null || cleanup_failed=1; fi
        fi
        if [ "$cleanup_failed" -ne 0 ]; then
            printf '%s\n' 'install-homelab-ops: automatic cleanup was incomplete; inspect the listed installation paths as administrator' >&2
        fi
    fi
    exit "$result"
}
trap cleanup EXIT
trap 'exit 1' HUP INT TERM

[ "$("$ID" -u)" -eq 0 ] || fail 'run as root, for example with sudo from the administrator account'
[ "$0" = "$SELF" ] || fail "invoke by absolute path: $SELF"

for executable in "$PYTHON" "$ID" "$ENV" "$DOCKER" "$INSTALL" "$RM" "$RMDIR" "$LN" "$CHOWN" "$CHMOD" "$SHA256SUM" "$VISUDO"; do
    [ -x "$executable" ] || fail "required executable missing: $executable"
done

# Inspect trusted staging, account/group state, dependencies, all path
# components, existing destinations, and the unchanged inventory rule before
# making any filesystem change.
"$PYTHON" -I - "$STAGE" "$SELF" "$GATEWAY_SRC" "$COMMON_SRC" "$APPROVER_SRC" "$POLICY_SRC" "$PACKAGE_SRC" "$PACKAGE_DST" "$SUDOERS_CANDIDATE" <<'PY'
import ast
import grp
import json
import os
import pwd
import re
import stat
import sys
from pathlib import Path

stage, *arguments = map(Path, sys.argv[1:])
sources, package_source, package_destination, sudoers_candidate = arguments[:5], arguments[5], arguments[6], arguments[7]
package_files = (
    "__init__.py", "approvals/__init__.py", "approvals/store.py",
    "gateway/__init__.py", "gateway/core.py", "gateway/approval_cli.py",
)
package_sources = [package_source / relative for relative in package_files]

def fail(message):
    raise SystemExit("install-homelab-ops: " + message)

def checked_chain(path, *, final_kind=None):
    absolute = path if path.is_absolute() else Path(os.path.abspath(path))
    for component in reversed((absolute, *absolute.parents)):
        try:
            info = component.lstat()
        except OSError as error:
            fail("required path unavailable: " + str(component))
        if stat.S_ISLNK(info.st_mode) or info.st_uid != 0:
            fail("symlink or non-root-owned path component: " + str(component))
        if component != absolute and not stat.S_ISDIR(info.st_mode):
            fail("non-directory parent component: " + str(component))
        if info.st_mode & 0o022:
            fail("group/world-writable path component: " + str(component))
    final = absolute.lstat()
    if final_kind == "directory" and not stat.S_ISDIR(final.st_mode):
        fail("not a directory: " + str(absolute))
    if final_kind == "file" and not stat.S_ISREG(final.st_mode):
        fail("not a regular file: " + str(absolute))
    return final

if stage != Path("/root/homelab-ops-phase2"):
    fail("unexpected staging path")
stage_info = checked_chain(stage, final_kind="directory")
if stage_info.st_gid != 0 or stat.S_IMODE(stage_info.st_mode) != 0o700:
    fail("staging directory must be root:root mode 0700")

for source in sources:
    info = checked_chain(source, final_kind="file")
    expected_mode = 0o700 if source.name == "install-homelab-ops.sh" else 0o600
    if (info.st_gid != 0 or info.st_nlink != 1
            or stat.S_IMODE(info.st_mode) != expected_mode):
        fail("source must have root:root ownership, one link, and expected private mode: " + str(source))

package_info = checked_chain(package_source, final_kind="directory")
if package_info.st_gid != 0 or stat.S_IMODE(package_info.st_mode) != 0o700:
    fail("package staging directory must be root:root mode 0700")
expected_package_paths = {package_source, *(package_source / name for name in ("approvals", "gateway")), *package_sources}
actual_package_paths = set()
for current, directories, filenames in os.walk(package_source, followlinks=False):
    current_path = Path(current)
    for name in directories + filenames:
        candidate = current_path / name
        if candidate.is_symlink():
            fail("package staging contains a symlink: " + str(candidate))
        actual_package_paths.add(candidate)
        if candidate.is_dir():
            checked = checked_chain(candidate, final_kind="directory")
            if checked.st_gid != 0 or stat.S_IMODE(checked.st_mode) != 0o700:
                fail("package staging directories must be root:root mode 0700")
        else:
            checked = checked_chain(candidate, final_kind="file")
            if (checked.st_gid != 0 or checked.st_nlink != 1
                    or stat.S_IMODE(checked.st_mode) != 0o600):
                fail("package source must be root:root, single-link, and private mode 0600: " + str(candidate))
if actual_package_paths != expected_package_paths - {package_source}:
    fail("package source file/directory set is unexpected")

for directory in (Path("/usr/local/sbin"), Path("/usr/local/lib"), Path("/etc/sudoers.d"), Path("/var/lib")):
    checked_chain(directory, final_kind="directory")

for destination in (
    Path("/usr/local/sbin/homelab-ops"),
    Path("/usr/local/sbin/homelab_ops_common.py"),
    Path("/usr/local/sbin/homelab-ops-approve-restart"),
    package_destination,
    Path("/etc/homelab-ops"),
    Path("/var/lib/homelab-ops"),
    Path("/etc/sudoers.d/homelab-ops"),
    sudoers_candidate,
):
    if destination.exists() or destination.is_symlink():
        fail("destination already exists; refusing to replace: " + str(destination))

agent = pwd.getpwnam("agent")
agent_groups = set(os.getgrouplist(agent.pw_name, agent.pw_gid))
for group_name in ("sudo", "docker"):
    try:
        group = grp.getgrnam(group_name)
    except KeyError:
        continue
    if group.gr_gid in agent_groups or agent.pw_name in group.gr_mem:
        fail("agent is already a member of prohibited group " + group_name)

inventory_rule = Path("/etc/sudoers.d/homelab-inventory")
rule_info = checked_chain(inventory_rule, final_kind="file")
if rule_info.st_gid != 0 or stat.S_IMODE(rule_info.st_mode) != 0o440:
    fail("existing inventory sudoers rule has unexpected owner or mode")
expected_rule = b'agent ALL=(root) NOPASSWD: /usr/local/sbin/homelab-inventory ""'
if expected_rule not in inventory_rule.read_bytes().splitlines():
    fail("expected existing homelab-inventory sudoers rule not found; leaving it untouched")

docker = checked_chain(Path("/usr/bin/docker"), final_kind="file")
if docker.st_mode & 0o111 == 0:
    fail("/usr/bin/docker is not executable")
inventory = checked_chain(Path("/usr/local/sbin/homelab-inventory"), final_kind="file")
if stat.S_IMODE(inventory.st_mode) != 0o755 or inventory.st_mode & 0o111 == 0:
    fail("existing homelab-inventory executable has unexpected mode")

sudoers = Path("/etc/sudoers")
checked_chain(sudoers, final_kind="file")
for candidate in (sudoers, *Path("/etc/sudoers.d").iterdir()):
    if candidate.is_file() and not candidate.is_symlink():
        try:
            content = candidate.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            fail("cannot safely inspect sudoers alias names")
        if re.search(r"^\s*(?:Cmnd_Alias\s+)?HOMELAB_OPS_PHASE2\b", content, re.M):
            fail("HOMELAB_OPS_PHASE2 alias already exists")

for source in sources[1:4] + package_sources:
    try:
        ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    except (OSError, UnicodeError, SyntaxError) as error:
        fail("Python source validation failed for " + source.name + ": " + str(error))
try:
    policy = json.loads(sources[4].read_text(encoding="utf-8"))
except (OSError, UnicodeError, json.JSONDecodeError) as error:
    fail("server policy JSON is invalid: " + str(error))
if (not isinstance(policy, dict) or set(policy) != {"schema", "operations", "services"}
        or type(policy.get("schema")) is not int or policy["schema"] != 1
        or policy["operations"] != ["status", "restart"]
        or not isinstance(policy["services"], dict) or set(policy["services"]) != {"jellyfin"}):
    fail("server policy does not match the supported Phase 2 schema")
service = policy["services"]["jellyfin"]
if (not isinstance(service, dict)
        or set(service) != {"container_name", "image", "compose_project", "compose_service"}
        or any(not isinstance(value, str) or not value for value in service.values())
        or service.get("container_name") != "jellyfin"
        or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", service["container_name"])):
    fail("Jellyfin server policy mapping is invalid")
PY

"$VISUDO" -c || fail 'existing sudoers configuration does not validate; no changes made'
IDENTITY_FORMAT='{{.Id}}|{{.Name}}|{{.Config.Image}}|{{index .Config.Labels "com.docker.compose.project"}}|{{index .Config.Labels "com.docker.compose.service"}}|{{.State.Status}}'
LIVE_IDENTITY=$("$ENV" -i PATH=/usr/bin:/bin HOME=/nonexistent DOCKER_CONFIG=/nonexistent DOCKER_HOST=unix:///var/run/docker.sock LC_ALL=C \
    "$DOCKER" container inspect --format "$IDENTITY_FORMAT" jellyfin) \
    || fail 'live Jellyfin inspection failed; no changes made'
"$PYTHON" -I - "$POLICY_SRC" "$LIVE_IDENTITY" <<'PY'
import json, re, sys
from pathlib import Path
try:
    policy = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    service = policy["services"]["jellyfin"]
except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError):
    raise SystemExit("install-homelab-ops: cannot check the live Jellyfin mapping")
fields = sys.argv[2].rstrip("\n").split("|")
if (len(fields) != 6 or not re.fullmatch(r"[0-9a-f]{64}", fields[0])
        or fields[1] != "/" + service["container_name"]
        or fields[2] != service["image"]
        or fields[3] != service["compose_project"]
        or fields[4] != service["compose_service"]
        or fields[5] != "running"):
    raise SystemExit("install-homelab-ops: live Jellyfin identity does not match protected policy; no changes made")
PY
printf '%s\n' 'Validated source hashes:'
"$SHA256SUM" "$SELF" "$GATEWAY_SRC" "$COMMON_SRC" "$APPROVER_SRC" "$POLICY_SRC" \
    "$PACKAGE_SRC/__init__.py" "$PACKAGE_SRC/approvals/__init__.py" "$PACKAGE_SRC/approvals/store.py" \
    "$PACKAGE_SRC/gateway/__init__.py" "$PACKAGE_SRC/gateway/core.py" "$PACKAGE_SRC/gateway/approval_cli.py"
printf '%s\n' 'Compare every hash with the reviewed local checkout. Type INSTALL to continue; any other input aborts without changes.'
[ -t 0 ] || fail 'interactive confirmation is required after hash review'
IFS= read -r confirmation || fail 'confirmation was not received'
[ "$confirmation" = INSTALL ] || fail 'administrator cancelled before installation'

# Every destination was confirmed absent above. The cleanup trap removes only
# the paths created by this run and disables the new sudoers entry first.
"$INSTALL" -d -o root -g root -m 0755 "$POLICY_DIR"
created_policy_dir=1
created_policy=1
"$INSTALL" -o root -g root -m 0640 "$POLICY_SRC" "$POLICY_DST"
created_gateway=1
"$INSTALL" -o root -g root -m 0750 "$GATEWAY_SRC" "$GATEWAY_DST"
created_common=1
"$INSTALL" -o root -g root -m 0640 "$COMMON_SRC" "$COMMON_DST"
created_approver=1
"$INSTALL" -o root -g root -m 0750 "$APPROVER_SRC" "$APPROVER_DST"

created_package=1
"$INSTALL" -d -o root -g root -m 0755 "$PACKAGE_DST" "$PACKAGE_DST/approvals" "$PACKAGE_DST/gateway"
for relative in $PACKAGE_FILES; do
    "$INSTALL" -o root -g root -m 0640 "$PACKAGE_SRC/$relative" "$PACKAGE_DST/$relative"
done

"$INSTALL" -d -o root -g root -m 0700 "$STATE_DIR"
created_state_dir=1
"$INSTALL" -d -o root -g root -m 0700 "$APPROVALS_DIR"
created_approvals_dir=1
"$INSTALL" -d -o root -g root -m 0700 "$PENDING_DIR"
created_pending_dir=1
"$INSTALL" -d -o root -g root -m 0700 "$CONSUMED_DIR"
created_consumed_dir=1

# Confirm installed ownership/modes and protected parent paths before creating
# any sudoers entry.
"$PYTHON" -I - "$GATEWAY_DST" "$COMMON_DST" "$APPROVER_DST" "$POLICY_DST" "$STATE_DIR" "$APPROVALS_DIR" "$PENDING_DIR" "$CONSUMED_DIR" "$PACKAGE_DST" "$PACKAGE_DST/approvals" "$PACKAGE_DST/gateway" <<'PY'
import os, stat, sys
from pathlib import Path

expected = {
    Path(sys.argv[1]): ("file", 0o750),
    Path(sys.argv[2]): ("file", 0o640),
    Path(sys.argv[3]): ("file", 0o750),
    Path(sys.argv[4]): ("file", 0o640),
    Path(sys.argv[5]): ("directory", 0o700),
    Path(sys.argv[6]): ("directory", 0o700),
    Path(sys.argv[7]): ("directory", 0o700),
    Path(sys.argv[8]): ("directory", 0o700),
    Path(sys.argv[9]): ("directory", 0o755),
    Path(sys.argv[10]): ("directory", 0o755),
    Path(sys.argv[11]): ("directory", 0o755),
}
for path, (kind, mode) in expected.items():
    current = path
    while True:
        info = current.lstat()
        if stat.S_ISLNK(info.st_mode) or info.st_uid != 0 or info.st_gid != 0 or info.st_mode & 0o022:
            raise SystemExit("install-homelab-ops: unsafe installed path: " + str(current))
        if current == path:
            valid_type = stat.S_ISREG(info.st_mode) if kind == "file" else stat.S_ISDIR(info.st_mode)
            if not valid_type or stat.S_IMODE(info.st_mode) != mode:
                raise SystemExit("install-homelab-ops: installed mode/type mismatch: " + str(path))
        if current.parent == current:
            break
        current = current.parent
PY

# Build and validate the exact rule while its hidden candidate filename keeps
# it out of the sudoers include directory. Publish it atomically only after
# the standalone parse succeeds.
created_candidate=1
(
    set -C
    printf '%s\n' \
        'Cmnd_Alias HOMELAB_OPS_PHASE2 = /usr/local/sbin/homelab-ops status, /usr/local/sbin/homelab-ops restart jellyfin' \
        'agent ALL=(root) NOPASSWD: HOMELAB_OPS_PHASE2' > "$SUDOERS_CANDIDATE"
)
"$CHOWN" root:root "$SUDOERS_CANDIDATE"
"$CHMOD" 0440 "$SUDOERS_CANDIDATE"
"$VISUDO" -cf "$SUDOERS_CANDIDATE" || fail 'new sudoers rule failed standalone validation'
"$LN" -- "$SUDOERS_CANDIDATE" "$SUDOERS_DST"
created_sudoers=1
"$RM" -- "$SUDOERS_CANDIDATE"
created_candidate=0
"$VISUDO" -c || fail 'complete sudoers configuration failed validation'

completed=1
printf '%s\n' 'homelab-ops Phase 2 installed and sudoers validated.'
printf '%s\n' 'The existing homelab-inventory sudoers rule was not modified.'
printf '%s\n' 'Run the read-only first verification as agent: scripts/homelab-ops --send status'
