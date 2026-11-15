# Phase 0 design — repository foundation

**Status:** Draft for foundation completion; this is an enabling milestone, not
one of the seven product releases.

## Architecture review

| Component | Decision | Reason |
|---|---|---|
| Existing gateway, client, inventory, and approval code | Reuse as evidence; do not extend in this documentation milestone. | Product code belongs to Phases 1–3 and is assessed against their accepted designs. |
| Product/architecture documents and ADRs | Refactor and consolidate. | One source of truth for product goal, boundaries, and decisions. |
| Compatibility and quality guidance | Replace implicit rules with explicit project policies. | Pre-1.0 changes need justified compatibility, not parallel legacy behavior. |
| Existing operational reports | Retain as dated reported evidence. | Do not rewrite history or imply independent verification. |

## Design and verification

The roadmap, requirements, phase contracts, and templates share a single
SPEC → DESIGN → TASKS → BUILD → VERIFY → RELEASE lifecycle. Phase statuses
describe release evidence, not code presence. Documentation changes do not
authorize server actions. Local quality checks run through the existing
Makefile/CI; deployment and production verification remain administrator
controlled.

## Alternatives and tradeoffs

Keep existing phase folders and narrow existing specs rather than replacing
the repository layout. Use `spec.md` as the canonical phase specification
filename; no runtime compatibility alias is warranted for internal docs.
