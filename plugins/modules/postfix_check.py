#!/usr/bin/python3
# -*- coding: utf-8 -*-

# (c) 2020, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r"""
---
module: postfix_check
author: Bodo 'bodsch' Schulz <bodo@boone-schulz.de>
version_added: 1.0.0

short_description: TBD
description:
    - TBD

options:
  verbose:
    description: TBD
    required: false
    type: str
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

# ----------------------------------------------------------------------


class PostfixCheck(object):
    """
      Main Class
    """
    module = None

    def __init__(self, module):
        """
          Initialize all needed Variables
        """
        self.module = module

        self._postfix = module.get_bin_path('postfix', True)
        self.verbose = module.params.get("verbose")

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
        args.append(self._postfix)

        if self.verbose:
            args.append("-v")
        # args.append("-D")
        args.append("-c")
        args.append("/etc/postfix")
        args.append("check")
        # args.append("2>&1")

        rc, out, err = self._exec(args)

        result['rc'] = rc

        if rc == 0:
            result['failed'] = False
            result['msg'] = out
        else:
            result['failed'] = True
            result['msg'] = err

        return result

    def _exec(self, cmd):
        """
        """
        self.module.log(f"cmd: '{cmd}'")

        rc, out, err = self.module.run_command(cmd, encoding=None, check_rc=False)

        self.module.log(f" - rc: '{rc}'")

        if rc != 0:
            self.module.log(f" - out: '{out}' ({type(out)}) - {len(out)}")
            self.module.log(f" - err: '{err}' ({type(err)}) - {len(err)}")

            if isinstance(out, list):
                _out = out.split("\n")
            else:
                _out = out
            if isinstance(err, list):
                _err = err.split("\n")
            else:
                _err = err

            self.module.log(f" - out: '{out}' ({type(out)}) - {len(out)}")
            self.module.log(f" - err: '{err}' ({type(err)}) - {len(err)}")
            self.module.log(f" - out: '{_out}'")
            self.module.log(f" - err: '{_err}'")

        return rc, out, err


# ===========================================
# Module execution.
#


def main():

    module = AnsibleModule(
        argument_spec=dict(
            verbose=dict(
                required=False,
            )
        ),
        supports_check_mode=True,
    )

    postfix = PostfixCheck(module)
    result = postfix.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
