# Identity and authentication

SSH currently authenticates a connection under shared Unix account `agent`.
It does not distinguish individual agents, humans, or automation principals.
The gateway records `SUDO_USER` as a caller label for the narrow approval
binding; that label is not a cryptographic principal identity.

Target identity must derive from trusted transport metadata or a
server-verified credential, never a request-body name or agent self-description.
Authentication answers which credential connected; mapping identifies the
registered actor; policy determines permitted operations; human approval
confirms a specific sensitive request. Audit correlates these without storing
secrets.

Phase 3 must define stable principal identifiers, credential ownership,
shared-account treatment, mapping lifecycle, revocation, and ambiguous mapping
behavior. Phase 4 is expected to introduce per-agent credentials/isolation.
Per-agent authorization is not a current capability.
