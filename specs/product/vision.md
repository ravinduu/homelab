# Product vision

**Status:** Proposed long-term direction; grounded in the existing supervised
Debian implementation. **Review date:** 2026-11-14.

## Problem

Infrastructure operators need to delegate bounded observation and maintenance
operations to agents and automation without giving those clients unrestricted
shell, Docker, host, or administrator authority. Client-side prompts and
allowlists cannot secure a remote host. A trusted server boundary must verify
who made a request, what operation is allowed, what target it applies to, and
whether human approval is required.

## Mission and users

Build an agent-independent framework for authenticated, explicitly authorized
infrastructure operations. Users include human CLI operators, AI coding
agents, custom agents, CI/CD systems, and automation platforms. Clients use a
stable, bounded operation contract; the server retains control of policy and
execution.

## Primary use cases

- Discover host and service health through restricted, sanitized inventory.
- Request a narrowly scoped operation such as an approved service restart.
- Require a separate administrator approval for sensitive operations.
- Audit requests and outcomes without recording secrets or arbitrary command
  output.
- Add infrastructure-specific adapters behind a common authorization and
  execution boundary.
- Progress from one Debian host to documented multi-server management only
  after identity, policy, transport, and fleet consistency are designed.

## Environment direction

**Observed foundation:** Debian, Python scripts, SSH, sudoers, Docker, and
Docker Compose. **Planned candidates:** Debian/Ubuntu, systemd, approved
Ansible workflows, Kubernetes, and multiple hosts. These are roadmap targets,
not current support claims. Each target requires adapter-specific design,
threat review, tests, and acceptance evidence.

## Product boundaries

- Requests are data with a bounded schema, never shell programs.
- The gateway is not a public unrestricted administrative API.
- Authentication, principal identity, authorization, and human approval are
  distinct checks.
- Policy, approvals, executables, release inputs, and secrets are protected
  from requesters.
- Clients do not gain privilege merely by being an AI agent or by using SSH.
- Deployment, destructive data operations, and host/network administration
  require separately scoped approval procedures.

## Long-term direction

Evolve in gated phases: reproducible foundation; read-only discovery; narrow
secure gateway; generalized verified-principal policy; remote credential and
transport hardening; bounded execution adapters; agent integrations; then
multi-server operations. Preserve compatibility while each capability is
introduced and independently verified.
