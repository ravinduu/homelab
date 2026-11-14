# Recovery and rollback

Current gateway actions are status and restart; neither modifies Compose or
application data. Installation docs require disabling the exact sudoers entry
before removing newly installed files. Installer cleanup and host rollback
were not independently verified in this documentation task.

Future changes must specify preflight, immutable known-good revision, backup
and data-migration implications, dependency checks, health criteria, bounded
rollback target, and approval authority. Compose rollback does not reverse
application data migration. Network/SSH, filesystem, destructive cleanup,
backup restoration, and host reboot remain separate high-risk procedures in
`AGENTS.md`.
