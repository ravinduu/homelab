# Product goal and success criteria

**Status:** Product direction for the Phase 1–7 delivery plan. Current support
claims are recorded separately in `requirements.md` and `roadmap.md`.

## Product goal

Build an agent-independent infrastructure operations framework. An authorized
agent can securely inspect supported servers, produce an evidence-based health
summary, explain detected problems, recommend supported actions, request
human approval, continue after a valid approval, execute only the exact
authorized operation through a trusted gateway, verify the result, and return
an auditable report.

Agents submit bounded operation requests; they never receive privileges. Each
server remains authoritative for authentication, principal mapping, policy,
approval validation, execution, and audit.

## Users and working scenario

The operator enrolls a server and an agent identity. The agent requests a
health inspection and receives a timestamped, sanitized report with evidence
and explicit uncertainty. If a supported issue has a corrective action, the
agent explains the scope and impact, then submits a typed request. The gateway
re-authenticates the caller and checks protected policy. If approval is
required, a separately authorized human approves that exact principal,
operation, resource, and policy context. The agent resumes using the same
request identity; the gateway validates and consumes the approval once,
executes through the selected adapter, checks service health, and returns a
correlated outcome. Denials and partial failures are reported without claiming
success.

## Measurable v1.0 success criteria

The Phase 7 release is successful only when evidence demonstrates all of the
following on the exact release artifact:

1. At least two independently authenticated agent clients use the documented
   operation contract to inspect and request supported work; client-side
   allowlists cannot grant server authority.
2. At least two separately enrolled hosts return attributable health results
   and per-host status. An unavailable host or partial operation is represented
   explicitly and never reported as fleet-wide success.
3. Every supported request has a typed operation/resource, an authenticated
   principal, a server-side policy decision, and a correlated audit record.
   Unknown or malformed requests deny before side effects.
4. Each approval-required action is bound to the exact principal, operation,
   resource, expiry, and policy context; it cannot be replayed or consumed by
   another request. A valid approval allows the requesting workflow to resume
   without creating an alternate authorization path.
5. Every successful mutation is followed by its declared health verification.
   Failed verification returns failure or partial status with evidence; it
   never returns success.
6. Reports identify evidence source and observation time, redact secrets and
   uncontrolled output, distinguish facts from diagnosis/recommendation, and
   link the request, approval, decision, execution, and verification events.
7. Supported installs are reproducible from reviewed artifacts. Installation,
   upgrade, credential revocation, and rollback are demonstrated in isolated
   environments without broadening privilege or losing required audit data.
8. Required tests, negative security checks, static/type/security/dependency
   checks, package validation, and release review pass on the exact revision.

Each phase adds measurable criteria for its own vertical slice. v1.0 is not
claimed until all seven phase releases are accepted and these product-level
criteria pass together.

## Product boundaries

- Requests are bounded data, never shell programs or arbitrary playbooks.
- Transport authentication, identity, authorization, human approval, and
  execution are separate decisions.
- Policy, credentials, approvals, release inputs, and execution binaries are
  protected from requesters.
- Health summaries cite observed data and do not invent causes or claim an
  action succeeded without verification.
- Each host enforces its own policy, even when a future coordinator manages a
  fleet.
- Debian/SSH/Docker is the current implementation environment, not a promise
  that other operating systems or infrastructure adapters are supported.
