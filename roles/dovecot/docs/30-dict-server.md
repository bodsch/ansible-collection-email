# 30-dict-server.conf

The global `dict { }` block of dovecot 2.3 became `dict_server { }` in 2.4, and
`dovecot-dict-sql.conf.ext` was folded into it.

```yaml
dovecot_dict_server:
  dicts:
    - quota:
        driver: sql
        sql_driver: mysql
        hostname: localhost
        maps:
          - priv/quota/storage:
              sql_table: quota
              username_field: username
              value_field bytes:
                type: uint
```

Each entry becomes a `dict <name> { }` block. The dict is reached over the
socket of `service dict`, which `dovecot_master.services` defines.
