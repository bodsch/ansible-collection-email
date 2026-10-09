#!/usr/bin/python3

# (c) 2026, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import annotations

import re
from typing import Any

from ansible.module_utils.basic import AnsibleModule

# ----------------------------------------------------------------------

DOCUMENTATION = r"""
---
module: postfix_master
author: Bodo 'bodsch' Schulz <bodo@boone-schulz.de>
version_added: 2.1.0

short_description: Manage single services in the postfix master.cf.
description:
    - Adds, changes, removes or comments out entries of C(master.cf) with C(postconf -M).
    - >-
      The master.cf shipped by the distribution stays the base; only the
      declared services are touched, everything else is left as it is.
    - >-
      A service is identified by C(name) and C(type), so C(smtp/inet) and
      C(smtp/unix) are two independent entries.
    - >-
      A declared service is written as a whole. Options (C(-o)) and arguments
      that are not declared are removed from that entry.
    - >-
      Option values may contain whitespace; they are written in the
      C({ name = value }) form, which needs postfix 3.0 or newer.
    - >-
      C(postconf -M) does not see commented out entries. Enabling a service
      that only exists as a comment adds a new line and leaves the comment.
options:
  services:
    description: The master.cf services to manage.
    required: true
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - The service name, for C(inet) services also C(host:port) like C(127.0.0.1:submission).
        required: true
        type: str
      type:
        description: The transport type of the service.
        required: true
        type: str
        choices: [inet, unix, unix-dgram, fifo, pass]
      state:
        description:
          - C(present) creates or updates the entry.
          - C(absent) removes the entry (C(postconf -MX)).
          - C(disabled) comments the entry out (C(postconf -#M)).
        type: str
        default: present
        choices: [present, absent, disabled]
      private:
        description: The C(private) column. A bool is written as C(y)/C(n), unset as C(-).
        type: raw
      unpriv:
        description: The C(unpriv) column. A bool is written as C(y)/C(n), unset as C(-).
        type: raw
      chroot:
        description: The C(chroot) column. A bool is written as C(y)/C(n), unset as C(-).
        type: raw
      wakeup:
        description: The C(wakeup) column, for example C(60) or C(1000?). Unset is C(-).
        type: raw
      maxproc:
        description: The C(maxproc) column. Unset is C(-).
        type: raw
      command:
        description: The daemon program. Required for O(services[].state=present).
        type: str
      options:
        description:
          - Parameter overrides, written as C(-o name=value).
          - A bool becomes C(yes)/C(no), a list is joined with C(,).
        type: dict
        default: {}
      args:
        description:
          - Further command arguments, written after the options.
          - Either a string or a list of strings, for example C(flags=DRhu user=vmail argv=/usr/bin/foo).
        type: raw
  config_directory:
    description: The postfix configuration directory (C(postconf -c)).
    required: false
    type: path
"""

EXAMPLES = r"""
- name: configure postfix master.cf services
  bodsch.email.postfix_master:
    services:
      - name: submission
        type: inet
        private: false
        chroot: false
        command: smtpd
        options:
          syslog_name: postfix/submission
          smtpd_tls_security_level: encrypt
          smtpd_sasl_auth_enable: true
          smtpd_relay_restrictions:
            - permit_sasl_authenticated
            - reject
      - name: dovecot
        type: unix
        unpriv: false
        chroot: false
        command: pipe
        args: "flags=DRhu user=vmail:vmail argv=/usr/lib/dovecot/deliver -f ${sender} -d ${recipient}"
      - name: smtps
        type: inet
        state: absent
      - name: smtp
        type: inet
        state: disabled
  notify:
    - restart postfix
"""

RETURN = r"""
changed:
    description: Whether at least one service was changed.
    returned: always
    type: bool
result:
    description: Per service state, keyed by C(name/type).
    returned: always
    type: list
    elements: dict
    sample:
      - submission/inet:
          changed: true
          state: present
          before: "submission inet n - n - - smtpd"
          after: "submission inet n - n - - smtpd -o syslog_name=postfix/submission"
"""

# ----------------------------------------------------------------------

FIELDS = ("private", "unpriv", "chroot", "wakeup", "maxproc")


