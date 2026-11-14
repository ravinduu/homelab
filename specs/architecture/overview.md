# Architecture overview

**Status:** Target architecture proposal; current implementation is narrower.

```mermaid
flowchart LR
  C[Agent / CLI / automation] -->|SSH authenticated request| T[Transport]
  T --> G[Root-controlled gateway]
  G --> I[Principal mapping]
  I --> P[Protected policy]
  P --> A[Human approval if required]
  A --> X[Bounded executor]
  X --> D[Infrastructure adapter]
  D --> H[Host / services]
  G --> L[Audit sink]
  X --> L
  Admin[Administrator] --> A
```

The client is untrusted. SSH proves control of a transport credential; it does
not establish role or permission. A trusted gateway maps verified transport
identity to a principal, evaluates protected policy, validates required
approval, calls a bounded adapter, and records decisions and outcomes.
Authentication, principal mapping, authorization, approval, and execution are
distinct checks.

The current tree contains scripts, shared approval primitives, static JSON
policies, client convenience validation, and standard-library tests. Gateway
requests are exactly `status` or `restart jellyfin`. Status delegates to the
approved inventory wrapper. Restart consumes a one-use approval, validates
protected policy and live container identity, then restarts the verified ID.
This is not a generalized API or policy engine.

```mermaid
sequenceDiagram
  participant R as Requester
  participant G as Gateway
  participant P as Protected policy
  participant A as Approval record
  participant E as Bounded executor
  participant L as Audit
  R->>G: typed operation request
  G->>P: principal, scope, constraints
  P-->>G: deny or allow + obligations
  G->>A: validate bound, unexpired, unused approval
  G->>L: decision
  G->>E: fixed operation/resource on allow
  E-->>G: bounded result
  G->>L: outcome
  G-->>R: sanitized response
```

Invariants: no caller command/path/environment reaches privileged execution;
adapter calls follow policy and approval; policy failure denies; promotion
inputs are requester-inaccessible; each host remains authoritative even in a
future fleet. See focused documents for [trust](trust-boundaries.md),
[identity](identity.md), [policy](policy-engine.md),
[approval](approval-system.md), [execution](execution-engine.md),
[transport](transport.md), [audit](audit.md), [threats](threat-model.md),
[configuration](configuration.md), [packaging](packaging.md),
[recovery](recovery.md), [resource model](resource-model.md),
[adapters](adapters.md), and [migration](migration.md).
