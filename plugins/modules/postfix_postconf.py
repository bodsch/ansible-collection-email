#!/usr/bin/python3

# (c) 2020, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)


import re

from ansible.module_utils.basic import AnsibleModule

# ----------------------------------------------------------------------

DOCUMENTATION = r"""
---
module: postfix_postconf
author: Bodo 'bodsch' Schulz <bodo@boone-schulz.de>
version_added: 1.0.0

short_description: Read a single postfix setting with postconf.
description:
    - Runs C(postconf <name>) and returns the value of that setting.
    - A setting postconf does not know is reported as a failure with a readable message.

options:
  config_name:
    description: Name of the postfix setting to read.
    required: true
    type: str
"""

EXAMPLES = r"""
- name: read the configured mydomain
  bodsch.email.postfix_postconf:
    config_name: mydomain
  register: postfix_mydomain

- ansible.builtin.debug:
    msg: "postfix serves {{ postfix_mydomain.postconf_value }}"
"""

RETURN = r"""
postconf_value:
    description: The value of the requested setting.
    returned: when the setting exists
    type: str
    sample: example.com
msg:
    description: Why the setting could not be read.
    returned: on failure
    type: str
"""

# ----------------------------------------------------------------------


class PostfixPostconf:
    """
    Main Class
    """

    module = None

    def __init__(self, module):
        """
        Initialize all needed Variables
        """
        self.module = module

        self._postconf = module.get_bin_path("postconf", True)
        self.config_name = module.params.get("config_name")

    def run(self):
        """
        runner
        """
        result = dict(
            rc=127,
            failed=True,
            changed=False,
        )

        args = []
        args.append(self._postconf)
        args.append(self.config_name)

        rc, out, err = self._exec(args)

        result["rc"] = rc

        pattern = re.compile(rf"{re.escape(self.config_name)} = (?P<value_string>.*)")
        match = re.search(pattern, out)

        if not match:
            # postconf prints nothing for a setting it does not know
            result["failed"] = True
            result["msg"] = (
                f"postconf returned no value for '{self.config_name}'. "
                "Is the setting name correct?"
            )
            return result

        result["failed"] = False
        result["postconf_value"] = match.group("value_string").strip()

        return result

    def _exec(self, cmd):
        """
        Run postconf and return (rc, stdout, stderr).

        check_rc is on, so a failing postconf aborts the task right here.
        """
        rc, out, err = self.module.run_command(cmd, check_rc=True)

        return rc, out, err


# ===========================================
# Module execution.
#


def main():
    """
    Read a single postfix setting with postconf and return its value.
    """
    module = AnsibleModule(
        argument_spec=dict(
            config_name=dict(
                required=True,
                type="str",
            )
        ),
        supports_check_mode=True,
    )

    postconf = PostfixPostconf(module)
    result = postconf.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == "__main__":
    main()
