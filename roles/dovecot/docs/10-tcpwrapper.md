# 10-tcpwrapper.conf


```yaml
dovecot_tcpwrapper:
  login_access_sockets: tcpwrap
  services:
    - login/tcpwrap:
        listeners:
          - login/tcpwrap:
              type: "unix"
              mode: "0666"
              user: ""
              group: ""
```
