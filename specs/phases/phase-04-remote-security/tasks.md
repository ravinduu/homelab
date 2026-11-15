# Phase 4 tasks — independent agent identity

**Status:** Planned; sequence after Phase 3 design and release.

| # | Vertical slice | Completion criterion | Status |
|---|---|---|---|
| 1 | Approve identity and credential threat model | Owner, enrollment, principal mapping, revocation and recovery decisions accepted. | Todo |
| 2 | Enroll one test principal | Unique credential maps to one server-side principal; no shell/forwarding bypass. | Todo |
| 3 | Rotate and revoke that credential | New credential works in staged overlap; revoked credential is denied before the next request. | Todo |
| 4 | Test loss and recovery | Break-glass path restores bounded access without broadening authority. | Todo |
| 5 | Migrate only after evidence | Controlled old shared-identity retirement plan and rollback approved. | Todo |
