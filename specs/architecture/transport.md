# Transport security

SSH is the initial transport, using alias `home-server-agent` and restricted
account `agent`. Encryption and SSH authentication protect a connection, but
shared Unix identity does not identify individual agents or grant operations.
Server-side sudoers and gateway checks remain mandatory.

Phase 4 must define per-principal credentials, host key verification,
forced-command restrictions, rotation, revocation, connection limits,
forwarding restrictions, and incident recovery. Do not expose a public
gateway. Any future protocol requires authenticated encrypted transport,
replay protection, bounded requests/rates, explicit exposure policy, and
security review. MCP is an integration surface, not authorization.
