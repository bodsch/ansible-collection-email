# 10-auth.conf

Two variables share this file, with two clearly separated jobs:

- `dovecot_auth.includes` decides **which** backends are active
- `dovecot_authentications` decides **how** each one is configured

A backend configured but not included never reaches dovecot. A backend included
but not configured renders a file without a single passdb — `10-auth.conf`
reports that as a comment, because dovecot itself does not complain about it.

```yaml
dovecot_auth:
  disable_plaintext_auth: true
  cache_size: 0
  cache_ttl: "1 hour"
  cache_negative_ttl: "1 hour"
  cache_verify_password_with_worker: false
  realms: []
  default_realm: ""
  username_chars: "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890.-_@"
  username_translation: ""
  username_format: "%Lu"
  master_user_separator: ""
  anonymous_username: anonymous
  worker_max_count: 80
  gssapi_hostname: ""
  krb5_keytab: ""
  use_winbind: false
  winbind_helper_path: ""
  failure_delay: 2 secs
  ssl_require_client_cert: false
  ssl_username_from_cert: false
  allow_weak_schemes: false        # dovecot >= 2.4
  verbose: false
  verbose_passwords: false
  mechanisms:
    - plain
    - login
    - cram-md5
  includes:
    - "# auth-deny.conf.ext"
    - "# auth-master.conf.ext"
    - auth-system.conf.ext
    - "# auth-sql.conf.ext"
    - "# auth-ldap.conf.ext"
    - "# auth-passwdfile.conf.ext"
    - "# auth-oauth2.conf.ext"
    - "# auth-static.conf.ext"
```

The settings carry **no** `auth_` prefix here — the template adds it. An entry
of `includes` prefixed with `#` is written as a comment, so the generated file
documents which backends exist but are inactive.

## dovecot_authentications

A mapping, keyed by the name of the file under `auth.d/`: `sql` is rendered into
`auth.d/auth-sql.conf.ext`.

```yaml
dovecot_authentications:
  system:
    passdb:
      driver: pam
      passdb_pam_service_name: dovecot   # 2.3: args: dovecot
    userdb:
      driver: passwd
```

The role ships the `system` backend, matching the `auth-system.conf.ext` that
`includes` has active by default. A fresh install therefore authenticates
against PAM without any configuration.

### replacing the default backend

Take the system file out of `includes` and put your own in. The unused default
stays behind harmlessly — it is rendered, but never included.

```yaml
dovecot_auth:
  includes:
    - auth-sql.conf.ext

dovecot_authentications:
  sql:
    passdb:
      driver: sql
      args: /etc/dovecot/dovecot-sql.conf.ext     # 2.3
    userdb:
      driver: sql
      args: /etc/dovecot/dovecot-sql.conf.ext
```

### order

Dovecot tries passdbs in the order they are included, so the **order of
`includes`** decides it — not the order of `dovecot_authentications`.

## 2.3 → 2.4

| 2.3 | 2.4 |
| --- | --- |
| `passdb { driver = x }` | `passdb x { }` — naming is mandatory |
| `args = ...` | per driver settings (`passdb_sql_query`, `passwd_file_path`, `passdb_pam_service_name`, …) |
| `default_fields` / `override_fields` | `fields { }` |
| `disable_plaintext_auth` | `auth_allow_cleartext`, inverted |
| `auth_username_format = %Lu` | `auth_username_format = %{user\|lower}` |

The `checkpassword`, `dict` and `vpopmail` backends were removed in 2.4;
`oauth2` was added. See `templates/etc/dovecot/<version>/auth.d/` for what
exists per version.
