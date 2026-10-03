# 20-managesieve.conf


```yaml
dovecot_managesieve:
  enabled_protocols:
    - "$protocols"
    - sieve
  services:
    - managesieve-login:
        # chroot: login
        # client_limit: 0
        # drop_priv_before_exec: no
        # executable: managesieve-login
        # extra_groups: ""
        # group: ""
        # idle_kill: 0
        listeners:
          - sieve:
              type: inet
              port: 4190
              address: ""
              haproxy: false
              reuse_port: false
              ssl: false
          - sieve_deprecated:
              type: inet
              port: 2000
    - managesieve:
        process_limit: 1024
```

