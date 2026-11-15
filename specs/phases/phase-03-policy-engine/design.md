# Phase 3 technical design — versioned policy engine

**Status:** Prior implementation design; its schema compatibility decision is
superseded by `specs/product/compatibility-policy.md` and the Phase 3
assessment. Update before further Phase 3 implementation.
**Scope:** Generalize policy for the existing `status` and `restart jellyfin`
operations, retaining exact request syntax, paths, approval store, and execution
checks. No new executable operation or production deployment is included.

## Decisions

1. **Phase 3 principal boundary:** derive the requester only from the trusted
   `SUDO_USER` value captured by the root gateway. A root-owned policy maps the
   exact Unix account `agent` to the stable compatibility principal
   `unix:agent`. This is one shared account principal, not an individual agent
   identity. Unknown accounts deny. Phase 4 must replace or extend this
   mapping with per-credential identity before claiming per-agent isolation.
2. **Policy schema:** schema 2 has exact top-level keys `schema`, `revision`,
   `principals`, `roles`, and `services`. Principals map Unix account names to
   stable principal IDs and role IDs. Roles contain an ordered list of exact
   operation/resource permissions. Service identity fields remain fixed data
   consumed by the existing Docker identity check.
3. **Composition:** all assigned roles contribute. Any matching explicit
   `deny` wins. Otherwise at least one matching `allow` is required. No match,
   unknown role/principal, malformed request, or invalid policy denies.
   Wildcards, arbitrary constraints, inheritance, and caller-supplied identity
   are unsupported in this version.
4. **Resources:** operations use exact canonical IDs: `host:local` for status
   and `service:<name>` for restart. Permission matching is exact; no path or
   prefix matching is introduced.
5. **Approval:** `require_approval` is a boolean obligation returned with the
   allow decision. The existing single-use restart approval remains mandatory
   at execution and remains bound to the Unix requester label for compatibility.
   Policy permission cannot create or bypass approval.
6. **Migration:** The prior design proposed schema 1 runtime compatibility.
   Under the adopted pre-1.0 policy, the preferred release design is one
   schema 2 runtime. Convert the old schema offline, compare decisions, and
   stage the schema 2 config for an administrator-reviewed canary transition.
   Keep the old protected config for rollback, not as a second evaluator in the
   new runtime. The live server is unchanged.
7. **Audit:** fixed event fields add stable principal, policy revision, and
   stable decision reason. No policy contents, approval contents, arbitrary
   request values, or exception details are logged.

## Evaluation flow

Parse the existing exact argv to a typed operation/resource. Resolve the
trusted Unix account using the protected policy mapping. Validate policy once
at gateway startup, including duplicate-key rejection, exact keys, bounded
file size, supported schema, and reference integrity. Evaluate all exact
permission matches and return a decision containing allow/deny, reason,
revision, principal, and approval obligation. Dispatch only an allowed
decision. A restart still consumes approval before any Docker inspection and
retains the existing identity check and fixed full-ID restart.

## Failure behavior

Policy parse, schema, mapping, role, or reference errors fail closed before
operation execution. Unknown principals and resources deny. Explicit deny
overrides any role allow. A required or missing approval cannot be satisfied
by policy. The gateway emits a bounded denial reason and returns a stable
nonzero gateway denial code. Offline schema conversion is covered by
decision-equivalence fixtures if required for the deployment transition.

## Server development test boundary

Development validation uses only the separate canary namespace. Stage files
from a reviewed local revision, compare hashes, and have an administrator
install/update only canary paths. First test valid `status`, then stage a
canary policy variant that denies `status` and verify no inventory command is
run and the canary journal records denial. Restore the reviewed canary policy
and verify status again. Do not use `restart jellyfin` as an ordinary
development test: that targets the live service. A positive restart test needs
its own impact review, explicit approval, and recovery/health verification.
The original gateway and policy remain untouched.

## Rollback

On the canary, restore the administrator-preserved, hash-verified prior canary
policy and package revision, then verify `sudo visudo -c`, canary status, and
denial behavior. If authorization is uncertain, disable only the canary sudoers
include and confirm denial before investigating. Preserve canary approval and
audit state. No production gateway rollback or policy promotion is part of
this phase implementation.
