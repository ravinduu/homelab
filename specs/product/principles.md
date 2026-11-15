# Product and engineering principles

1. **Security by default:** expose only reviewed operations and minimum data.
2. **Least privilege:** requesters receive no general shell, Docker socket, or
   broad sudo authority.
3. **Default deny:** unknown principal, operation, resource, constraint, or
   policy state means deny.
4. **Agent independence:** protocol semantics do not depend on a vendor's
   prompting, identity claims, or client-side enforcement.
5. **Server-side enforcement:** the trusted gateway is authoritative for
   identity mapping, authorization, approval validation, and execution.
6. **Human approval:** sensitive operations require explicit approval that is
   separate from request authentication and bound to a precise operation,
   resource, principal, and bounded validity period.
7. **Auditability:** record attributable decisions and outcomes while excluding
   secrets, credentials, and uncontrolled command output.
8. **Reproducible installation:** reviewed immutable inputs, explicit
   compatibility, integrity checks, and administrator-controlled promotion.
9. **Fail closed:** malformed, stale, ambiguous, unavailable, or tampered
   policy/approval state cannot authorize execution.
10. **Justified compatibility:** preserve installed behavior only for a
    documented requirement or controlled production transition; remove
    obsolete internal paths when their consumers are migrated. See
    [`compatibility-policy.md`](compatibility-policy.md).
11. **Modular adapters:** infrastructure-specific behavior remains behind
    narrow interfaces; adapters cannot bypass identity, policy, audit, or
    approval controls.
12. **Minimal trusted computing base:** keep privileged code, dependencies,
    parsers, and configuration surface small and reviewable.
13. **Safe observability:** inventory and logs are bounded, sanitized, and
    designed against secret disclosure and resource exhaustion.
14. **Evidence before claims:** distinguish code, local tests, installation,
    and live operational verification.
