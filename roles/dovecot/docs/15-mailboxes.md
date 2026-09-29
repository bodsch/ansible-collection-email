# 15-mailboxes.conf


```yaml
dovecot_defaults_mailboxes:
  ## Rendered into conf.d/15-mailboxes.conf as "namespace <name> { mailbox ... }".
  ##
  ## The namespace name MUST match the one in dovecot_mail.namespaces (default:
  ## inbox). A second namespace with inbox = yes makes dovecot refuse to start.
  ##
  ## "auto" decides whether dovecot creates the mailbox at all:
  ##   false     - never created automatically  (this is dovecot's default)
  ##   create    - created, but not subscribed
  ##   subscribe - created AND subscribed
  ## Without "auto" a mailbox block only carries metadata (special_use) for a
  ## folder the user has to create themselves - which is why the special use
  ## folders appear to be missing.
  namespaces:
    - inbox:
        inbox: true
        type: private
        list: true
        subscriptions: true
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
    ## Further mailbox attributes:
    #     disabled: false
    #     hidden: false
    #     ignore_on_failure: false
    #     location: ""
    #     order: 0
    #     prefix: ""
    #     separator: ""
    #     "Sent Messages":
    #       # legacy alias some clients still use
    #       special_use: \Sent
    ## Needs the "virtual" mail plugin, otherwise dovecot fails to open them:
    #     virtual/All:
    #       comment: "All my messages"
    #       special_use: \All
    #     virtual/Flagged:
    #       comment: "All my flagged messages"
    #       special_use: \Flagged
```
