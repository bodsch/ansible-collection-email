# dovecot-dict-auth.conf

https://doc.dovecot.org/configuration_manual/authentication/dict/?highlight=default_pass_scheme

This file is commonly accessed via `passdb {}` or `userdb {}` section in
`auth.d/auth-dict.conf.ext`

```yaml
dovecot_dict_auth:
  # uri: ""
  default_pass_scheme: MD5
  iterate_prefix: userdb/
  # iterate_disable: false
  dict_keys:
    - passwd:
        key: passdb/%u
        format: json
    - userdb:
        key: userdb/%u
        format: json
    - quota:
        key: userdb/%u/quota
        default_value: 100M

  passdb_objects:
    - passdb
  passdb_fields: {}
  userdb_objects:
    - userdb
  userdb_fields:
    quota_rule: "*:storage=%{dict:quota}"
    mail: "maildir:%{dict:userdb.home}/Maildir"
```
