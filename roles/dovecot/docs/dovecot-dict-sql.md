# dovecot-dict-sql.conf

```yaml
dovecot_dict_sql:
  connects:
    host: localhost
    dbname: mails
    user: testuser
    password: pass
  maps:
    - pattern: priv/quota/storage
      table: quota
      username_field: username
      value_field: bytes
    - pattern: priv/quota/messages
      table: quota
      username_field: username
      value_field: messages
    - pattern: "shared/expire/$user/$mailbox"
      table: expires
      value_field: expire_stamp
      fields:
        username: $user
        mailbox: $mailbox
```


