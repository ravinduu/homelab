# Privileged execution boundary

Current gateway uses Python isolated mode, fixed paths, exact argv,
`shell=False`, fixed child environment, timeouts, and generic errors. Status
delegates to inventory. Restart checks policy and approval, inspects configured
container identity/Compose labels, then restarts only the full verified ID.
These safeguards apply only to the two implemented operations.

Target core validates typed request, resolves policy obligations, records the
decision, dispatches a bounded adapter call, enforces time/output/resource
limits, normalizes results, and records outcome. No client supplies shell,
executable path, environment, Compose file, playbook, or arbitrary manifest.
Adapters declare capabilities, schemas, side effects, idempotency, timeout,
and recovery semantics. Docker socket access is effectively host-root
authority; a read-only mount does not restrict API methods.
