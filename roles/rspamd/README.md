
# Ansible Role:  `bodsch.email.rspamd`

Ansible role to setup rspamd.

[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/bodsch/ansible-rspamd/main.yml?logo=github&branch=main)][ci]
[![GitHub issues](https://img.shields.io/github/issues/bodsch/ansible-rspamd)][issues]
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/bodsch/ansible-rspamd)][releases]
[![Ansible Downloads](https://img.shields.io/ansible/role/d/bodsch/rspamd?logo=ansible)][galaxy]

[ci]: https://github.com/bodsch/ansible-rspamd/actions
[issues]: https://github.com/bodsch/ansible-rspamd/issues?q=is%3Aopen+is%3Aissue
[releases]: https://github.com/bodsch/ansible-rspamd/releases
[galaxy]: https://galaxy.ansible.com/ui/standalone/roles/bodsch/rspamd/


## Requirements & Dependencies

- nothing

### Supported (tested) Operating systems

Tested on

* Arch Linux
* Debian based
    - Debian 11 / 12
    - Ubuntu 22.04 / 24.04


## `rspamd_logging`

| Parameter             | Description |
| :----                 | :-----      |
| `type`                | Defines logging type (`file`, `console` or `syslog`). For some types mandatory attributes may be required. |
| `filename`            | Path to log file for file logging (required for **file** type) |
| `facility`            | Logging facility for **syslog** type (required if this type is used) |
| `level`               | Defines logging level (`error`, `warning`, `info` or `debug`). |
| `log_buffered`        | Flag that controls whether logging is buffered. |
| `log_buf_size`        | For file and console logging defines buffer size that will be used for logging output. |
| `log_urls`            | Flag that defines whether all URLs in message should be logged. Useful for testing. Default: `false`. |
| `log_re_cache`        | Output regular expressions statistics after each message. Default: `true`. |
| `debug_ip`            | List that contains IP addresses for which debugging should be turned on. |
| `color`               | Turn on coloring for log messages. Default: `false`. |
| `systemd`             | If true timestamps aren’t prepended to log messages. Default: `false`. |
| `debug_modules`       | A list of modules that are enabled for debugging. |
| `log_usec`            | Log microseconds (e.g. `11:43:16.68071`). Default: `false`. |
| `log_severity` (2.8+) | Log severity explicitly (e.g. `[info]` or `[error]`). Default: `false`. |

---

## Enabling DKIM signing

`rspamd` can sign outgoing mail itself via its [`dkim_signing`](https://docs.rspamd.com/modules/dkim_signing/)
module, using the same milter socket that already handles spam scanning - no second milter daemon required.
This role does **not** generate or manage DKIM private keys: they are expected to be provisioned onto disk by
an external key-management process, at the path referenced below. This role also does not create that key
directory itself - only `/etc/rspamd/local.d` and `/etc/rspamd/override.d` are managed - so make sure your
key-provisioning process creates it with the correct ownership.

Enable it through the generic `rspamd_local_config` map, which is rendered 1:1 into `/etc/rspamd/local.d/<key>.conf`:

```yaml
rspamd_local_config:
  dkim_signing:
    enabled: true
    # rspamd substitutes $selector and $domain per message; this is rspamd's own default path
    path: "/var/lib/rspamd/dkim/$domain.$selector.key"
    selector: "mail"
    sign_authenticated: true
    sign_local: true
    use_redis: false
```

The private key for each signing domain must exist at the resulting path (e.g.
`/var/lib/rspamd/dkim/example.com.mail.key`) and be readable by the OS user rspamd runs as (typically `_rspamd`
on Debian/Ubuntu, `rspamd` on Arch Linux).

To route outgoing mail through rspamd's milter, point [`bodsch.email.postfix`](../postfix/README.md) at the
`rspamd_proxy` worker's socket (`localhost:11332` by default - see `rspamd_workers` in `defaults/main.yml`):

```yaml
postfix_smtpd:
  milters:
    - "inet:localhost:11332"
```

---

## Custom maps

Modules such as `multimap` or `rbl` often reference plain-text map files (lists of domains, IP networks,
or other values) rather than inline configuration - this is how mailcow ships its `custom/*.map` files for
blacklists, whitelists, and trusted-network lists.

`rspamd_custom_maps` renders exactly that: each key becomes a filename under `/etc/rspamd/custom/`, and each
value is a list of lines written verbatim, one per line, to `/etc/rspamd/custom/<key>.map`:

```yaml
rspamd_custom_maps:
  mailcow_networks:
    - "10.0.0.0/8"
    - "192.168.0.0/16"
  whitelisted_domains:
    - "example.com"
    - "example.org"
```

A module config referencing such a map (via `rspamd_local_config` or `rspamd_config_overrides`, see below)
would then point at `/etc/rspamd/custom/mailcow_networks.map` accordingly. Maps removed from
`rspamd_custom_maps` are cleaned up from `/etc/rspamd/custom/` on the next run.

## `rspamd_local_config` / `rspamd_config_overrides`

Both are generic dicts, keyed by rspamd module name, rendered 1:1 into UCL config. `rspamd_local_config`
writes to `/etc/rspamd/local.d/<key>.conf` (merged with the module's built-in defaults, priority 1);
`rspamd_config_overrides` writes to `/etc/rspamd/override.d/<key>.conf` (takes precedence over everything
else, priority 10) - this mirrors rspamd's own [local.d vs. override.d](https://docs.rspamd.com/tutorials/quickstart/#configuration)
convention. Keys removed from either variable are cleaned up from disk on the next run.

```yaml
rspamd_local_config:
  actions:
    reject: 15
    add_header: 6
  multimap:
    mailcow_networks:
      type: ip
      map: "/etc/rspamd/custom/mailcow_networks.map"
      description: "trusted mailcow networks"
```

---

## Development,  Branches (Git Tags)

The `master` Branch is my *Working Horse* includes the "latest, hot shit" and can be complete broken!

If you want to use something stable, please use a [Tagged Version](https://github.com/bodsch/ansible-rspamd/tags)!

---

## Author and License

- Bodo Schulz

## License

[Apache](LICENSE)

**FREE SOFTWARE, HELL YEAH!**
