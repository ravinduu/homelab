# Envoy open-source preparation audit

**Review date:** 2026-11-15  
**Stage:** Audit and separation plan only. No source/configuration was moved,
renamed, deleted, committed, pushed, or published. No remote, production host,
service, or sudoers configuration was changed.

This report is a private planning artifact for the existing Homelab repository;
do not copy it into a public Envoy repository without a separate privacy
review.

## 1. Repository state and audit scope

- Audited the working tree, including staged/unstaged tracked files and
  nonignored untracked files, plus all six commits reachable from local/remote
  refs. `git fsck` found no unreachable objects; reflogs contained no additional
  commits outside ref history.
- The active branch is `main`. `origin` points to the existing GitHub
  repository named `homelab`; its URL and owner path were intentionally omitted
  from this report. The remote was not changed. Its GitHub visibility was not
  checked; verify it remains private before any further preparation that could
  expose this history.
- The worktree contains substantial pre-existing modifications, deletions, and
  untracked code/specification work. All of it is preserved. This audit report
  itself is a new untracked file.
- File classification below is a proposed destination, not permission to move
  or publish any file. Several candidate public files need a second scrub.

## 2. Inventory and classification

| Current paths | Classification | Finding / proposed disposition |
|---|---|---|
| `src/homelab_ops/**` | Product source candidate | Reusable package boundary, but the gateway, approval and policy paths still encode a shared Unix account, fixed service, homelab paths, and legacy names. Port/refactor into a newly named package only after interface review; do not copy verbatim. |
| `tests/**` | Product tests candidate | Useful unit/negative tests. Rename test modules, remove personal policy/service assumptions, and add synthetic fixtures. Keep site integration tests in Homelab. |
| `pyproject.toml`, `Makefile`, `requirements-quality.txt`, `scripts/check-wheel.py`, `.github/workflows/quality.yml`, `.gitignore` | Public development tooling candidate | Existing Python/src packaging and basic quality CI can be reused after package/command rename and security review. CI does not yet provide a full public release pipeline or a secret-scanning gate. |
| `specs/product/**`, `specs/architecture/**`, `specs/phases/**`, `specs/templates/**`, `docs/adr/**` | Public documentation candidate | Most content describes product boundaries and phase delivery. Scrub host/service names, installed paths, site policy examples, canary procedures, and personal deployment claims before copying. |
| `README.md`, `AGENTS.md` | Replace for Envoy | README describes the personal homelab product/deployment context. AGENTS contains infrastructure access rules and personal deployment details. Write a product README and contributor-oriented agent instructions; do not publish the current AGENTS file. |
| `docs/infrastructure.md`, `docs/service-inventory.md`, `docs/infrastructure-management-phase-1.md`, `docs/docker-*.md`, `docs/homelab-ops-*.md`, `docs/operations/homelab-ops-canary.md`, `docs/operations/phase-03-policy-engine-dev-test.md` | Private Homelab documentation | Site inventory, host operation, installation, paths, and canary/runbook material. Retain in the private repository. Extract only generic operational principles into newly reviewed Envoy docs. |
| `infra/compose/**`, `infra/policy/**`, `proposed/**` | Private infrastructure/configuration | Personal Compose snapshots, monitoring config, client allowlist, production policy, and site-specific policy fixtures. None should ship as Envoy defaults. Convert selected test examples to synthetic fixtures after review. |
| `reports/homelab-audit.md`, `reports/docker-socket-remediation-plan.md` | Private audit/remediation evidence | Contains personal infrastructure evidence and network/path context. Keep private. |
| `reports/phase-03-quality-assessment.md` | Product engineering report candidate, needs scrub | Assessment includes fixed service and canary assumptions. Rewrite in generic terms before any public use. |
| `scripts/install-homelab-ops*.sh`, `scripts/homelab-ops-canary`, `packaging/entrypoints/homelab-ops-*`, `packaging/entrypoints/homelab_ops_common.py` | Private deployment compatibility tooling | Encodes installed paths, sudoers, canary layout, and legacy commands. Keep with Homelab until a separately approved migration; do not publish as a generic installer. |
| `scripts/homelab-ops`, `scripts/homelab-inventory` | Mixed product/deployment boundary | The CLI logic may become Envoy client functionality; the host alias and inventory wrapper are deployment-specific. Separate the reusable request contract from Homelab transport/wrapper configuration. |
| `.agents/skills/**` | Private Homelab workflows | Current skills are environment-specific audit/session procedures. Do not publish them as Envoy product workflows. |
| `specs/phases/phase-00-foundation/code-migration-*` and canary docs | Historical/private transition artifacts | Preserve in Homelab history. Keep only scrubbed product architecture decisions in Envoy. |

