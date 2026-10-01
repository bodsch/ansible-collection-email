# 10-master.conf

[upstream doku](https://doc.dovecot.org/configuration_manual/service_configuration/?highlight=service)

## Dovecot Service configuration

All services are defined as a list.
Below this, each service can be configured individually.

Services that are to provide a listener must define this via a `listeners` list.
This allows a number of listeners to be configured for a service.

For each listener, the type can be defined individually.
The following types can be used:

- unix
- inet


For example, the `imap-login` service.  

```yaml
dovecot_master:
  services:
    - imap-login:
        service_count: 1
        process_min_avail: 0
        listeners:
          - imap:
              type: "inet"
              port: 143
          - imaps:
              type: inet
              port: 993
              ssl: true
```

creates the following configuration entry:

```bash
    service imap-login {
      inet_listener imap {
        port: 143
      }
      inet_listener imaps {
        port: 993
        ssl: true
      }
      service_count: 1
      process_min_avail: 0
    }
```



```yaml
dovecot_master:
  default_process_limit: 100
  default_client_limit: 1000
  default_vsz_limit: 256M
  default_login_user: dovenull
  default_internal_user: dovecot

  services:
    # service log {
    #   chroot =
    #   client_limit = 0
    #   drop_priv_before_exec = no
    #   executable = log
    #   extra_groups =
    #   group =
    #   idle_kill = 4294967295 secs
    #   privileged_group =
    #   process_limit = 1
    #   process_min_avail = 0
    #   protocol =
    #   service_count = 0
    #   type = log
    #   unix_listener log-errors {
    #     group =
    #     mode = 0600
    #     user =
    #   }
    #   user =
    #   vsz_limit = 18446744073709551615 B
    # }
    - log:
        chroot: ""
        client_limit: 0
        drop_priv_before_exec: false
        executable: log
        extra_groups:
        user:
        group:
        idle_kill: "4294967295 secs"
        privileged_group:
        process_limit: 1
        process_min_avail: 0
        protocol:
        service_count: 0
        type: log
        vsz_limit:
        listeners:
          - log-errors:
              type: unix
              group:
              user:
              mode: "0600"

    # service imap-login {
    #   inet_listener imap {
    #     #port: 143
    #   }
    #   inet_listener imaps {...
    #     #port: 993
    #     #ssl: true
    #   }
    #   #service_count: 1
    #   #process_min_avail: 0
    #   #vsz_limit: $default_vsz_limit
    # }
    - imap-login:
        service_count: 1
        process_min_avail: 0
        # vsz_limit: "$default_vsz_limit"
        listeners:
          - imap:
              type: "inet"
              port: 143
          - imaps:
              type: inet
              port: 993
              ssl: true
    # service pop3-login {
    #   inet_listener pop3 {
    #     #port: 110
    #   }
    #   inet_listener pop3s {
    #     #port: 995
    #     #ssl: true
    #   }
    # }
    - pop3-login:
        listeners:
          - pop3:
              port: 110
          - pop3s:
              port: 995
              ssl: true

    # service submission-login {
    #   inet_listener submission {
    #     #port: 587
    #   }
    # }
    - submission-login:
        listeners:
          - submission:
              port: 587

    # service lmtp {
    #   unix_listener lmtp {
    #     #mode: 0666
    #   }
    #   #inet_listener lmtp {
    #     #address: ""
    #     #port: ""
    #   #}
    # }
    - lmtp:
        listeners:
          - lmtp:
              type: inet
              address: 127.0.0.1
              port: 999
              haproxy: false
              reuse_port: false
              ssl: false
          - lmtp:
              type: unix
              mode: "0666"

    # service imap {
    #   #vsz_limit: $default_vsz_limit
    #   #process_limit: 1024
    # }
    - imap:
        process_limit: 1024

    # service pop3 {
    #   #process_limit: 1024
    # }
    - pop3:
        process_limit: 1024

    # service submission {
    #   #process_limit: 1024
    # }
    - submission:
        process_limit: 1024

    # service auth {
    #   #
    #   #
    #   unix_listener auth-userdb {
    #     #mode: 0666
    #     #user: ""
    #     #group: ""
    #   }
    #   #unix_listener /var/spool/postfix/private/auth {
    #   #}
    #   #user: $default_internal_user
    # }
    - auth:
        user: $default_internal_user
        listeners:
          - auth-userdb:
              type: unix
              mode: "0666"
              user: ""
              group: ""
          - auth:
              type: unix
              path: /var/spool/postfix/private/auth

    # service auth-worker {
    #   #user: root
    # }
    - auth-worker:
        user: root

    # service dict {
    #   unix_listener dict {
    #     #mode: 0600
    #     #user: ""
    #     #group: ""
    #   }
    # }
    - dict:
        listeners:
          - dict:
              type: unix
              mode: "0600"
              user: ""
              group: ""
```

## the SASL socket for postfix

Postfix authenticates against a dovecot socket inside its own chroot. The role
writes it as its **own** `service auth { }` block, which dovecot merges with the
one from `dovecot_master.services` — so replacing that list cannot lose the
socket again.

```yaml
dovecot_postfix_sasl:
  enabled: true
  path: /var/spool/postfix/private/auth
  user: postfix
  group: postfix
  mode: "0660"
```

The matching postfix side:

```yaml
postfix_smtpd:
  sasl:
    auth_enable: true
    type: dovecot
    path: private/auth      # relative - smtpd runs chrooted in /var/spool/postfix
```

It is **off by default**: `/var/spool/postfix/private` only exists once postfix
is installed, and dovecot refuses to start when it cannot create the socket.
Run the postfix role before the dovecot role.

Note that a listener's `type` is `unix` or `inet`; the template appends the
`_listener` suffix itself.
