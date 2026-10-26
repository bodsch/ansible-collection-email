#!/usr/bin/python3

# (c) 2020, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)


from ansible.module_utils.basic import AnsibleModule

# ----------------------------------------------------------------------

DOCUMENTATION = r"""
---
module: postfix_check
author: Bodo 'bodsch' Schulz <bodo@boone-schulz.de>
version_added: 1.0.0

short_description: Check whether postfix considers its configuration usable.
description:
    - Runs C(postfix check) against /etc/postfix.
    - >-
      A non zero exit is reported through the result rather than aborting the
      task, so a playbook can decide what to do with a broken configuration.

options:
  verbose:
    description: Add C(-v) to the postfix command line.
    required: false
    type: bool
    default: false
"""

EXAMPLES = r"""
- name: check the postfix configuration
  bodsch.email.postfix_check:
  register: postfix_check_result

- name: fail on a broken configuration
  ansible.builtin.fail:
    msg: "{{ postfix_check_result.msg }}"
  when: postfix_check_result.failed
"""

RETURN = r"""
rc:
    description: Exit code of C(postfix check).
    returned: always
    type: int
msg:
    description: Output of postfix - stdout on success, stderr on failure.
    returned: always
    type: str
"""

# ----------------------------------------------------------------------


class MailmonkeyBootstrap:
    """
    Main Class
    """

    module = None

    def __init__(self, module):
        """
        Initialize all needed Variables
        """
        self.module = module

        self.bin_mailmonkey = module.get_bin_path("mailmonkey", True)
        self.config = module.params.get("config")

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
        args.append(self.bin_mailmonkey)

        if self.config:
            args.append("-config")
            args.append(self.config)

        args.append("bootstrap")
        # args.append("2>&1")

        rc, out, err = self._exec(args)

        result["rc"] = rc

        if rc == 0:
            result["failed"] = False
            result["msg"] = "The bootstrap process was successful."
        else:
            result["failed"] = True
            result["msg"] = err

        return result

    def _exec(self, cmd):
        """
        Run "postfix check" and return (rc, stdout, stderr).

        check_rc is off on purpose: a non zero exit is the expected outcome
        for a broken configuration and is reported through the result, not
        as a module crash.
        """
        self.module.log(f"cmd: '{cmd}'")

        rc, out, err = self.module.run_command(cmd, check_rc=False)

        self.module.log(f" - rc: '{rc}'")

        if rc != 0:
            self.module.log(f" - out: '{out}'")
            self.module.log(f" - err: '{err}'")

        return rc, out, err


# ===========================================
# Module execution.
#


def main():
    """
    Run "postfix check" and report whether postfix considers its
    configuration usable.
    """
    spec = dict(
        config=dict(
            required=False, type="str", default="/etc/mailmonkey/mailmonkey.yaml"
        )
    )

    module = AnsibleModule(
        argument_spec=spec,
        supports_check_mode=True,
    )

    postfix = MailmonkeyBootstrap(module)
    result = postfix.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == "__main__":
    main()
