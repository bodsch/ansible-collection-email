#!/usr/bin/python3

# (c) 2020, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)


from ansible.module_utils.basic import AnsibleModule

# ----------------------------------------------------------------------

DOCUMENTATION = r"""
---
module: postfix_newaliases
author: Bodo 'bodsch' Schulz <bodo@boone-schulz.de>
version_added: 1.0.0

short_description: Rebuild the postfix alias database.
description:
    - Runs C(newaliases) to rebuild the alias database from its source file.
    - Supports check mode - the command is reported but not executed.

options:
  alias_database:
    description:
      - A non default alias database, passed to newaliases as C(-oA).
      - Uses the postfix default when omitted.
    required: false
    type: str
"""

EXAMPLES = r"""
- name: rebuild the alias database
  bodsch.email.postfix_newaliases:

- name: rebuild a non default alias database
  bodsch.email.postfix_newaliases:
    alias_database: lmdb:/etc/postfix/aliases
"""

RETURN = r"""
rc:
    description: Exit code of newaliases.
    returned: always
    type: int
msg:
    description: Output of newaliases, or the command that would have run in check mode.
    returned: always
    type: str
"""

# ----------------------------------------------------------------------


class PostfixNewaliases:
    """
    Main Class
    """

    module = None

    def __init__(self, module):
        """
        Initialize all needed Variables
        """
        self.module = module

        self._newaliases = module.get_bin_path("newaliases", True)
        self.alias_database = module.params.get("alias_database")

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
        args.append(self._newaliases)

        if self.alias_database:
            args.append("-oA")
            args.append(self.alias_database)

        if self.module.check_mode:
            # rebuilding the alias database is a change; report it but do
            # not touch anything
            return dict(
                rc=0,
                failed=False,
                changed=True,
                msg=f"would run: {' '.join(args)}",
            )

        rc, out, err = self._exec(args)

        if rc == 0:
            result["failed"] = False
            result["changed"] = True
            result["msg"] = out
        else:
            result["failed"] = True
            result["changed"] = False
            result["msg"] = err

        return result

    def _exec(self, cmd):
        """
        Run newaliases and return (rc, stdout, stderr).
        """
        rc, out, err = self.module.run_command(cmd, check_rc=True)

        return rc, out, err


# ===========================================
# Module execution.
#


def main():
    """
    Rebuild the postfix alias database with newaliases.
    """
    module = AnsibleModule(
        argument_spec=dict(
            alias_database=dict(
                required=False,
                type="str",
            )
        ),
        supports_check_mode=True,
    )

    newaliases = PostfixNewaliases(module)
    result = newaliases.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == "__main__":
    main()
