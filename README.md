# My ansible scripts for managing remote servers

## Dependencies

[pass](https://www.passwordstore.org/)

## Usage

- Clone the repo
- Create `~/.ssh/config` file as in [example](/ssh_config_example)
- Add your passwords to pass storage in format `servers/[host]/[username]`
  > `Host` and `username` must match the ones from `~/.ssh/config`
- Now use [playbooks](/playbooks) like:
    ```shell
    ansible-playbook playbooks/upgrade_hosts.yml
    ```
