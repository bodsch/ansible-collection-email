#!/usr/bin/python3
# -*- coding: utf-8 -*-

# (c) 2020, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function

import re

from ansible.module_utils.basic import AnsibleModule


# ----------------------------------------------------------------------

DOCUMENTATION = r"""
---
module: postfix_postconf
author: Bodo 'bodsch' Schulz <bodo@boone-schulz.de>
version_added: 1.0.0

short_description: TBD
description:
    - TBD

options:
  config_name:
    description: TBD
    required: true
    type: str
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

# ----------------------------------------------------------------------


class PostfixPostconf(object):
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

        pattern_1 = re.compile(rf"{self.config_name} = (?P<value_string>.*)")

        version = re.search(pattern_1, out)

        if version:
            # version = re.search(pattern_2, version.group('version'))
            value_string = version.group("value_string")

        # self.module.log(msg=f"value: {value_string}")

        result["rc"] = rc

        if rc == 0:
            result["failed"] = False
            result["postconf_value"] = value_string

        return result

    def _exec(self, cmd):
        """ """
        rc, out, err = self.module.run_command(cmd, check_rc=True)

        return rc, out, err


# ===========================================
# Module execution.
#


def main():

    module = AnsibleModule(
        argument_spec=dict(
            config_name=dict(
                required=True,
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
