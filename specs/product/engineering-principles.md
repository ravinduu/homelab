# Engineering principles

**Status:** Adopted project policy. Applies to new work and to refactoring that
is required to make a feature safe and maintainable.

1. **Production-oriented development:** Build complete, deployable increments
   with explicit operating and recovery behavior. Do not accumulate demos or
   proof-of-concept paths as product architecture.
2. **One canonical implementation per responsibility:** Keep one policy
   evaluator, one request model, one approval authority, and one supported
   runtime configuration for a released capability.
3. **Simplicity over unnecessary abstraction:** Add a layer only when it
   removes real duplication, isolates a trust boundary, or enables a required
   capability. Prefer explicit data and small functions over speculative
   frameworks.
4. **Explicit compatibility:** Preserve behavior only when a requirement,
   external consumer, or controlled production transition justifies it.
   Document the owner, scope, and removal condition of every compatibility
   layer.
5. **Refactoring is part of feature work:** Reuse suitable components, refactor
   unsuitable ones, replace obsolete implementations, and delete dead paths
   when a scoped change makes them obsolete.
6. **Security by design:** Authenticate identity independently from
   authorization and human approval. Enforce bounded operations, default deny,
   least privilege, protected policy, and fail-closed behavior at the trusted
   server boundary.
7. **Testability and observability:** Design deterministic boundaries that can
   be tested without a production host. Emit bounded, attributable events that
   exclude secrets and uncontrolled command output.
8. **Clear module boundaries:** Keep request parsing, identity resolution,
   policy decisions, approval, execution, and audit responsibilities explicit.
   Adapters cannot bypass shared controls.
9. **Automated quality checks:** Run agreed tests, formatting, linting, type
   checks, security analysis, dependency audit, and packaging validation in
   local tooling and CI. Record failures; never describe an unrun check as
   passing.
10. **Incremental deployable releases:** Each phase has a user-visible
    vertical slice, explicit prerequisites, a supported install, and
    verifiable runtime behavior.
11. **Safe migration and rollback:** Migrations preserve a known-good state,
    compare old and new decisions where authorization changes, and include
    tested recovery. A rollback may not broaden access.
12. **No unverified readiness claims:** Local implementation, automated
    verification, canary operation, and production release are distinct states.
    Use the quality lifecycle and evidence required by
    [`quality-standards.md`](quality-standards.md).

The project is pre-1.0. Internal APIs and policy formats may change under the
rules in [`compatibility-policy.md`](compatibility-policy.md).
