# 10-mail.conf

Where the mail lives, and how its folders are named. Two variables share the
job, and mixing them up is the most common way to end up without folders:

| variable | decides | file |
| --- | --- | --- |
| `dovecot_mail` | **where** mail is stored and how the namespaces are named | `conf.d/10-mail.conf` |
| `dovecot_mailboxes` | **which** folders exist and which are created automatically | `conf.d/15-mailboxes.conf`, see [15-mailboxes.md](15-mailboxes.md) |

---

## 1. Where the mail is stored

Three settings, and only the first is mandatory:

| setting | |
| --- | --- |
| `mail_driver` | `maildir`, `sdbox`, `mdbox`, `mbox`, … |
| `mail_path` | the mail directory. `~/` is the user's home |
| `mail_home` | the home, when the userdb does not return one |

**Dovecot 2.4 removed mail location autodetection.** Where 2.3 fell back to
`~/Maildir`, 2.4 resolves `mail_driver` and `mail_path` to an empty string. The
configuration still passes `doveconf -n` — the server simply has no INBOX, and
every client reports it as unavailable. The role therefore ships a 2.4 default
that reproduces what 2.3 autodetected:

```
mail_driver = maildir
mail_path   = ~/Maildir
```

The 2.3 spelling keeps working and **takes precedence** over that default:

```yaml
dovecot_mail:
  mail_location: "maildir:~/:INDEX=/var/mail/INDEX/%d/%n:CONTROL=/var/mail/CONTROL/%d/%n:LAYOUT=maildir++"
```

The role splits it into the separate 2.4 settings. The options map like this:

| 2.3 option | 2.4 setting |
| --- | --- |
| `INDEX=` | `mail_index_path` |
| `INDEXPVT=` | `mail_index_private_path` |
| `CONTROL=` | `mail_control_path` |
| `VOLATILEDIR=` | `mail_volatile_path` |
| `ALT=` | `mail_alt_path` |
| `INBOX=` | `mail_inbox_path` |
| `LAYOUT=` | `mailbox_list_layout` |

Variables are translated too: `%h` → `%{home}`, `%u` → `%{user}`,
`%n` → `%{user|username}`, `%d` → `%{user|domain}`. A doubled `%%d` is the owner
of a shared mailbox and becomes `%{owner_user|domain}`.

### directories on disk

Dovecot creates the **per user** part of a path itself, but not the static
parent above it. With

```
mail_control_path = /var/mail/CONTROL/%{user|domain}/%{user|username}
```

and `/var/mail` owned by root, the first subscription fails with

```
mkdir(/var/mail/CONTROL/example.com) failed: Permission denied
cmd mailbox subscribe: ... Internal error occurred.
```

`dovecot_manage_mail_directories` (on by default) creates `/var/mail/CONTROL`
and `/var/mail/INDEX` and hands them to `dovecot_virtual_user`. Top level
directories such as `/` or `/var` are never created or chowned.

---

## 2. How a folder name is built

A folder's IMAP name is the namespace **prefix**, then the mailbox name, with
the namespace **separator** between its levels:

```
namespace inbox {
  prefix    = INBOX.
  separator = .
}
mailbox Sent { }      →  INBOX.Sent
```

Without a prefix and with `separator = /` the same mailbox is just `Sent`, and a
nested one is `Sent/2024`.

On disk it depends on `mailbox_list_layout`:

| layout | `INBOX.Sent` becomes |
| --- | --- |
| `maildir++` | `<mail_path>/.Sent/` |
| `fs` | `<mail_path>/Sent/` |

For `mail_driver = maildir` the layout defaults to `maildir++`, for everything
else to `fs`. Note that `doveconf -h mailbox_list_layout` prints `fs` — that is
the raw default before the driver is taken into account.

**Changing prefix, separator or layout on a running server renames nothing.**
Existing folders keep lying where they are and become invisible under the new
scheme.

---

## 3. Creating and subscribing to folders

A `mailbox` block alone creates nothing — it only carries metadata. The `auto`
setting decides:

| `auto` | |
| --- | --- |
| *unset* / `no` | never created. The block only declares `special_use` for a folder the user creates themselves |
| `create` | created, but not subscribed — the client does not show it until the user subscribes |
| `subscribe` | created **and** subscribed |

