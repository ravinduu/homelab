# Configuration and policy integrity

Phase 2 server policy is protected JSON schema 1 with a fixed Jellyfin
mapping. Installer/runtime validate ownership, modes, paths, and structure.
`infra/policy/server-policy.json` is a local proposal, not proof of installed
policy. Client allowlist is not authoritative.

Future configuration needs explicit schemas/versions, strict parsing
(including duplicate-key rejection), bounded size, safe file opening,
protected parents, administrator-controlled updates, and migration/rollback
tests. Reject unknown fields unless explicitly extensible. A digest alone
does not establish trust if one untrusted actor controls both artifact and
expected digest.
