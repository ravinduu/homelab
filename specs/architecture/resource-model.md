# Resource and operation model

Current Phase 2 uses a deliberately small positional CLI vocabulary:
`status` and `restart jellyfin`. It has no generalized resource schema.

Future operations should use stable operation identifiers and typed resource
references. A request should contain only validated data such as operation,
resource type/ID, bounded options, and a correlation identifier. It must not
encode shell syntax, paths, arbitrary service names, Docker flags, executable
names, or environment variables. The server resolves a public logical
resource reference through protected inventory/policy to its canonical target
and validates that the target remains in scope at execution time.

Each operation definition should specify required permission, resource scope,
constraints, approval obligation, timeout, side effects, idempotency,
result schema, audit fields, and recovery semantics. Inventory disclosure
must be distinct from mutation. Schema and operation versions require
compatibility policy; unknown operations and fields deny unless explicitly
declared safe extensions.
