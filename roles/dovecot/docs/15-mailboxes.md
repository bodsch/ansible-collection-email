# 15-mailboxes.conf

Which folders a user has, and which of them dovecot creates by itself. The
companion of [10-mail.conf](10-mail.md), which decides *where* the mail lives.

```yaml
dovecot_mailboxes:
  namespaces:
    - inbox:
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

renders

```
namespace inbox {
  mailbox "Drafts" {
    auto = subscribe
    special_use = \Drafts
  }
  ...
}
```

This is what the role ships by default, so a fresh installation already has the
five special use folders.

---

## 1. The namespace name has to match

The key under `namespaces` is the **name of a namespace from
`dovecot_mail.namespaces`** — dovecot merges blocks of the same name.

```yaml
dovecot_mail:
  namespaces:
    - name: inbox          # <- this name
      inbox: true

dovecot_mailboxes:
  namespaces:
    - inbox:               # <- has to be this one
        Sent:
          auto: subscribe
```

A name that does not exist opens a **second** namespace. The folders are then
created there, and the client never looks at it. With
`dovecot_validate_drivers` on, the role refuses such a configuration before
anything is written.

## 2. Namespace attributes and mailboxes share one mapping

Inside a namespace both kinds of entry live side by side. The role tells them
apart by their value: **a mapping is a mailbox, anything else is a namespace
attribute.**

```yaml
    - inbox:
        inbox: true           # scalar -> namespace attribute
        type: private         # scalar -> namespace attribute
        Sent:                 # mapping -> mailbox
          auto: subscribe
```

Recognised namespace attributes are `alias_for`, `disabled`, `hidden`,
`ignore_on_failure`, `inbox`, `list`, `mail_driver`, `mail_path`,
`mail_index_path`, `order`, `prefix`, `separator`, `subscriptions` and `type`.
A mailbox whose name collides with one of those cannot be expressed here — give
it its settings in `dovecot_mail.namespaces` instead, or rename the folder.

Everything a namespace needs can also stay in `dovecot_mail`; repeating it here
is optional.

## 3. auto — the setting that actually creates the folder

A `mailbox` block on its own creates **nothing**. It declares metadata for a
folder; `auto` decides whether the folder comes into existence.

| `auto` | |
| --- | --- |
| *unset* / `no` | never created. Only the metadata, for a folder the user creates |
| `create` | created, but not subscribed — most clients do not show it |
| `subscribe` | created **and** subscribed |

This is the single most common reason for "the standard folders are missing":
the mailbox blocks are all there, and not one of them carries `auto`.

Dovecot creates such a folder when the mailbox list is first opened, not when
the configuration is written. `doveadm mailbox list -u <user>` triggers it.

## 4. Settings of a mailbox block

| setting | |
| --- | --- |
| `auto` | see above |
| `special_use` | the RFC 6154 label — `\All`, `\Archive`, `\Drafts`, `\Flagged`, `\Junk`, `\Sent`, `\Trash` |
| `comment` | shown by clients that support it |
| `autoexpunge` | delete mails older than this, e.g. `30d` |
| `autoexpunge_max_mails` | keep at most this many mails |
| `notify_status` | dovecot >= 2.4 |
| `driver` | a storage driver of its own; written as `mail_driver` for 2.4 |

`special_use` is what makes a client put its own Sent or Trash **into this
folder** instead of creating a second one. A label outside the RFC is accepted
with a warning:

```
Warning: mailbox X: special_use label \Totalnonsense is not an RFC-defined label - allowing anyway
```

Two mailboxes may carry the same label — dovecot neither warns nor refuses, it
simply uses the first. That is how a legacy alias is expressed:

```yaml
        Sent:
          auto: subscribe
          special_use: \Sent
        "Sent Messages":          # some older clients look for this name
          special_use: \Sent      # no auto - do not create a second Sent
```

## 5. Hierarchy

A mailbox name is written with the **separator of its namespace**, not with a
fixed character:

```yaml
dovecot_mail:
  namespaces:
    - name: inbox
      separator: "/"
      inbox: true

dovecot_mailboxes:
  namespaces:
    - inbox:
        Archive:
          auto: subscribe
          special_use: \Archive
        Archive/2024:
          auto: create
```

With `separator: "."` the same folder is `Archive.2024`. On disk, a maildir++
layout turns it into `.Archive.2024/` — see
[10-mail.conf, section 2](10-mail.md).

---

## 6. Examples

### A — the default, plus automatic cleanup

Trash is emptied after 30 days, Junk after 14. Both only for mails the user
left there; nothing else is touched.

```yaml
dovecot_mailboxes:
  namespaces:
    - inbox:
        Drafts:
          auto: subscribe
          special_use: \Drafts
        Junk:
          auto: subscribe
          autoexpunge: 14d
          special_use: \Junk
        Sent:
          auto: subscribe
          special_use: \Sent
        Trash:
          auto: subscribe
          autoexpunge: 30d
          special_use: \Trash
        Archive:
          auto: subscribe
          special_use: \Archive
```

### B — folders that exist but are not forced on anybody

`auto: create` gives every user the folder without subscribing it; the metadata
of `Archive` applies the moment a user creates it themselves.

```yaml
dovecot_mailboxes:
  namespaces:
    - inbox:
        Sent:
          auto: subscribe
          special_use: \Sent
        Trash:
          auto: subscribe
          special_use: \Trash
        Templates:
          auto: create
          comment: "Message templates"
        Archive:
          special_use: \Archive     # no auto - created on demand
```

### C — virtual folders

`virtual/All` and `virtual/Flagged` need the `virtual` mail plugin. Without it
dovecot fails to open them, so they must **not** carry `auto` unless the plugin
is loaded:

```yaml
dovecot_mail:
  mail_plugins:
    - virtual

dovecot_mailboxes:
  namespaces:
    - inbox:
        virtual/All:
          comment: "All my messages"
          special_use: \All
        virtual/Flagged:
          comment: "All my flagged messages"
          special_use: \Flagged
```

The folders themselves are defined by `dovecot-virtual` files below the virtual
namespace's path — the role does not write those.

---

## 7. When a folder does not appear

```bash
doveadm mailbox list -u user@example.com      # which folders exist
doveadm mailbox list -s -u user@example.com   # which are subscribed
```

| symptom | cause |
| --- | --- |
| only `INBOX` is listed | no mailbox carries `auto` — section 3 |
| the folder exists but no client shows it | `auto: create` without `subscribe` |
| the client creates its own second Sent folder | `special_use` missing or on the wrong mailbox |
| the folders landed in a namespace nobody sees | the namespace name does not match `dovecot_mail` — section 1 |
| only `INBOX`, and the debug log says `acl: owner = no` | not a mailbox problem — see [90-acl.md](90-acl.md) |
| subscribing fails with `mkdir(...) Permission denied` | not a mailbox problem — see [10-mail.md](10-mail.md) |

A folder that already exists on disk is **not** changed by `auto`. Adding
`special_use` later does apply to it; changing the name does not rename
anything.
