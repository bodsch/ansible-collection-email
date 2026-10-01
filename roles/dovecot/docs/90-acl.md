# 90-acl.conf

```yaml
dovecot_acl:
  plugins:
    - acl: vfile:/etc/dovecot/global-acls:cache_secs=300
    - acl_shared_dict: file:/var/lib/dovecot/shared-mailboxes
    - acl_user: "%u"
```

## 2.3 → 2.4

The `plugin { }` block is gone; the acl settings are global. The role keeps the
2.3 spelling above and translates it.

**`acl` is split.** 2.3 packed driver, global ACL file and cache time into one
value; 2.4 takes a plain driver name. Handing it the whole string makes dovecot
2.4.1 abort with `Unknown ACL backend`, while 2.4.4 silently keeps only the part
before the first colon and drops the cache time:

```
acl = vfile:/etc/dovecot/global-acls:cache_secs=300
→
acl_driver                    = vfile
acl_cache_ttl                 = 300 secs
```

The global ACL **file** has no 2.4 equivalent — global rights are configured
inside a `mailbox <name> { acl <id> { } }` block. The generated file says so as
a comment.

**Variables are translated.** Dovecot 2.4 does not expand the 2.3 `%u`, so
`acl_user = %u` stays the literal string `%u`, never matches the mailbox owner,
and every mailbox but the INBOX disappears from `LIST`. The debug log shows:

```
acl: acl username = %u
acl: owner = no
```

The role rewrites `%u` to `%{user}`, `%d` to `%{user|domain}` and so on, in
`acl_user` and in the path of `acl_shared_dict`. A doubled `%%u` — the owner of
a shared mailbox — is left alone.

**`acl_anyone`** became the boolean `imap_acl_allow_anyone`; `allow` and
`authenticated` both map to `yes`, a difference 2.4 no longer expresses.

**`acl_shared_dict`** became a named filter:

```
acl_sharing_map {
  dict file {
    path                      = /var/lib/dovecot/shared-mailboxes
  }
}
```
