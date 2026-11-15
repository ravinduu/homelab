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

Phase 3 defines the compatibility principal `unix:agent`, resolved from the
trusted `SUDO_USER` supplied to the root gateway and mapped by protected policy.
This represents the shared Unix account only; it does not distinguish agents,
humans, or automation using that account. Unknown accounts deny. Credential
ownership, revocation, and per-credential mapping remain Phase 4 work.
