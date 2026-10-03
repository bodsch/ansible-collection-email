# 90-sieve.conf


```yaml
dovecot_sieve:
  plugins:
    - default:
        sieve: file:%h/sieve;active=%h/dovecot.sieve
        sieve_dir: /srv/mail/sieve/%d/%u
        sieve_global_dir: /srv/mail/sieve/global
        # sieve_default: /var/lib/dovecot/sieve/default.sieve
        # sieve_default_name: ""
        # sieve_global: ""
        # sieve_discard: ""
        # sieve_before: /var/lib/dovecot/sieve.d/
        # sieve_before2: ldap:/etc/sieve-ldap.conf;name=ldap-domain
        # sieve_before3: (etc...)
        # sieve_after: ""
        # sieve_after2: ""
        # sieve_after2: (etc...)
        sieve_extensions: "+notify +imapflags"
        # sieve_global_extensions: ""
        # sieve_plugins: ""
        # recipient_delimiter: +
        # sieve_max_script_size: 1M
        # sieve_max_actions: 32
        # sieve_max_redirects: 4
        # sieve_quota_max_scripts: 0
        # sieve_quota_max_storage: 0
        # sieve_user_email: ""
        # sieve_user_log: ""
        # sieve_redirect_envelope_from: sender
        # sieve_trace_dir: ""
        # #   "actions"        - Only print executed action commands, like keep,
        # #                      fileinto, reject and redirect.
        # #   "commands"       - Print any executed command, excluding test commands.
        # #   "tests"          - Print all executed commands and performed tests.
        # #   "matching"       - Print all executed commands, performed tests and the
        # #                      values matched in those tests.
        #sieve_trace_level: ""
        # sieve_trace_debug: false
        # sieve_trace_addresses: false
```


## dovecot 2.3

The settings are written into one `plugin { }` block as they are. As soon as a script
location is configured, `sieve` is added to `mail_plugins` of `protocol lmtp` and
`protocol lda` - into the block `dovecot_lmtp.protocols` / `dovecot_lda.protocols`
configures, because a second block would replace it. With `dovecot_sieve_extprograms`
configured, `sieve_extprograms` and the `+vnd.dovecot.*` extensions are added to
`sieve_plugins` and `sieve_global_extensions`.

## dovecot 2.4

The 2.3 variables above keep working. The role translates them:

| 2.3 | 2.4 |
| --- | --- |
| `sieve: file:%h/sieve;active=%h/.dovecot.sieve` | `sieve_script personal { driver = file  path = %{home}/sieve  active_path = %{home}/.dovecot.sieve }` |
| `sieve_dir` | `path` of the personal block, when `sieve` names only the active script |
| `sieve_before`, `sieve_before2`, `sieve_after`, `sieve_discard` | `sieve_script before { type = before }`, `before2`, ... |
| `sieve_default` + `sieve_default_name` | `sieve_script default { type = default  name = ... }` |
| `sieve_global`, `sieve_global_dir` | `sieve_script global_dir { type = global }` (`include :global`) |
| `sieve_extensions: "+a -b"` | `sieve_extensions { a = yes  b = no }` - a plain entry replaces the list: `sieve_extensions = a b` |

`notify`, `imapflags` and `vnd.dovecot.duplicate` no longer exist in 2.4. They are written
as a comment; their successors `enotify`, `imap4flags` and `duplicate` are enabled by default.

As soon as a script location exists, the sieve plugin is loaded for `protocol lmtp` and
`protocol lda` - without it no script runs, and dovecot does not report that.

A block can also be written the 2.4 way. A block with the same name wins over a
translated one:

```yaml
dovecot_sieve:
  scripts:
    personal:
      driver: file
      path: "~/sieve"
      active_path: "~/.dovecot.sieve"
```

Global scripts (`before`, `after`, `default`, `global`) are not compiled by the delivering
process unless it may write next to them. Precompile them with `sievec`, or the delivery
log reports `need to be pre-compiled using the sievec tool`.
