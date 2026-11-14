# Infrastructure adapters

Adapters translate an authorized logical operation into a fixed
infrastructure-specific action. They do not authenticate callers, choose
policy, create approval, or decide whether to audit. Every adapter call must
carry the already validated principal/request context and a policy decision
reference for traceability.

An adapter contract must declare supported resource types and operations,
input/output schemas, privilege needs, timeout and output bounds, expected
side effects, idempotency, health checks, failure modes, and rollback/data
recovery limitations. Inputs are canonical typed values, never commands,
arbitrary paths, environment files, or user-selected binaries.

Planned adapter domains include Docker and Compose, systemd, narrowly approved
Ansible operations, and bounded scaling. Kubernetes and other environments
remain candidates requiring their own threat and trust-boundary design. Docker
socket access is treated as host-root authority. Add one adapter at a time;
deny by default if the adapter or declared operation is unavailable.
