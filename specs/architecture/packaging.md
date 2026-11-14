# Packaging and deployment

Compatibility paths include `/usr/local/sbin/homelab-ops`,
`/usr/local/sbin/homelab-ops-approve-restart`,
`/usr/local/sbin/homelab_ops_common.py`, `/usr/local/sbin/homelab-inventory`,
`/etc/homelab-ops`, `/var/lib/homelab-ops`, and `scripts/homelab-ops`. The
bootstrap is a guarded first-install workflow and refuses existing
destinations. November 14 notes report an already-installed host and an
in-place module update through a separately recorded operation; this review
does not inspect host files.

Implementation modules are maintained under `src/homelab_ops/`. The minimal
installed-path launcher sources and former common-module import facade are
maintained under `packaging/entrypoints/`; `scripts/` no longer contains
those privileged Python sources. The local `scripts/homelab-ops` CLI remains
as the documented operator command. The new package layout is not deployed.

Preserve entry points until an explicit compatibility migration. Keep root
ownership/mode checks, sudoers validation, and safe partial-install behavior.
Future releases should be staged from reviewed immutable revisions and
administrator-promoted with a known-good release retained. Never use a
requester-writable checkout as privileged input.
