#!/bin/sh
# First-install-only, side-by-side canary gateway bootstrap.
# Run only from the root-owned /root/homelab-ops-canary staging directory.

set -eu
umask 077

STAGE=/root/homelab-ops-canary
SELF=$STAGE/install-homelab-ops-canary.sh
GATEWAY_SRC=$STAGE/homelab-ops-canary
APPROVER_SRC=$STAGE/homelab-ops-approve-restart-canary
POLICY_SRC=$STAGE/server-policy.json
PACKAGE_SRC=$STAGE/homelab_ops

GATEWAY_DST=/usr/local/sbin/homelab-ops-canary
APPROVER_DST=/usr/local/sbin/homelab-ops-approve-restart-canary
PACKAGE_BASE=/usr/local/lib/homelab-ops-canary
PACKAGE_DST=$PACKAGE_BASE/homelab_ops
POLICY_DIR=/etc/homelab-ops-canary
POLICY_DST=$POLICY_DIR/gateway-policy.json
STATE_DIR=/var/lib/homelab-ops-canary
APPROVALS_DIR=$STATE_DIR/approvals
PENDING_DIR=$APPROVALS_DIR/pending
CONSUMED_DIR=$APPROVALS_DIR/consumed
SUDOERS_DIR=/etc/sudoers.d
SUDOERS_DST=$SUDOERS_DIR/homelab-ops-canary
SUDOERS_CANDIDATE=$SUDOERS_DIR/.homelab-ops-canary.candidate.$$
PACKAGE_FILES='__init__.py approvals/__init__.py approvals/store.py gateway/__init__.py gateway/core.py gateway/approval_cli.py'

PYTHON=/usr/bin/python3
ID=/usr/bin/id
ENV=/usr/bin/env
DOCKER=/usr/bin/docker
INSTALL=/usr/bin/install
MKDIR=/usr/bin/mkdir
RM=/usr/bin/rm
RMDIR=/usr/bin/rmdir
LN=/usr/bin/ln
CHOWN=/usr/bin/chown
CHMOD=/usr/bin/chmod
SHA256SUM=/usr/bin/sha256sum
VISUDO=/usr/sbin/visudo

created_gateway=0
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
    printf '%s\n' "install-homelab-ops-canary: $*" >&2
    exit 1
}

cleanup() {
    result=$?
    cleanup_failed=0
    trap - EXIT HUP INT TERM
    if [ "$completed" -ne 1 ]; then
        if [ "$created_sudoers" -eq 0 ] \
            && { [ -e "$SUDOERS_CANDIDATE" ] || [ -L "$SUDOERS_CANDIDATE" ]; } \
            && { [ -e "$SUDOERS_DST" ] || [ -L "$SUDOERS_DST" ]; } \
            && [ "$SUDOERS_CANDIDATE" -ef "$SUDOERS_DST" ]; then
            created_sudoers=1
        fi
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
            if [ "$created_gateway" -eq 1 ]; then "$RM" -f -- "$GATEWAY_DST" || cleanup_failed=1; fi
            if [ "$created_policy" -eq 1 ]; then "$RM" -f -- "$POLICY_DST" || cleanup_failed=1; fi
            if [ "$created_package" -eq 1 ]; then "$RM" -rf -- "$PACKAGE_BASE" || cleanup_failed=1; fi
            if [ "$created_consumed_dir" -eq 1 ]; then "$RMDIR" "$CONSUMED_DIR" 2>/dev/null || cleanup_failed=1; fi
            if [ "$created_pending_dir" -eq 1 ]; then "$RMDIR" "$PENDING_DIR" 2>/dev/null || cleanup_failed=1; fi
            if [ "$created_approvals_dir" -eq 1 ]; then "$RMDIR" "$APPROVALS_DIR" 2>/dev/null || cleanup_failed=1; fi
            if [ "$created_state_dir" -eq 1 ]; then "$RMDIR" "$STATE_DIR" 2>/dev/null || cleanup_failed=1; fi
            if [ "$created_policy_dir" -eq 1 ]; then "$RMDIR" "$POLICY_DIR" 2>/dev/null || cleanup_failed=1; fi
        fi
        if [ "$cleanup_failed" -ne 0 ]; then
            printf '%s\n' 'install-homelab-ops-canary: cleanup incomplete; inspect only the canary paths as administrator' >&2
        fi
    fi
    exit "$result"
}
trap cleanup EXIT
trap 'exit 1' HUP INT TERM

[ "$("$ID" -u)" -eq 0 ] || fail 'run as root from the administrator account'
[ "$0" = "$SELF" ] || fail "invoke by absolute path: $SELF"

