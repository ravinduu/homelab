# Phase 3 task breakdown

**Status:** In progress; implementation remains local until separately
reviewed and installed in the canary environment.

1. Add policy schema 2, typed requests/decisions, strict schema validation,
   trusted Unix-account principal resolution, deterministic role evaluation,
   deny precedence, and stable decision reasons.
2. Integrate evaluation in the gateway before status inventory or restart
   approval/Docker work. Keep the exact CLI behavior and use one canonical
   runtime policy schema. Resolve the schema 1 reader per compatibility policy.
3. Add representative schema 2 policy fixtures and offline schema-conversion
   decision comparisons; do not retain schema 1 as a second runtime path.
4. Add positive, negative, malformed/tampered, role-conflict, boundary-scope,
   unknown-principal, approval-obligation, and no-execution tests.
5. Extend canary bootstrap validation and package staging for Phase 3 policy;
   preserve separate canary paths and first-install refusal.
6. Document local verification, hash review, administrator-only canary update,
   safe server checks, negative policy testing, restart approval boundary, and
   canary rollback. Do not execute remote changes in this implementation.
7. Record requirement-to-test evidence, known limitations, and phase/roadmap
   status after verification. Mark Released only after the full production DoD.
