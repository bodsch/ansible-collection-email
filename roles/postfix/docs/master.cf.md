
### master.cf

To manage the `master.cf` via the role, this feature must be explicitly **enabled**:

```yaml
postfix_handle_mastercf: true
```

[upstream doku](http://www.postfix.org/master.5.html)

|           | type             |                |                                    |
| :----     | :----            | :----          | :----                              |
| `service` | *string* / *int* | `smtp` / `589` | service name oder port             |
| `comment` | *string*         | `-`            | comment                            |
| `enable`  | *bool*           | `true`         | enable or disable service          |
| `type`    | *string*         | `inet`         | service type                       |
| `private` | *bool*           | `false`        |                                    |
| `unpriv`  | *bool*           | `false`        |                                    |
| `chroot`  | *bool*           | `false`        |                                    |
| `wakeup`  | *int*            | `60`           |                                    |
| `maxproc` | *int*            | `100`          |                                    |
| `command` | *string*         | `postscreen`   | postfix command                    |
| `args`    | *list*           | `[]`           | liste von argumenten für `command` |

```yaml
postfix_master:
  #
  - name: submission
    type: inet
    private: false
    chroot: false
    command: smtpd
    options:
      syslog_name: postfix/submission
      smtpd_tls_security_level: encrypt
      smtpd_sasl_auth_enable: true
      smtpd_tls_auth_only: true
      smtpd_relay_restrictions:
        - permit_sasl_authenticated
        - reject
  #      
  - name: smtps
    type: inet
    private: false
    chroot: false
    command: postscreen
  #
  - name: smtp
    type: inet
    state: disabled
```
