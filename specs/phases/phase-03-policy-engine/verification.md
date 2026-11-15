# Phase 3 verification record

**Status:** Verification Pending

| Requirement | Evidence needed | Result |
|---|---|---|
| Canonical schema and evaluator | Schema decision, exact-key/reference validation and decision matrix | Schema 2 evaluator is local; schema 1 runtime reader remains under review |
| Gateway integration | Schema 2 allow/deny through actual gateway; denial before side effects | Direct evaluator and selected gateway tests exist; installed path not proven |
| Security behavior | Malformed/duplicate/oversized/tampered policy, unknown identity/scope, approval and no-execution negatives | Partial local tests; complete requirement trace pending |
| Installed runtime | Isolated package/entrypoint against protected temporary config on disposable host | Not recorded |
| Quality gates | Unit, Ruff, type, security, dependency, package and CI on exact candidate | Prior unit/Ruff/shell checks reported; full CI/tool suite not executed |
| Runtime and rollback | Canary schema 2 allow/deny, audit, exact hashes and tested policy/package restoration | Not verified; earlier canary status is a separate reported state |

The schema 1 runtime removal recommendation is recorded in
`specs/product/compatibility-policy.md`; implementation is not removed by this
verification record. Do not contact or modify the server without the separate
approval required by `AGENTS.md`.
