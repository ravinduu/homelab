# Homelab

Infrastructure configuration for the Debian homelab, maintained from the Mac.

- [`infra/compose/`](infra/compose/README.md): four Compose projects covering Arr,
  Jellyfin, Pi-hole and monitoring. Includes environment templates, the live
  assessment from 2026-11-22, validation and adoption/rollback instructions.
- [`terraform/environments/home/`](terraform/environments/home/): Terraform-managed
  Docker networks, separate from the networks currently owned by Compose.
- `infra/terraform-iam/`: IAM configuration.
- `infra/policy/`: existing operations policies.
- `scripts/`: Compose validation/preflight and legacy homelab operations wrappers.

Validate Compose from this checkout without changing the running homelab:

```sh
python3 scripts/check-compose.py --ssh homelab-terraform
ssh homelab-terraform 'sh -s' < scripts/check-compose-host.sh
```

Use `python3 scripts/check-compose.py` if Docker Compose is installed locally.
The server configuration targets Linux paths and devices; Docker Desktop on the
Mac is not the runtime target.

The Compose source preserves existing data paths and project names, pins the
observed running images by digest, bounds container logs and keeps credentials
outside Git. Read the [Compose runbook](infra/compose/README.md) before adoption.
Local implementation does not deploy to the server.
