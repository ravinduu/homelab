# Quality standards and production Definition of Done

**Status:** Adopted project policy. A phase is not Released merely because its
code or unit tests are complete.

## Lifecycle statuses

Use exactly these statuses for phases and release candidates:

| Status | Meaning |
|---|---|
| Planned | Scope is a proposal; implementation has not started. |
| Design Approved | Requirements, architecture, threat boundary, test plan, compatibility decisions, and rollback are reviewed. |
| In Development | Implementation or required refactoring is underway. |
| Code Complete | Scoped implementation and developer tests are complete; release verification is not. |
| Verification Pending | One or more required automated, integration, security, install, runtime, or rollback checks remain. |
| Release Ready | Every applicable Definition of Done item has evidence and independent review; an authorized release decision remains. |
| Released | Exact immutable revision was approved, installed through the authorized process, verified, documented, and has a tested rollback result. |

Never label unverified work `Complete`, `Release Ready`, or `Released`.
Historical operational reports should be labelled Reported until rechecked.

## Definition of Done

Every phase release must record evidence for each applicable item below. Mark
non-applicable items with a reason and reviewer; do not omit them.

1. **Requirements:** User-visible vertical slice, scope, exclusions, threat
   model, dependencies, and measurable acceptance criteria are reviewed.
2. **Architecture and design:** Trust boundaries, module ownership, policy and
   data formats, failure behavior, compatibility decisions, and refactoring
   disposition are approved before implementation.
3. **Implementation quality:** One canonical implementation per
   responsibility; no unexplained dead code or compatibility layers; bounded
   inputs, outputs, time, and resource use; types and errors are explicit.
4. **Security review:** Threat-driven review covers identity, authorization,
   approval, filesystem and process boundaries, secrets, logging, privilege,
   and failure modes. Findings have owners and disposition.
5. **Automated tests:** Unit tests cover successful behavior and boundary
   cases. Integration tests cover component wiring and installed layout.
   End-to-end tests exercise a disposable or isolated target. Negative security
   tests prove denial before side effects, malformed/tampered input handling,
   replay/race behavior, timeouts, and secret redaction as applicable.
6. **Static and dependency checks:** Formatting, lint, type checking, security
   analysis, and vulnerability scanning run on the exact release revision.
   Exceptions are scoped, justified, and reviewed.
7. **Packaging and installation:** Build/install artifacts are reproducible
   from reviewed immutable inputs; ownership, modes, destination collisions,
   partial-failure cleanup, and configuration validation are tested.
8. **Deployment verification:** The exact approved revision and target are
   recorded. Preflight, service health, dependent services, audit records, and
   expected denial behavior are checked. Production work follows the
   repository's Observe/Plan/Review/Approve/Execute/Verify/Document policy.
9. **Rollback verification:** Recovery is tested in an isolated/canary
   environment. It restores a known-good state without broadening authority or
   losing required audit records.
10. **Operational documentation:** Installation, configuration, dev test,
    runtime verification, failure handling, rollback, support ownership, and
    evidence links are current.
11. **Release evidence:** Reviewer, date, source revision, artifact hashes,
    commands/results, exceptions, residual risks, and release decision are
    recorded. No readiness claim is inferred from source presence.

## Minimum Python quality gates

The initial toolchain uses the standard-library `unittest`, Ruff for formatting
and linting, mypy for static types, Bandit for Python AST security findings,
`pip-audit` for known Python dependency vulnerabilities, `build` for wheel
validation, and shell syntax validation for installers. It adds no runtime
dependencies. Dependency versions are pinned in `requirements-quality.txt`;
transitive dependency locking and hashes are a release-readiness item.

Canonical commands are defined in the repository `Makefile` and run in CI.
CI is evidence for code checks only; it cannot establish server installation,
runtime health, or rollback verification. Findings from security scanners
require reviewed disposition, not blanket suppressions.

## Current phase status rule

Phases 0–3 currently have local or reported operational work, but the
repository has no prior CI/static-analysis/release-evidence history and the
server state is not rechecked by a standards update. Set them to
`Verification Pending` until each phase's own release evidence is complete.
Phases 4–7 remain `Planned`.

## Phase completion and v1.0 readiness

A phase is complete only when its specified user capability works from the
supported install, the acceptance criteria pass, and the evidence record names
the exact revision, environment, checks, security review, operational
verification, and tested recovery. Code Complete means implementation work
ended; it is not phase completion. Verification Pending means any required
evidence remains. Mark Released only after the authorized release and
verification are documented.

The v1.0 release requires all seven roadmap phases to be Released, then a
combined end-to-end demonstration of the product success criteria in
`specs/product/vision.md`: independent agent clients, independently
authenticated hosts, protected policy, exact approval and resume behavior,
bounded execution, verified outcomes, correlated redacted audit, explicit
partial failures, reproducible install, and exercised rollback. No skipped
phase may be relabeled complete to satisfy this gate.
