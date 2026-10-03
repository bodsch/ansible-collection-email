# 10-metrics.conf

New in dovecot 2.4. Statistics come from events through `metric` blocks and need
no plugin — the old `auth_stats` setting and the `old-stats` plugin were removed.

```yaml
dovecot_metrics:
  metrics:
    - type: auth_success
      filter: "event=auth_request_finished AND success=yes"

    - type: imap_command
      filter: "event=imap_command_finished"
      fields: "bytes_in bytes_out lock_wait_usecs running_usecs"
      group_by: "cmd_name tagged_reply_state"

    - type: mail_delivery
      filter: "event=mail_delivery"
      group_by: "duration:exponential:1:5:10"

    - type: imap_commands_slow
      filter: "event=imap_command_finished AND duration > 1min"
      exporter: log-export
      exporter_include:
        - name
        - hostname
        - fields

  event_exporters:
    - log-export:
        driver: log
        format: json
        time_format: rfc3339

  prometheus:
    enabled: true
    port: 9900
    address: "127.0.0.1"
```

## metrics

One mapping per metric.

| key | |
| --- | --- |
| `type` | the metric name — mandatory |
| `filter` | the event filter — mandatory, dovecot refuses to start without it |
| `fields` | extra event fields, as a string or a list |
| `group_by` | see below |
| `exporter` | the name of an `event_exporters` entry |
| `exporter_include` | which parts of the event the exporter receives |
| `description` | |

## group_by

In dovecot 2.4 `group_by` is a **named list filter, not a setting**. Writing the
2.3 form yourself is rejected:

```
group_by = cmd_name tagged_reply_state
→ Fatal: group_by: Setting is a named list filter
```

The role keeps the compact notation from the dovecot documentation,
`field[:method[:arg...]]` separated by spaces, and expands it:

| notation | meaning |
| --- | --- |
| `cmd_name` | discrete — the default, no method block is written |
| `cmd_name:discrete:lowercase` | discrete with a modifier |
| `duration:exponential:1:5:10` | `min_magnitude` : `max_magnitude` : `base` |
| `duration:linear:0:100:10` | `min` : `max` : `step` |

`duration:exponential:1:8:10` therefore becomes:

```
group_by duration {
  method exponential {
    min_magnitude           = 1
    max_magnitude           = 8
    base                    = 10
  }
}
```

The expansion lives in the filter `bodsch.email.dovecot_metrics`. It refuses a
metric without a name or filter, an unknown setting, an unknown method, and an
`exponential` or `linear` that does not carry all three arguments — the latter
would silently fall back to dovecot's defaults and group nothing.

## event_exporters

An exporter **not** named after its driver needs an explicit `driver`;
`event_exporter_driver` defaults to `log`.

## prometheus

Adds an http listener to `service stats`, which serves `/metrics`.