No root `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, or `CHANGELOG.md` is
present. Existing tests and local package metadata do not establish an open
source license or public release readiness.

## 3. Sensitive-data and history audit

### Scanner results

- Yelp `detect-secrets` 1.5.0 scanned the current tracked and untracked
  worktree and each of the six reachable commit snapshots. It reported zero
  candidate secrets. No matched values were emitted.
- A separate value-redacting heuristic found personal home-directory paths in
  eight current files and a private IPv4 address in one current audit report.
  Across historical commit snapshots, personal paths/private addressing
  appeared in 31 commit/path snapshots. The affected current files are
  `AGENTS.md`, `docs/docker-monitoring-security.md`,
  `docs/infrastructure-management-phase-1.md`, `docs/infrastructure.md`,
  `docs/operations/homelab-ops-canary.md`,
  `docs/operations/phase-03-policy-engine-dev-test.md`,
  `reports/docker-socket-remediation-plan.md`, and
  `reports/homelab-audit.md`. Exact paths/addresses are withheld.
- The secret scanner is heuristic, not proof that the repository contains no
  secrets. The system did not have `gitleaks` or `trufflehog`; no scanner
  baseline or public scanning workflow exists yet. The manual/current/history
  audit must be repeated on the final export using an approved scanner and
  reviewed false positives.

### Categories requiring private separation or scrubbing

- **Hostnames, SSH account/alias, and local deployment paths:** present in
  `AGENTS.md` and operational/installation documentation. Values are omitted.
- **SSH keys/tokens/passwords:** no key-file names or credential-shaped
  detector hits were found. This does not establish that externally managed
  credentials were never used; do not copy any credentials into either repo.
  No rotation is indicated by this scan. Rotate immediately if manual review
  finds a live credential in current or historical content.
- **Mount points and personal service configuration:** concentrated in
  `infra/compose/**` and `proposed/monitoring/**`; keep private. Treat rendered
  Compose/env output as sensitive even if current files use environment
  substitutions.
- **Production policy:** `infra/policy/server-policy.json` is site policy and
  must remain private. `infra/policy/allowlist.json` is deployment-specific
  client configuration, not a server authorization source. The development
  deny fixture is not a safe public example until rewritten with synthetic
  names and validated against the canonical schema.
- **Infrastructure diagram/audit evidence:** `docs/infrastructure.md`,
  `docs/service-inventory.md`, and `reports/homelab-audit.md` are private.
- **Hardcoded service/runtime assumptions:** the current implementation and
  tests include a fixed Jellyfin operation plus SSH, sudoers, Docker, and
  installed-path assumptions. Monitoring/media service names also occur in
  site configuration and docs. Replace product examples with a synthetic
  adapter fixture; do not make personal services Envoy defaults.
- **Legacy identifier:** `homelab-ops`/`homelab_ops` occurs in 36 current files
  across source, tests, scripts, package metadata, docs, specs, and entrypoints.
  A systematic rename/refactor is needed; public compatibility aliases are not
  recommended by default.
- **Commit metadata:** all six reachable commits contain author metadata.
  Preserve the old private repository; a fresh public import should be created
  with an explicitly chosen public attribution identity.

### History conclusion

Removing private files from the current tree would not remove their data from
the six-commit history. Because history already contains private filesystem
paths and private network addressing, the safer recommendation is a fresh
sanitized public Envoy repository with a new root commit. Do not rewrite or
force-push the existing Homelab history. Keep the existing remote and history
private; do not make it public.

## 4. Proposed repository separation

### Public Envoy repository

Start a new repository from an explicit allowlist, not a copy of the current
tree or `.git` directory:

```text
envoy-public/
  .github/workflows/       CI, security checks, package validation
  docs/                    user, architecture, security, install/operations
  examples/                synthetic config/policy only; no live values
  specs/{product,architecture,phases,templates}/
  src/<approved_package>/  canonical product implementation only
  tests/{unit,integration,fixtures}/
  .gitignore
  AGENTS.md                public contribution/development rules
  CHANGELOG.md
  CONTRIBUTING.md
  LICENSE                  only after owner approval
  README.md
  SECURITY.md
  Makefile
  pyproject.toml
  requirements-quality.txt
```

Do not add empty adapter modules. Package name, import namespace, executable,
and repository branding are an unresolved decision (see Section 6).

### Private Homelab repository

Keep the existing repository as the private source of site state. After
separate approval, organize it around:

```text
homelab-private/
  .agents/skills/           private operational procedures
  AGENTS.md                 host/account/safety rules
  infra/compose/            reviewed site Compose snapshots
  infra/policy/             site policy and client configuration
  proposed/                 unapproved site proposals
  docs/                     infrastructure, service inventory, runbooks
  reports/                  private audits and remediation evidence
  deployments/envoy/        site-supplied policy/config and package pins
  scripts/                  site bootstrap/update/rollback wrappers
  tests/site-integration/   tests requiring this site model
```

Credentials and rendered secret configuration stay outside Git. Homelab
supplies its own protected policy, inventory/adapter settings, SSH target,
credential references, and release pin to Envoy. Envoy should accept explicit
configuration and never default to this host, account, service, mount, or
policy.

## 5. Rename and refactoring plan (no rename performed)

| Existing surface | Planned action |
|---|---|
| PyPI distribution in `pyproject.toml` (`homelab-ops`) | Select a collision-free distribution after brand approval; do not claim the bare `envoy` distribution. |
| `src/homelab_ops` imports and test imports | Refactor to one approved package namespace; no compatibility alias by default. Keep public API behavior only where specified. |
| `scripts/homelab-ops`, canary CLI and approval command names | Replace the product-facing CLI with an approved unambiguous executable. Keep Homelab wrappers private. |
| `scripts/homelab-inventory` and gateway entrypoints | Extract generic typed inventory/adapter contract; keep current host wrapper and privileged paths private until redesigned. |
| Install scripts and paths | Replace personal paths/sudoers/bootstrap assumptions with a reviewed, portable installation contract and separate privileged adapter setup. |
| Policy/config/environment names | Define one canonical public schema and safe examples. Move production policy and site substitutions to Homelab. Do not preserve schema 1 or old env vars solely for compatibility. |
| Docs/specs/tests/CI | Replace the product name consistently, scrub all site values, use synthetic fixtures, and add packaging/config/secret scans. Keep phase workflow and current roadmap. |
| Old compatibility facade and schema migration | Decide through architecture review whether any installed private consumer still needs it. Retain only inside the private transition plan with an owner and removal date; do not publish it by default. |

### Envoy name and distribution conflict

“Envoy” is already the name of a prominent CNCF edge/service proxy. CNCF
branding guidance prohibits using CNCF's name as another product name and its
project-naming guidance advises avoiding existing trademarks. Exact reuse is a
serious trademark/brand-clearance risk. PyPI also already has an
`envoy` package, and `envoy-server` currently installs an `envoy` executable
and import namespace. Do not publish under the bare `Envoy`/`envoy` names until
legal/brand review and registry checks are complete. Prefer a distinct product
brand; if the owner still chooses Envoy, approve the exact qualified brand,
distribution, import namespace, CLI, domain, and trademark position first.

## 6. Open-source readiness and decisions

### Required before creating or publishing the public repository

- [ ] Approve the product name/brand and package, import, CLI, and repository
  identifiers after CNCF trademark and package-registry review.
- [ ] Approve a license and copyright holder. **Candidate recommendation:**
  Apache-2.0 for a reusable infrastructure/security tool because it is
  permissive and includes an express patent grant. This is a recommendation,
  not a selection; do not add a license file without approval.
- [ ] Approve a fresh sanitized repository and initial attribution; preserve
  the existing private repository and remote without history rewrite.
- [ ] Approve the public-file allowlist and private Homelab file ownership
  table in this report.
- [ ] Replace fixed site/service/account/path assumptions with injected
  configuration and adapter boundaries; add fictional examples.
- [ ] Ensure requesters cannot configure authorization, approval, or executor
  trust roots; all policy remains protected and server-side.
- [ ] Add `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, product README, and
  approved `LICENSE`; state support and vulnerability-reporting process.
- [ ] Run established secret scanning on the export and its new history; add
  scanning to CI/pre-commit only after an approved baseline review.
- [ ] Verify packaging, clean-clone installation, CLI, tests, config/schema
  validation, static/type/security/dependency checks, and documentation links.
- [ ] Check third-party dependency/action licenses and pin/provenance policy.

### Recommended release verification

1. Build an allowlisted sanitized export in a separate directory/repository;
   do not edit this repository into the public repository in place.
2. Inspect every exported file, generated wheel/sdist, CI artifact, test
   fixture, and Git commit metadata for private content.
3. Run secret scanning over all exported files and every new commit snapshot;
   review all findings without printing candidate values.
4. From a clean clone, install the package in an isolated supported Python
   environment, run `--help`, exercise read-only synthetic configuration, and
   run all quality/security/package/config checks.
5. Exercise gateway denial, policy tampering, approval misuse/replay, and
   adapter no-side-effect cases on disposable targets only.
6. Review release artifact contents and documentation links; keep publishing
   and remote changes behind separate explicit approval.

## 7. Prioritized implementation plan after approval

| Priority | Work | Exit evidence |
|---|---|---|
| P0 | Decide brand/trademark, package/CLI identifiers, license/copyright, and new repository ownership. | Written owner decisions; no names reserved or published by this audit. |
| P1 | Create public-file allowlist and private Homelab separation mapping; establish a fresh sanitized checkout without `.git` history. | Two trees inventory cleanly; every file has one owner; original repo/remote intact. |
| P2 | Extract/refactor the minimal product package from private wrappers; remove fixed homelab service/account/path assumptions and obsolete runtime compatibility only after consumer review. | Clean package installs independently; no Homelab configuration is required; security contract/tests pass. |
| P3 | Add public README, contribution/security/changelog docs, approved license, synthetic examples, and generic phase docs. | Open-source checklist reviewed; no personal docs/configs in Envoy export. |
| P4 | Add CI security/config/packaging/clean-clone checks and run them on the exact candidate. | Reproducible green checks with scanner findings reviewed; artifact inventory recorded. |
| P5 | Prepare a separate publication proposal for user review. | Exact repository, remote, files, history, license, artifacts, and release diff approved before any create/publish/push action. |

## 8. Decisions requiring owner approval

1. Whether to retain “Envoy” despite the CNCF project-name and trademark risk,
   or select a distinct name.
2. Exact distribution/import/CLI/repository names; bare `envoy` is already
   occupied/conflicting on PyPI.
3. License and copyright holder. Apache-2.0 is recommended for consideration,
   not selected.
4. Creation of a new public repository with fresh sanitized history and the
   attribution identity for its initial commit.
5. The file allowlist and the private Homelab destination structure.
6. Which current installed Homelab consumers require any legacy command/path
   compatibility during a private deployment migration.
7. Which environments/adapters Envoy v1.0 will support; current host-specific
   operation coverage is not a general support promise.

## Sources checked for naming/license planning

- [CNCF Envoy project](https://www.cncf.io/projects/envoy/)
- [CNCF Brand Guidelines](https://www.cncf.io/brand-guidelines/)
- [CNCF project lifecycle and naming conventions](https://contribute.cncf.io/projects/lifecycle/)
- [PyPI `envoy`](https://pypi.org/project/envoy/) and [PyPI `envoy-server`](https://pypi.org/project/envoy-server/)
- [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)
