# Open-source preparation status

**Review date:** 2026-11-15  
**Status:** Audit and plan only; no repository separation or publication has
been approved or performed.

The detailed inventory, file classification, privacy/history scan, proposed
repository layouts, rename map, and readiness plan are in
[`reports/envoy-open-source-audit.md`](../reports/envoy-open-source-audit.md).
This status page is a short handoff; it is private Homelab documentation and
must not be copied to a public product repository without review.

## Verified facts

- The current `main` worktree contains substantial pre-existing uncommitted
  changes. They were preserved. The existing GitHub `origin` was not changed;
  its visibility was not checked.
- The current tree mixes reusable Python/package/phase-workflow candidates
  with personal infrastructure configuration, production policy, deployment
  tooling, host operations documentation, and audit evidence.
- Yelp `detect-secrets` 1.5.0 reported no candidate secrets in the current
  tracked/untracked tree or the six reachable commit snapshots. A separate
  value-redacting heuristic found personal filesystem paths and private
  addressing in the tree/history. This is not a guarantee that no secret
  exists.
- No source/configuration was moved, renamed, deleted, committed, pushed, or
  published during the audit. No server or sudoers changes were made.

## Decisions still required

1. Resolve whether the product can use the `Envoy` name. CNCF Envoy branding
   creates a trademark/association concern; PyPI also has conflicting `envoy`
   package/import/command names. Obtain clearance or select a distinct name.
2. Approve the package, import, CLI, repository, and copyright identifiers.
3. Select a license. Apache-2.0 is only a candidate recommendation; no license
   file has been added.
4. Approve a fresh sanitized repository with new history. Do not rewrite or
   publish the existing Homelab history.
5. Approve the public-file allowlist and private Homelab ownership/layout.

## Next session

After decisions 1–5 are approved, prepare an allowlisted export in a separate
checkout, scan its complete new history, and validate the package from a clean
clone. Keep the existing worktree and remote intact. Do not publish or change
remote settings without separate approval.
