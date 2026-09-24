
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

## Development,  Branches (Git Tags)

The `master` Branch is my *Working Horse* includes the "latest, hot shit" and can be complete broken!

If you want to use something stable, please use a [Tagged Version](https://github.com/bodsch/ansible-rspamd/tags)!

---

## Author and License

- Bodo Schulz

## License

[Apache](LICENSE)

**FREE SOFTWARE, HELL YEAH!**