def tokenize(line: str) -> list[str]:
    """
    Split a master.cf line at whitespace, keeping C({ ... }) groups as one token.
    """
    tokens: list[str] = []
    current = ""
    depth = 0

    for char in line:
        if char == "{":
            depth += 1
        elif char == "}" and depth > 0:
            depth -= 1

        if char.isspace() and depth == 0:
            if current:
                tokens.append(current)
                current = ""
            continue

        current += char

    if current:
        tokens.append(current)

    return tokens


def split_option(token: str) -> tuple[str, str]:
    """
    Turn C(name=value) or C({ name = value }) into a (name, value) tuple.
    """
    token = token.strip()
    if token.startswith("{") and token.endswith("}"):
        token = token[1:-1]

    name, _, value = token.partition("=")
    return name.strip(), value.strip()


def field_value(value: Any) -> str:
    """
    Render a master.cf column: bools as y/n, unset as '-'.
    """
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return "-"
    if isinstance(value, bool):
        return "y" if value else "n"

    value = str(value).strip()
    return {"yes": "y", "no": "n", "true": "y", "false": "n"}.get(value.lower(), value)


def option_value(value: Any) -> str:
    """
    Render a -o value: bools as yes/no, lists joined with ','.
    """
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (list, tuple)):
        return ",".join(str(v).strip() for v in value)

    return str(value).strip()


def parse_entry(line: str) -> dict[str, Any] | None:
    """
    Parse one line of C(postconf -M) output into its parts.
    """
    tokens = tokenize(line)
    if len(tokens) < 8:
        return None

    options: dict[str, str] = {}
    args: list[str] = []

    rest = tokens[8:]
    idx = 0
    while idx < len(rest):
        token = rest[idx]
        if token == "-o" and idx + 1 < len(rest):
            name, value = split_option(rest[idx + 1])
            options[name] = value
            idx += 2
            continue
        if token.startswith("-o") and len(token) > 2:
            name, value = split_option(token[2:])
            options[name] = value
        else:
            args.append(token)
        idx += 1

    return dict(
        name=tokens[0],
        type=tokens[1],
        fields=tuple(field_value(t) for t in tokens[2:7]),
        command=tokens[7],
        options=options,
        args=args,
    )


def desired_entry(service: dict[str, Any]) -> dict[str, Any]:
    """
    Normalise a declared service into the same shape parse_entry() returns.
    """
    args = service.get("args")
    if isinstance(args, (list, tuple)):
        args = " ".join(str(a) for a in args)

    return dict(
        name=service["name"],
        type=service["type"],
        fields=tuple(field_value(service.get(f)) for f in FIELDS),
        command=str(service["command"]).strip(),
        options={
            str(k).strip(): option_value(v)
            for k, v in (service.get("options") or {}).items()
        },
        args=tokenize(str(args)) if args else [],
    )


def render_entry(entry: dict[str, Any]) -> str:
    """
    Build the master.cf line for postconf -M from a normalised entry.
    """
    parts = [entry["name"], entry["type"], *entry["fields"], entry["command"]]

    for name, value in entry["options"].items():
        if re.search(r"\s", value):
            parts += ["-o", f"{{ {name} = {value} }}"]
        else:
            parts += ["-o", f"{name}={value}"]

    parts += entry["args"]

    return " ".join(parts)


def same_entry(current: dict[str, Any], desired: dict[str, Any]) -> bool:
    """
    Compare two entries, ignoring the order of the -o options.
    """
    return (
        current["fields"] == desired["fields"]
        and current["command"] == desired["command"]
        and current["options"] == desired["options"]
        and current["args"] == desired["args"]
    )


