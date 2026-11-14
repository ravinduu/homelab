# Trust boundaries

**Current:** Repository files and local client are requester-controlled. SSH
terminates on the host as restricted `agent`. The inventory wrapper is the
documented read-only Docker path. Root-owned gateway, policy, approval helper,
and approval state form the privileged boundary. Recheck live ownership before
any operational decision.

| Boundary | Untrusted input | Required control |
|---|---|---|
| Client → SSH | Arguments, client policy | Restricted credential/account, server parsing |
| SSH → principal | Shared Unix identity, forwarded environment | Trusted credential-to-principal mapping |
| Gateway → policy | Policy file/path | Root protection, strict versioned validation, deny on error |
| Gateway → approval | Record and races | Exact binding, expiry, single-use atomic consumption |
| Executor → adapter | Operation/resource values | Fixed typed interface, bounds, no shell or arbitrary path |
| Git → release | Mutable checkout/build context | Independent review and immutable protected staging |
| Host → audit | Host compromise/privileged operator | Restrict, retain/forward where designed; root can tamper locally |

Agent identity, SSH authentication, authorization, and human approval are
separate. See [ADR-0001](../../docs/adr/0001-gateway-security-boundary.md)
and [ADR-0003](../../docs/adr/0003-server-side-policy.md).
