# Homelab

My Debian server configuration, managed from my Mac.

- [`docker/`](docker/README.md) — Arr, Jellyfin, Pi-hole and monitoring.
- [`ansible/`](ansible/README.md) — server setup and stack deployment.
- `terraform/environments/home/` — Docker networks.
- `infra/terraform-iam/` — AWS IAM configuration.

Deploy:

```sh
cd ansible
ansible-playbook site.yml --ask-vault-pass --ask-become-pass
```

Deploy one stack with `--tags arr`, `jellyfin`, `pihole` or `monitoring`.
Add `--check --diff` to preview changes.

Check Compose files from the Mac:

```sh
python3 scripts/check-compose.py --ssh homelab-terraform
ssh homelab-terraform 'sh -s' < scripts/check-compose-host.sh
```

Omit `--ssh` when Docker Compose is installed locally. The host check runs on
Debian and checks mounts, data paths, devices and existing monitoring volumes.
Keep secrets in Ansible Vault and leave `.env` files and Terraform state out of Git.
