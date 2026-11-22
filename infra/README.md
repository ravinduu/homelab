# Homelab infrastructure

[`compose/`](compose/README.md) is the desired Compose source for the Debian
homelab, maintained on the Mac. It covers the four projects inspected over SSH
on 2026-11-22: Arr, Jellyfin, Pi-hole and monitoring. See the Compose README for
the live assessment, environment setup, validation and adoption procedure.

`terraform-iam/` contains the separate IAM configuration. Docker network
Terraform lives under `../terraform/`; it currently manages `homelab-media` and
`homelab-monitoring-v2`. The existing Compose projects own `arr-network` and
`monitoring-network`. Changing network ownership requires a deliberate migration.

`policy/` contains the existing operations policy files. The legacy operations
wrappers under `../scripts/` are separate from Compose administration.

Keep credentials, runtime env files, Terraform state and application data outside
Git. The Compose changes in this checkout have not been deployed.
