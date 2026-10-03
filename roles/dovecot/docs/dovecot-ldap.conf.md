# dovecot-ldap.conf.ext 

```yaml
dovecot_ldap: {}
  # hosts: []
  # uris: []
  # dn: ""
  # dnpass: ""
  # sasl_bind: false
  # sasl_mech: ""
  # sasl_realm: ""
  # sasl_authz_id: ""
  # tls: false
  # tls_ca_cert_file: ""
  # tls_ca_cert_dir: ""
  # tls_cipher_suite: ""
  # tls_cert_file: ""
  # tls_key_file: ""
  # # Valid values: never, hard, demand, allow, try
  # tls_require_cert: ""
  # ldaprc_path: ""
  # debug_level: 0
  # auth_bind: false
  # auth_bind_userdn: ""
  # ldap_version: 3
  # base: ""
  # # Dereference: never, searching, finding, always
  # deref: never
  # # Search scope: base, onelevel, subtree
  # scope: subtree
  #
  # # User attributes are given in LDAP-name=dovecot-internal-name list. The
  # # internal names are:
  # #   uid - System UID
  # #   gid - System GID
  # #   home - Home directory
  # #   mail - Mail location
  # #
  # # There are also other special fields which can be returned, see
  # # http://wiki2.dovecot.org/UserDatabase/ExtraFields
  # user_attrs:
  #   - homeDirectory=home
  #   - uidNumber=uid
  #   - gidNumber=gid
  #
  # http://wiki2.dovecot.org/Variables for full list):
  # #   %u - username
  # #   %n - user part in user@domain, same as %u if there's no domain
  # #   %d - domain part in user@domain, empty if user there's no domain
  # user_filter: (&(objectClass=posixAccount)(uid=%u))
  # pass_attrs:
  #   - uid=user
  #   - userPassword=password
  # pass_attrs:
  #   - uid=user
  #   - userPassword=password
  #   - homeDirectory=userdb_home
  #   - uidNumber=userdb_uid
  #   - gidNumber=userdb_gid
  # pass_filter: (&(objectClass=posixAccount)(uid=%u))
  # iterate_attrs: uid=user
  # iterate_filter: (objectClass=posixAccount)
  # # List of supported schemes is in: http://wiki2.dovecot.org/Authentication
  # default_pass_scheme: CRYPT
  # blocking: false
```
