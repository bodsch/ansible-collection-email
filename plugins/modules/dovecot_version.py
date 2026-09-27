#!/usr/bin/python3

# (c) 2020, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)


import re

from ansible.module_utils.basic import AnsibleModule

# ----------------------------------------------------------------------

DOCUMENTATION = r"""
---
module: dovecot_version
author: Bodo 'bodsch' Schulz <bodo@boone-schulz.de>
version_added: 1.2.0

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


class DovecotVersion:
    """
    Main Class
    """

    module = None

    def __init__(self, module):
        """
        Initialize all needed Variables
        """
        self.module = module

        self.dovecot_bin = module.get_bin_path("dovecot", True)
        # self.config_name = module.params.get("config_name")

    def run(self):
        """
        """
        dovecot_version = None
        result = dict(
            failed=True,
            changed=False,
            version = dovecot_version
        )

        args = []
        args.append(self.dovecot_bin)
        args.append("--version")

        rc, out, err = self._exec(args)

        pattern = re.compile(rf"(?P<version>.*)\s+\(.*\)")

        match = re.search(pattern, out)

        if match:
            # version = re.search(pattern_2, version.group('version'))
            dovecot_version = match.group("version")

        self.module.log(msg=f"value: {dovecot_version}")

        result["rc"] = rc

        if rc == 0:
            result["failed"] = False
            result["version"] = dovecot_version

        return result

    def _exec(self, cmd):
        """ """
        rc, out, err = self.module.run_command(cmd, check_rc=True)

        return rc, out, err


# ===========================================
# Module execution.
#


def main():

    args = dict()

    module = AnsibleModule(
        argument_spec=args,
        supports_check_mode=True,
    )

    _module = DovecotVersion(module)
    result = _module.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == "__main__":
    main()
