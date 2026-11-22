# Ansible

Run these commands from `ansible/`.

```sh
ansible-galaxy collection install -r requirements.yml
ansible-vault edit group_vars/homelab/vault.yml
```

Vault keys (use existing application credentials):

```yaml
vault_pihole_webpassword: "..."
vault_arr_radarr_api_key: "..."
vault_arr_sonarr_api_key: "..."
vault_grafana_admin_password: "..."
```

Host settings live in `inventory.yml` and `group_vars/homelab/vars.yml`.
Set `monitoring_grafana_admin_user` to the existing Grafana username.
Grafana's environment credentials only initialize a new database.

```sh
ansible-playbook site.yml --syntax-check
ansible-playbook site.yml --ask-vault-pass --ask-become-pass --check --diff
ansible-playbook site.yml --ask-vault-pass --ask-become-pass
```

Select roles with `--tags storage,docker,pihole,jellyfin,arr,monitoring`.
For just the remaining stacks, use `--tags arr,monitoring`.
Tagged runs need their prerequisites already installed.

Stacks are copied from `../docker/` to `/opt/stacks/<stack>`, with protected
`.env` files. Arr uses UID/GID 1000:1000; `/mnt/media` must be mounted and writable
by that user. Check mode skips staging files into new stack directories.

Back up application data before deployment. Monitoring expects existing
`prometheus_data` and `grafana_data` volumes. On a fresh server only, create them:

```sh
docker volume create prometheus_data
docker volume create grafana_data
```
