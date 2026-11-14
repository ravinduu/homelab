# Threat model

**Scope:** Current single-host SSH/gateway foundation and target framework. **Assumptions:** Host OS/root and SSH daemon are trusted until compromised; requester and arguments are untrusted; repository content is not production trusted; administrator actions are out of band. Shared Unix `agent` identity does not distinguish agents. Gateway is not public.

| Threat | Mitigations required / present | Residual risk and open work |
|---|---|---|
| Malicious/compromised AI agent | Exact allowlist, server policy, no shell, bounded inventory, separate approval | Shared identity prevents individual attribution; future protocol adds parser/DoS surface. |
| Stolen SSH credentials | Restricted account and exact sudo scope | Credential granularity/host-key practice need review; stolen credential can request allowed status and approved operation. |
| Shared Unix identities | Treat username as transport label | Approval currently binds label `agent`; per-agent identity/revocation are future work. |
| Privilege escalation | Root-owned files, exact sudoers, no Docker group/socket, fixed paths | Root compromise, interpreter/dependency issues, sudoers drift remain high impact. |
| Arbitrary command execution | Exact parser, fixed executables, `shell=False`, no caller paths | Future adapters/protocol decoders need independent negative/fuzz tests. |
| Docker socket exposure | Keep requester away from socket; isolate Docker adapter | Docker API access is effectively root; read-only socket mount still permits API calls. Existing monitoring exposure is documented, not changed here. |
| Policy tampering | Protected policy, strict schema, fail closed | Admin compromise and unsafe promotion; local proposal is not proof of installed policy. |
| Approval replay/race | Short expiry, binding, nonce, protected file, atomic consume | Filesystem semantics, clock drift, crash windows, retention and approver auth need review. |
| Symlink/filesystem attack | `lstat`, `O_NOFOLLOW`, ownership/mode/link/size checks | TOCTOU and filesystem assumptions need specialist review; do not overstate race freedom. |
| Compromised dependencies | Current scripts use standard library; minimize TCB | Python/runtime and OS supply chain remain trusted; future pinning/SBOM/provenance needed. |
| Network exposure | SSH-only initial channel; no public gateway | Firewall/router exposure not verified; Phase 4 needs evidence. |
| Denial of service | Timeouts, inventory cap, narrow request set | SSH flood, log/storage exhaustion, concurrency and rate limits remain open. |
| Unauthorized deploy/scale | Not implemented; working tree not trusted release input | Future actions need protected immutable promotion and separate approval. |
| Audit tampering | Authpriv events; avoid sensitive payloads | Root can alter local logs; retention, forwarding, integrity, disk-full policy unestablished. |
| Installer/update supply chain | Root-only staging, hashes, path checks, overwrite refusal, sudoers validation | Current host update provenance not independently verified; signed provenance needed before generalized updates. |

## Separate security concepts

SSH credential validation authenticates a connection. Principal mapping assigns a registered actor. Policy authorizes an operation. Human approval attests to a specific sensitive action. OS permissions constrain execution. Audit records the chain. Failure in any required layer denies execution.

## Unresolved decisions

Per-agent credential authority/lifecycle; policy language and promotion; approval identity/revocation; concurrency/rate limits; clock source; distributed audit; adapter isolation; release signing/provenance; network exposure verification; multi-server consistency and partial failure.