```yaml
dovecot_mailboxes:
  namespaces:
    - inbox:                   # must match a name in dovecot_mail.namespaces
        Sent:
          auto: subscribe
          special_use: \Sent
```

Subscriptions are stored in a `subscriptions` file in the control directory —
`mail_control_path` when set, otherwise the mail directory. That file has to be
writable by the mail user, which is what the `mkdir` error above is about.

---

## 4. Examples

### A — system users, mail in the home directory

The role's default. Nothing to configure; `auth-system.conf.ext` authenticates
against PAM and the home comes from `/etc/passwd`.

```yaml
dovecot_mail:
  mail_driver: maildir
  mail_path: "~/Maildir"
  namespaces:
    - name: inbox
      inbox: true
```

Folders are `Sent`, `Trash`, … and live in `~/Maildir/.Sent/`.

### B — virtual users, indexes on separate storage

One mail user for everything, home per domain and account, indexes and control
files away from the mail itself — for instance to keep them off a network file
system.

```yaml
dovecot_mail:
  mail_uid: 1101
  mail_gid: 1101
  first_valid_uid: 1101
  last_valid_uid: 1101
  mail_home: /var/vmail/%d/%n

  namespaces:
    - name: inbox
      type: private
      inbox: true
      list: true
      subscriptions: true
      separator: "."
      prefix: INBOX.
      location: "maildir:~/:INDEX=/var/mail/INDEX/%d/%n:CONTROL=/var/mail/CONTROL/%d/%n:LAYOUT=maildir++"

dovecot_mailboxes:
  namespaces:
    - inbox:
        inbox: true
        type: private
        Drafts:
          auto: subscribe
          special_use: \Drafts
        Junk:
          auto: subscribe
          special_use: \Junk
        Sent:
          auto: subscribe
          special_use: \Sent
        Trash:
          auto: subscribe
          special_use: \Trash
        Archive:
          auto: subscribe
          special_use: \Archive
```

The user `admin@example.com` then gets:

```
/var/vmail/example.com/admin/        cur new tmp .Drafts .Junk .Sent .Trash .Archive
/var/mail/INDEX/example.com/admin/
/var/mail/CONTROL/example.com/admin/ subscriptions
```

and in the client `INBOX`, `INBOX.Drafts`, `INBOX.Sent`, …

`dovecot_manage_mail_directories` creates `/var/vmail`, `/var/mail/INDEX` and
`/var/mail/CONTROL` as `vmail:vmail`.

### C — a public namespace next to it

Shared folders every user sees, in addition to their own.

```yaml
dovecot_mail:
  namespaces:
    - name: inbox
      type: private
      inbox: true
      separator: "."
      prefix: INBOX.
      location: "maildir:~/"

    - name: public
      type: public
      separator: "."
      prefix: "shared."
      location: "maildir:/srv/mail/PUBLIC:INDEX=/srv/mail/PUBLIC/indexes:CONTROL=/srv/mail/PUBLIC/control"
      list: children
      subscriptions: true
```

A namespace needs a `name` — an unnamed one renders as `namespace  { }`, which
2.3 still accepts and 2.4 refuses with `namespace { } is missing section name`.
Exactly **one** namespace carries `inbox: true`.

`list: children` hides the namespace root itself and shows only what is below
it.

---

## 5. When folders do not appear

Check with `doveadm` first — it goes straight to the storage, without IMAP and
without the client:

```bash
doveadm mailbox list -u user@example.com      # which folders exist
doveadm mailbox list -s -u user@example.com   # which are subscribed
doveadm user user@example.com                 # what the userdb returns
```

| symptom | likely cause | where |
| --- | --- | --- |
| client says the INBOX is unavailable, `doveconf -h mail_driver` is empty | no mail storage configured, 2.4 does not guess | section 1 |
| `doveadm mailbox list` shows only `INBOX` | the folders have no `auto` | section 3 |
| `doveadm mailbox list` shows only `INBOX`, debug log says `acl: owner = no` | `acl_user` still uses the 2.3 `%u` | [90-acl.md](90-acl.md) |
| subscribing fails, log says `mkdir(...) failed: Permission denied` | the static parent of the control path is missing or not owned by the mail user | section 1 |
| the subscribe dialog is empty | there is nothing besides the INBOX to subscribe to | section 3 |
| folders exist on disk but the client does not see them | prefix, separator or layout changed after the fact | section 2 |
| dovecot refuses to start, `namespace { } is missing section name` | a namespace without `name` | section 4 C |

