# Verification record: <name>

## Requirement-to-evidence traceability

| Requirement ID | Test/check/evidence | Result | Artifact or command |
|---|---|---|---|
| <ID> | <specific check> | Not run | <path> |

## Unit, integration, installed-layout, and end-to-end tests

Commands, environment, results, and failures.

## Security tests

Include malformed input, unauthorized principal, default-deny, replay/race,
permission/path attacks, timeout/resource exhaustion, and secret redaction as
relevant.

## Deployment verification

Exact approved revision/host/operation, preflight, health and dependent-service
checks, audit evidence, and operator approval reference. Mark not applicable
for local-only work. Never infer deployment from local tests.

## Known limitations

List untested assumptions, unavailable evidence, and residual risk.

## Completion decision

Planned | Design Approved | In Development | Code Complete |
Verification Pending | Release Ready | Released, with reviewer and date.

Release Ready requires all applicable quality-standards evidence. Released
requires authorized runtime verification, or a reviewed non-deployment phase
to record why runtime evidence is not applicable.
