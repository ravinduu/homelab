# Infrastructure configuration workspace

`infra/` is the canonical local working tree for reviewed desired-state files. It now contains sanitized Compose snapshots of the four projects inspected over read-only SSH and the client-side project/action inventory in `policy/allowlist.json`. These files are not yet promoted deployment releases: runtime variables and secret handling were sanitized, and some live mounts and persistent-storage details cannot be independently verified with the current read-only inventory.

Proposed additions after review:

```text
infra/compose/{arr,jellyfin,pihole,monitoring}/
infra/policy/allowlist.json
```

The Compose snapshots intentionally preserve the existing service settings, including known risky monitoring privileges and mutable image tags, so the Git baseline describes the observed stack. Pi-hole's configured password is replaced by a required external variable. Treat these files as a review baseline until the diffs and runtime env are approved and the commit is independently promoted into a root-owned immutable release. Do not put `.env`, credentials, rendered configuration, or release approval records in this tree.