The role catches three of these before anything is written, as long as
`dovecot_validate_drivers` is on: no mail storage on 2.4, not exactly one
namespace with `inbox: true`, and a namespace name in `dovecot_mailboxes` that
`dovecot_mail` does not define — the latter would open a second namespace and
create the special use folders somewhere the client never looks.

---

## 6. Reference

```yaml
dovecot_mail:
  # the 2.4 spelling
  # mail_driver: maildir
  # mail_path: "~/Maildir"
  # mail_home: ""
  # mail_index_path: ""
  # mail_control_path: ""
  # mailbox_list_layout: ""
  #
  # the 2.3 spelling, translated by the role - takes precedence
  # mail_location: "mbox:~/mail:INBOX=/var/mail/%u"
  namespaces:
    - name: inbox
      # type: private
      # separator: ""
      # prefix: ""
      # location: ""
      inbox: true
      # hidden: false
      # list: true
      # subscriptions: true
      # ignore_on_failure: false
      # order: 0
      # alias_for: ""
      # disabled: false
      #
      # The MAILBOXES of a namespace are not configured here, they live in
      # dovecot_mailboxes - see docs/15-mailboxes.md

  #   - name: ""
  #     #type: shared
  #     #separator: /
  #     #prefix: shared/%%u/
  #     #location: maildir:%%h/Maildir:INDEX=~/Maildir/shared/%%u
  #     #subscriptions: false
  #     #list: children
  #     #order: 0
  # mail_shared_explicit_inbox: false
  # mail_uid: ""
  # mail_gid: ""
  # mail_privileged_group: mail
  # mail_access_groups: ""
  # mail_full_filesystem_access: false
  # mail_attribute_dict: ""
  # mail_server_comment: ""
  # mail_server_admin: ""
  # mmap_disable: false
  # dotlock_use_excl: true
  # mail_fsync: optimized
  # lock_method: fcntl
  # mail_temp_dir: /tmp

  # <doc/wiki/UserIds.txt>
  # first_valid_uid: 1101
  # last_valid_uid: 1101
  # first_valid_gid: 1101
  # last_valid_gid: 1101
  # mail_max_keyword_length: 50
    # <doc/wiki/Chrooting.txt>
  valid_chroot_dirs: []
  # mail_chroot: ""
  # auth_socket_path: /var/run/dovecot/auth-userdb
  # mail_plugin_dir: /usr/lib/dovecot/modules
  # mail_plugins: []
  # mailbox_list_index: true
  # mailbox_list_index_very_dirty_syncs: true
  # mailbox_list_index_include_inbox: false
  # mail_cache_min_mail_count: 0
  # mailbox_idle_check_interval: 30 secs
  # mail_save_crlf: false
  # mail_prefetch_count: 0
  # mail_temp_scan_interval: 1w
  # mail_sort_max_read_count: 0
    # protocol !indexer-worker {
    #   #mail_vsize_bg_after_count: 0
    # }
  mail_protocols:
    - name: "!indexer-worker"
      # mail_vsize_bg_after_count: 0
  # maildir_stat_dirs: false
  # maildir_copy_with_hardlinks: true
  # maildir_very_dirty_syncs: false
  # maildir_broken_filename_sizes: false
  # maildir_empty_new: false
  # mbox_read_locks:
  #   - fcntl
  # mbox_write_locks:
  #   - fcntl
  #   - dotlock
  # mbox_lock_timeout: 5 mins
  # mbox_dotlock_change_timeout: 2 mins
  # mbox_dirty_syncs: true
  # mbox_very_dirty_syncs: false
  # mbox_lazy_writes: true
  # mbox_min_index_size: 0
  # mbox_md5: apop3d
  # mdbox_rotate_size: 10M
  # mdbox_rotate_interval: 0
  # mdbox_preallocate_space: false
  # mail_attachment_dir: ""
  # mail_attachment_min_size: 128k
  mail_attachment_fs: "sis posix"
  # mail_attachment_hash: "%{sha256:80}"
  # mail_attachment_detection_options: ""
```