for executable in "$PYTHON" "$ID" "$ENV" "$DOCKER" "$INSTALL" "$MKDIR" "$RM" "$RMDIR" "$LN" "$CHOWN" "$CHMOD" "$SHA256SUM" "$VISUDO"; do
    [ -x "$executable" ] || fail "required executable missing: $executable"
done

# Validate the protected stage, exact file set, canary-only destinations,
# operator privilege boundary, current inventory rule, and both schemas.
"$PYTHON" -I - "$STAGE" "$SELF" "$GATEWAY_SRC" "$APPROVER_SRC" "$POLICY_SRC" "$PACKAGE_SRC" "$PACKAGE_BASE" "$SUDOERS_CANDIDATE" <<'PY'
import ast
import grp
import json
import os
import pwd
import re
import stat
import sys
from pathlib import Path

stage, self_path, gateway, approver, policy_path, package, package_base, candidate = map(Path, sys.argv[1:])
sources = (self_path, gateway, approver, policy_path)
package_files = (
    "__init__.py", "approvals/__init__.py", "approvals/store.py",
    "gateway/__init__.py", "gateway/core.py", "gateway/approval_cli.py",
)
package_sources = [package / item for item in package_files]

def fail(message):
    raise SystemExit("install-homelab-ops-canary: " + message)

