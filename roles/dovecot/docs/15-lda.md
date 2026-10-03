# 15-lda.conf


```yaml
dovecot_lda:
  # postmaster_address: ""
  # hostname: ""
  # quota_full_tempfail: false
  # sendmail_path: /usr/sbin/sendmail
  # submission_host: ""
  # rejection_subject: Rejected: %s
  # rejection_reason: "Your message to <%t> was automatically rejected:%n%r"
  # recipient_delimiter: "+"
  # original_recipient_header: ""
  # mailbox_autocreate: false
  # mailbox_autosubscribe: false
  protocols:
    - lda:
        mail_plugins:
          - "$mail_plugins"
```

