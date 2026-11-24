# Ansible

Run these commands from `ansible/`.

`site.yml` selects the service roles. Each service handles its own prerequisites
and credentials, then calls `roles/compose_stack` to stage files, deploy Compose,
and verify ports or HTTP endpoints. Storage and Docker installation remain
separate roles.

The shared role requires `stack_dir`, `stack_compose_src`, and
`stack_env_template` (an absolute template path). Optional directories, extra
configuration files, health checks, and containers needing network repair are
declared by each caller; defaults are in `roles/compose_stack/defaults/main.yml`.
Environment files stay mode `0600` with logging and diffs disabled. Check mode
defers staging when destination directories do not yet exist.

Run the local staging checks without Docker, SSH, or a Vault password:

```sh
ansible-playbook -i localhost, tests/compose_stack.yml --check --tags stack_test
```

These checks use temporary files to verify rendering, permissions, repeat runs,
option isolation, tags, and check-mode behavior. They do not deploy services.

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

The Arr keys are optional for existing installations: the role reads missing
keys from `/var/lib/homelab/arr/{radarr,sonarr}/config.xml` on the server,
including in check mode. Vault values take precedence. For a fresh installation,
add both existing API keys to Vault before deploying Arr with Unpackerr.

Host settings live in `inventory.yml` and `group_vars/homelab/vars.yml`.
SSH uses `~/.ssh/homelab-terraform` for `ravindu@192.168.1.10`, matching
the existing `homelab-terraform` SSH connection. Update
`ansible_ssh_private_key_file` in the inventory if your key is elsewhere.
Check the connection before running a playbook:

```sh
ansible homelab -m ansible.builtin.ping --ask-vault-pass
```

The vault password is needed even for this check because Ansible loads the
encrypted group variables before connecting.

Set `monitoring_grafana_admin_user` to the existing Grafana username.
Grafana's environment credentials only initialize a new database.
If `vault_grafana_admin_password` is missing or empty, the role reuses
`GF_SECURITY_ADMIN_PASSWORD` from the existing Grafana container, even if it is
stopped. Fresh installations require a password in Vault. This fallback does
not recover or reset the current Grafana login password.

```sh
ansible-playbook site.yml --syntax-check
ansible-playbook site.yml --ask-vault-pass --ask-become-pass --check --diff
ansible-playbook site.yml --ask-vault-pass --ask-become-pass
```

Select roles with `--tags storage,docker,pihole,jellyfin,arr,monitoring`.
For just the remaining stacks, use `--tags arr,monitoring`.
Tagged runs need their prerequisites already installed.

Monitoring web ports bind to `monitoring_web_bind_ip` (`192.168.1.10`).
After deploying, open Grafana at `http://192.168.1.10:3000` and Prometheus at
`http://192.168.1.10:9090` from the LAN. Set the bind address to `127.0.0.1`
for access through an SSH tunnel instead. Exporters remain on the Docker network.

Stacks are copied from `../docker/` to `/opt/stacks/<stack>`, with protected
`.env` files. Arr uses UID/GID 1000:1000; `/mnt/media` must be mounted and writable
by that user. Check mode skips staging files into new stack directories.

Back up application data before deployment. Monitoring expects existing
`prometheus_data` and `grafana_data` volumes. On a fresh server only, create them:

```sh
docker volume create prometheus_data
docker volume create grafana_data
```