def checked_chain(path, *, kind=None):
    absolute = path if path.is_absolute() else Path(os.path.abspath(path))
    for component in reversed((absolute, *absolute.parents)):
        try:
            info = component.lstat()
        except OSError:
            fail("required path unavailable: " + str(component))
        if stat.S_ISLNK(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
            fail("symlink, non-root-owned, or writable path component: " + str(component))
        if component != absolute and not stat.S_ISDIR(info.st_mode):
            fail("non-directory parent: " + str(component))
    info = absolute.lstat()
    if kind == "directory" and not stat.S_ISDIR(info.st_mode):
        fail("not a directory: " + str(absolute))
    if kind == "file" and not stat.S_ISREG(info.st_mode):
        fail("not a regular file: " + str(absolute))
    return info

if stage != Path("/root/homelab-ops-canary"):
    fail("unexpected staging path")
stage_info = checked_chain(stage, kind="directory")
if stage_info.st_gid != 0 or stat.S_IMODE(stage_info.st_mode) != 0o700:
    fail("staging directory must be root:root mode 0700")
for source in sources:
    info = checked_chain(source, kind="file")
    expected_mode = 0o700 if source.name == "install-homelab-ops-canary.sh" else 0o600
    if info.st_gid != 0 or info.st_nlink != 1 or stat.S_IMODE(info.st_mode) != expected_mode:
        fail("source must be root:root, single-link, and exact private mode: " + str(source))
    if info.st_size > 1024 * 1024:
        fail("source file exceeds the 1 MiB limit: " + str(source))

package_info = checked_chain(package, kind="directory")
if package_info.st_gid != 0 or stat.S_IMODE(package_info.st_mode) != 0o700:
    fail("package staging root must be root:root mode 0700")
expected = {package / name for name in ("approvals", "gateway", *package_files)}
actual = set()
for current, directories, files in os.walk(package, followlinks=False):
    current_path = Path(current)
    for name in directories + files:
        candidate_path = current_path / name
        if candidate_path.is_symlink():
            fail("package staging contains a symlink: " + str(candidate_path))
        actual.add(candidate_path)
        if candidate_path.is_dir():
            info = checked_chain(candidate_path, kind="directory")
            if info.st_gid != 0 or stat.S_IMODE(info.st_mode) != 0o700:
                fail("package staging subdirectories must be root:root mode 0700")
        else:
            info = checked_chain(candidate_path, kind="file")
            if info.st_gid != 0 or info.st_nlink != 1 or stat.S_IMODE(info.st_mode) != 0o600:
                fail("package source must be root:root, single-link, mode 0600: " + str(candidate_path))
            if info.st_size > 1024 * 1024:
                fail("package source exceeds the 1 MiB limit: " + str(candidate_path))
if actual != expected:
    fail("package staging has missing or unexpected files")

for parent in (Path("/usr/local/sbin"), Path("/usr/local/lib"), Path("/etc/sudoers.d"), Path("/var/lib")):
    checked_chain(parent, kind="directory")
for destination in (
    Path("/usr/local/sbin/homelab-ops-canary"),
    Path("/usr/local/sbin/homelab-ops-approve-restart-canary"),
    package_base, Path("/etc/homelab-ops-canary"),
    Path("/var/lib/homelab-ops-canary"),
    Path("/etc/sudoers.d/homelab-ops-canary"), candidate,
):
    if destination.exists() or destination.is_symlink():
        fail("canary destination exists; refusing to replace: " + str(destination))

agent = pwd.getpwnam("agent")
groups = set(os.getgrouplist(agent.pw_name, agent.pw_gid))
for group_name in ("sudo", "docker"):
    try:
        group = grp.getgrnam(group_name)
    except KeyError:
        continue
    if group.gr_gid in groups or agent.pw_name in group.gr_mem:
        fail("agent is already in prohibited group " + group_name)

inventory_rule = Path("/etc/sudoers.d/homelab-inventory")
inventory_info = checked_chain(inventory_rule, kind="file")
if inventory_info.st_gid != 0 or stat.S_IMODE(inventory_info.st_mode) != 0o440:
    fail("existing inventory sudoers rule has unexpected owner or mode")
expected_inventory = b'agent ALL=(root) NOPASSWD: /usr/local/sbin/homelab-inventory ""'
if expected_inventory not in inventory_rule.read_bytes().splitlines():
    fail("expected inventory rule not found; leaving all current rules untouched")

checked_chain(Path("/etc/sudoers"), kind="file")
docker_info = checked_chain(Path("/usr/bin/docker"), kind="file")
if docker_info.st_mode & 0o111 == 0:
    fail("Docker executable is not executable")
inventory_info = checked_chain(Path("/usr/local/sbin/homelab-inventory"), kind="file")
if (inventory_info.st_gid != 0 or stat.S_IMODE(inventory_info.st_mode) != 0o755
        or inventory_info.st_nlink != 1):
    fail("approved inventory executable has unexpected ownership, mode, or links")
for entry in (Path("/etc/sudoers"), *Path("/etc/sudoers.d").iterdir()):
    if entry.is_file() and not entry.is_symlink():
        try:
            content = entry.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            fail("cannot inspect active sudoers aliases safely")
        if re.search(r"^\s*(?:Cmnd_Alias\s+)?HOMELAB_OPS_CANARY\b", content, re.M):
            fail("HOMELAB_OPS_CANARY alias already exists")

for source in (gateway, approver, *package_sources):
    try:
        ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    except (OSError, UnicodeError, SyntaxError) as error:
        fail("Python source validation failed for " + source.name + ": " + str(error))
def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result
try:
    config = json.loads(policy_path.read_text(encoding="utf-8"), object_pairs_hook=_unique)
except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
    fail("canary policy JSON is invalid: " + str(error))
if (not isinstance(config, dict) or set(config) != {"schema", "operations", "services"}
        or type(config.get("schema")) is not int or config["schema"] != 1
        or config["operations"] != ["status", "restart"]
        or not isinstance(config["services"], dict) or set(config["services"]) != {"jellyfin"}):
    fail("policy does not match the supported Phase 2 schema")
service = config["services"]["jellyfin"]
if (not isinstance(service, dict)
        or set(service) != {"container_name", "image", "compose_project", "compose_service"}
        or any(not isinstance(value, str) or not value for value in service.values())
        or service.get("container_name") != "jellyfin"):
    fail("policy Jellyfin mapping is invalid")
PY

"$VISUDO" -c || fail 'active sudoers configuration does not validate'
IDENTITY_FORMAT='{{.Id}}|{{.Name}}|{{.Config.Image}}|{{index .Config.Labels "com.docker.compose.project"}}|{{index .Config.Labels "com.docker.compose.service"}}|{{.State.Status}}'
LIVE_IDENTITY=$("$ENV" -i PATH=/usr/bin:/bin HOME=/nonexistent DOCKER_CONFIG=/nonexistent DOCKER_HOST=unix:///var/run/docker.sock LC_ALL=C \
    "$DOCKER" container inspect --format "$IDENTITY_FORMAT" jellyfin) || fail 'live Jellyfin inspection failed'
"$PYTHON" -I - "$POLICY_SRC" "$LIVE_IDENTITY" <<'PY'
import json, re, sys
from pathlib import Path
policy = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
service = policy["services"]["jellyfin"]
fields = sys.argv[2].rstrip("\n").split("|")
if (len(fields) != 6 or not re.fullmatch(r"[0-9a-f]{64}", fields[0])
        or fields[1] != "/" + service["container_name"] or fields[2] != service["image"]
        or fields[3] != service["compose_project"] or fields[4] != service["compose_service"]
        or fields[5] != "running"):
    raise SystemExit("install-homelab-ops-canary: live Jellyfin identity differs; no changes made")
PY

printf '%s\n' 'Canary source hashes (10 files):'
"$SHA256SUM" "$SELF" "$GATEWAY_SRC" "$APPROVER_SRC" "$POLICY_SRC" \
    "$PACKAGE_SRC/__init__.py" "$PACKAGE_SRC/approvals/__init__.py" "$PACKAGE_SRC/approvals/store.py" \
    "$PACKAGE_SRC/gateway/__init__.py" "$PACKAGE_SRC/gateway/core.py" "$PACKAGE_SRC/gateway/approval_cli.py"
printf '%s\n' 'Compare all ten hashes with the reviewed local checkout. Type INSTALL CANARY to continue.'
[ -t 0 ] || fail 'interactive confirmation is required after hash review'
IFS= read -r confirmation || fail 'confirmation was not received'
[ "$confirmation" = 'INSTALL CANARY' ] || fail 'administrator cancelled before installation'

# Only the new canary namespace is created below. The existing gateway,
# policy, approval state, and sudoers include are not installer destinations.
"$MKDIR" -m 0755 "$PACKAGE_BASE"
created_package=1
"$MKDIR" -m 0755 "$PACKAGE_DST" "$PACKAGE_DST/approvals" "$PACKAGE_DST/gateway"
for relative in $PACKAGE_FILES; do
    "$INSTALL" -o root -g root -m 0640 "$PACKAGE_SRC/$relative" "$PACKAGE_DST/$relative"
done
created_gateway=1
"$INSTALL" -o root -g root -m 0750 "$GATEWAY_SRC" "$GATEWAY_DST"
created_approver=1
"$INSTALL" -o root -g root -m 0750 "$APPROVER_SRC" "$APPROVER_DST"
"$MKDIR" -m 0755 "$POLICY_DIR"
created_policy_dir=1
created_policy=1
"$INSTALL" -o root -g root -m 0640 "$POLICY_SRC" "$POLICY_DST"
"$MKDIR" -m 0700 "$STATE_DIR"
created_state_dir=1
"$MKDIR" -m 0700 "$APPROVALS_DIR"
created_approvals_dir=1
"$MKDIR" -m 0700 "$PENDING_DIR"
created_pending_dir=1
"$MKDIR" -m 0700 "$CONSUMED_DIR"
created_consumed_dir=1

"$PYTHON" -I - "$GATEWAY_DST" "$APPROVER_DST" "$POLICY_DST" "$PACKAGE_BASE" "$PACKAGE_DST" "$PACKAGE_DST/approvals" "$PACKAGE_DST/gateway" "$STATE_DIR" "$APPROVALS_DIR" "$PENDING_DIR" "$CONSUMED_DIR" <<'PY'
import stat, sys
from pathlib import Path
expected = {
    Path(sys.argv[1]): ("file", 0o750), Path(sys.argv[2]): ("file", 0o750),
    Path(sys.argv[3]): ("file", 0o640), Path(sys.argv[4]): ("directory", 0o755),
    Path(sys.argv[5]): ("directory", 0o755), Path(sys.argv[6]): ("directory", 0o755),
    Path(sys.argv[7]): ("directory", 0o755), Path(sys.argv[8]): ("directory", 0o700),
    Path(sys.argv[9]): ("directory", 0o700), Path(sys.argv[10]): ("directory", 0o700),
    Path(sys.argv[11]): ("directory", 0o700),
}
for path, (kind, mode) in expected.items():
    for component in reversed((path, *path.parents)):
        info = component.lstat()
        if stat.S_ISLNK(info.st_mode) or info.st_uid != 0 or info.st_gid != 0 or info.st_mode & 0o022:
            raise SystemExit("install-homelab-ops-canary: unsafe installed path: " + str(component))
    info = path.lstat()
    valid = stat.S_ISREG(info.st_mode) if kind == "file" else stat.S_ISDIR(info.st_mode)
    if not valid or stat.S_IMODE(info.st_mode) != mode:
        raise SystemExit("install-homelab-ops-canary: installed mode/type mismatch: " + str(path))
PY

created_candidate=1
(
    set -C
    printf '%s\n' \
        'Cmnd_Alias HOMELAB_OPS_CANARY = /usr/local/sbin/homelab-ops-canary status, /usr/local/sbin/homelab-ops-canary restart jellyfin' \
        'agent ALL=(root) NOPASSWD: HOMELAB_OPS_CANARY' > "$SUDOERS_CANDIDATE"
)
"$CHOWN" root:root "$SUDOERS_CANDIDATE"
"$CHMOD" 0440 "$SUDOERS_CANDIDATE"
"$VISUDO" -cf "$SUDOERS_CANDIDATE" || fail 'canary sudoers candidate failed validation'
"$LN" -- "$SUDOERS_CANDIDATE" "$SUDOERS_DST"
created_sudoers=1
"$RM" -- "$SUDOERS_CANDIDATE"
created_candidate=0
"$VISUDO" -c || fail 'active sudoers configuration failed after canary addition'

completed=1
printf '%s\n' 'homelab-ops canary installed. Existing gateway files, state, policy, and sudoers entry were not modified.'
printf '%s\n' 'First verification should be read-only: scripts/homelab-ops-canary --send status'