class PostfixMaster:
    """
    Manage master.cf entries with postconf -M.
    """

    module = None

    def __init__(self, module: Any) -> None:
        """
        Initialize all needed Variables
        """
        self.module = module

        self._postconf = module.get_bin_path("postconf", True)
        self.services = module.params.get("services") or []
        self.config_directory = module.params.get("config_directory")

    def run(self) -> dict[str, Any]:
        """
        runner
        """
        error = self._validate()
        if error:
            return dict(failed=True, changed=False, msg=error)

        result_state: list[dict[str, Any]] = []
        changed = False
        diff_before: list[str] = []
        diff_after: list[str] = []

        for service in self.services:
            key = f"{service['name']}/{service['type']}"
            state = service.get("state") or "present"

            current_line = self._current(key)
            current = parse_entry(current_line) if current_line else None

            res: dict[str, Any] = dict(changed=False, state=state, before=current_line)

            if state == "present":
                desired = desired_entry(service)
                after = render_entry(desired)
                res["after"] = after

                if current is None or not same_entry(current, desired):
                    res["changed"] = True
                    self._postconf_cmd(["-M", f"{key}={after}"])
            elif current is not None:
                # absent and disabled both drop the active line
                res["changed"] = True
                res["after"] = None if state == "absent" else f"#{current_line}"
                self._postconf_cmd(["-MX" if state == "absent" else "-#M", key])

            if res["changed"]:
                changed = True
                diff_before.append(current_line or "")
                diff_after.append(res.get("after") or "")

            result_state.append({key: res})

        result: dict[str, Any] = dict(
            changed=changed, failed=False, result=result_state
        )

        if changed and getattr(self.module, "_diff", False):
            result["diff"] = dict(
                before="\n".join(diff_before) + "\n",
                after="\n".join(diff_after) + "\n",
                before_header="master.cf",
                after_header="master.cf",
            )

        return result

    def _validate(self) -> str | None:
        """
        Reject duplicate services and present services without a command.
        """
        seen: set[str] = set()
        problems: list[str] = []

        for service in self.services:
            key = f"{service.get('name')}/{service.get('type')}"
            if key in seen:
                problems.append(f"'{key}' is declared more than once")
            seen.add(key)

            if (service.get("state") or "present") == "present" and not service.get(
                "command"
            ):
                problems.append(f"'{key}' needs a command")

        return "; ".join(problems) if problems else None

    def _current(self, key: str) -> str | None:
        """
        Return the active master.cf line of a service, or None.
        """
        _rc, out, _err = self._exec(self._base_cmd() + ["-M", key])
        for line in out.splitlines():
            tokens = tokenize(line)
            if len(tokens) >= 2 and f"{tokens[0]}/{tokens[1]}" == key:
                return " ".join(tokens)

        return None

    def _postconf_cmd(self, args: list[str]) -> None:
        """
        Run a changing postconf call, unless in check mode.
        """
        if self.module.check_mode:
            return

        self._exec(self._base_cmd() + args)

    def _base_cmd(self) -> list[str]:
        cmd = [self._postconf]
        if self.config_directory:
            cmd += ["-c", self.config_directory]
        return cmd

    def _exec(self, cmd: list[str]) -> tuple[int, str, str]:
        """
        Run postconf and fail on errors; 'unmatched request' warnings are fine.
        """
        rc, out, err = self.module.run_command(cmd, check_rc=False)

        if rc != 0 or "fatal:" in err:
            self.module.fail_json(
                msg=f"'{' '.join(cmd)}' failed: {err.strip() or out.strip()}",
                rc=rc,
            )

        return rc, out, err


# ===========================================
# Module execution.
#


def main() -> None:
    """Run the module."""
    specs = dict(
        services=dict(
            required=True,
            type="list",
            elements="dict",
            options=dict(
                name=dict(required=True, type="str"),
                type=dict(
                    required=True,
                    type="str",
                    choices=["inet", "unix", "unix-dgram", "fifo", "pass"],
                ),
                state=dict(
                    type="str",
                    default="present",
                    choices=["present", "absent", "disabled"],
                ),
                private=dict(type="raw"),
                unpriv=dict(type="raw"),
                chroot=dict(type="raw"),
                wakeup=dict(type="raw"),
                maxproc=dict(type="raw"),
                command=dict(type="str"),
                options=dict(type="dict", default={}),
                args=dict(type="raw"),
            ),
        ),
        config_directory=dict(required=False, type="path"),
    )

    module = AnsibleModule(
        argument_spec=specs,
        supports_check_mode=True,
    )

    p = PostfixMaster(module)
    result = p.run()

    module.log(msg=f"= result: {result}")
    module.exit_json(**result)


# import module snippets
if __name__ == "__main__":
    main()
