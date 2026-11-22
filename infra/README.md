# Infrastructure

`terraform-iam/` contains AWS IAM configuration.
Docker Compose files live in [`../docker/`](../docker/README.md), and Docker
network Terraform lives in `../terraform/environments/home/`.

Terraform manages `homelab-media` and `homelab-monitoring-v2`;
Compose manages `arr-network` and `monitoring-network`.
