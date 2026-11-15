# Phase 6 tasks — independent agent clients

**Status:** Planned; deliver one client protocol increment at a time.

| # | Vertical slice | Completion criterion | Status |
|---|---|---|---|
| 1 | Stabilize operation and approval-resume contract | Versioned request/result, capability discovery, denial and resume states accepted. | Todo |
| 2 | Implement the MCP adapter beside the CLI contract | Thin adapter authenticates and forwards typed requests only. | Todo |
| 3 | Add independent client conformance | At least two agents use the same contract; neither can bypass server checks. | Todo |
| 4 | Verify adversarial behavior | Auth failure, spoofed identity, malformed/oversized request, replay, secret and policy bypass tests pass. | Todo |
| 5 | Package and operate | Client setup, credential removal, runtime audit correlation and rollback documented and tested. | Todo |
