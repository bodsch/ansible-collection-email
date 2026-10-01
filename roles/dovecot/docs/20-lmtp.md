# 20-lmtp.conf

```yaml
dovecot_lmtp:
  # proxy: false
  # save_to_detail_mailbox: false
  # rcpt_check_quota: false

  # The default is "final", which is the same as the one given to the
  # RCPT TO command.
  # "original" uses the address given in RCPT TO's ORCPT parameter,
  # "none" uses nothing. Note that "none" is currently always used
  # when a mail has multiple recipients.
  # hdr_delivery_address: final

  # rendered as "protocol lmtp { }" - only needed to ADD something for LMTP
  protocols:
    - lmtp:
        mail_plugins:
          - quota
```

Every value above is dovecot's own default, so an empty `dovecot_lmtp: {}`
produces the same running configuration.

## mail_plugins in 2.4

The `$mail_plugins` placeholder no longer exists — dovecot 2.4 removed setting
variable expansion. It is also not needed: in 2.4 `mail_plugins` is a boolean
list, and the block form **adds** to the global list instead of replacing it.
A `protocol lmtp { mail_plugins { } }` is therefore only written when LMTP needs
something *on top* of what `dovecot_mail.mail_plugins` already loads.

Note that `mail_plugins` has to be a **list**. Given a string, jinja iterates
over its characters and the generated config contains one entry per letter.

## 2.3 → 2.4

`lmtp_verbose_replies` was removed. `lmtp_user_concurrency_limit` changed its
default from `0` (unlimited) to `10`.
