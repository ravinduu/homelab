# Phase 6 design — independent agent clients

**Status:** Planned; protocol selection and approval-resume design required.

## Architecture review

| Component | Decision | Reason |
|---|---|---|
| Typed gateway request/result | Reuse one versioned contract as the authority. | Client schemas are not authorization sources. |
| Current CLI | Reuse or refactor as the reference client after contract review. | Avoid a parallel client-only policy model. |
| MCP | Implement as a thin untrusted client integration beside the CLI contract. | MCP is the protocol explicitly selected for Phase 6; it cannot grant authority. |
| Client allowlists/prompts | Remove as security assumptions; retain only usability cues. | Gateway authenticates and authorizes every operation. |

## Required design decisions

Define capability discovery, schema/version behavior, authentication, bounded
responses, approval-required response, request correlation and safe resume
after approval. Approval must come from an independent authenticated human
path. Design at least two independent agent clients against the same contract;
do not add a second server authorization path.
