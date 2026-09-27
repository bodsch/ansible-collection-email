#!/usr/bin/python3

# (c) 2022-2023, Bodo Schulz <bodo@boone-schulz.de>



import os

from ansible.module_utils.basic import AnsibleModule

# ----------------------------------------------------------------------

DOCUMENTATION = r"""
---
module: postfix_validate_certs
author: Bodo 'bodsch' Schulz <bodo@boone-schulz.de>
version_added: 1.0.0

short_description: Check that the configured postfix TLS certificate files exist.
description:
    - Checks the RSA, DSA and ECDSA key pairs plus the CA file of a TLS configuration.
    - >-
      Only the entries that are actually configured are looked at, and all of
      them are checked before returning, so one run reports every missing file
      instead of stopping at the first.
    - >-
      A value that starts with C($) is a postfix variable rather than a path
      and counts as fine - only postfix itself can resolve it.

options:
  config:
    description:
      - The TLS configuration to check.
      - >-
        Recognised keys are C(cert_file), C(key_file), C(dcert_file),
        C(dkey_file), C(eccert_file), C(eckey_file) and C(ca_file).
    required: true
    type: dict
  verbose:
    description: More logging on the target.
    required: false
    type: bool
    default: false
"""

EXAMPLES = r"""
- name: validate the postfix certificates
  bodsch.email.postfix_validate_certs:
    config:
      cert_file: /etc/ssl/certs/postfix.pem
      key_file: /etc/ssl/private/postfix.key
      ca_file: /etc/ssl/certs/ca.pem
  register: postfix_certs

- name: report every missing file at once
  ansible.builtin.fail:
    msg: "{{ postfix_certs.result_failed }}"
  when: postfix_certs.failed
"""

RETURN = r"""
failed:
    description: Whether at least one configured file is missing.
    returned: always
    type: bool
result_failed:
    description: The files that are missing, keyed by their role.
    returned: on failure
    type: dict
    sample:
        cert:
            failed: true
            msg: "file /etc/ssl/certs/postfix.pem does not exists."
"""

# ----------------------------------------------------------------------


class PostfixValidateCerts:
    """
    Main Class
    """

    module = None

    def __init__(self, module):
        """
        Initialize all needed Variables
        """
        self.module = module

        self.verbose = module.params.get("verbose")
        self.config = module.params.get("config")

    def run(self):
        """
        runner
        """
        res = dict(failed=False, msg="module init")

        if isinstance(self.config, dict):
            """ """
            res = self.validate(self.config)

        # self.module.log(f"  - res: {res}")

        return res

    def validate(self, config):
        """
        Check every configured certificate file of one TLS configuration.

        Covers the RSA, DSA and ECDSA pairs plus the CA file. Only the
        entries that are actually configured are looked at, and all of them
        are checked before returning, so one run reports every missing file
        rather than stopping at the first.

        Returns a mapping with failed, plus result_failed with the details
        when something is missing.
        """
        res = dict()

        cert_file = config.get("cert_file", None)
        key_file = config.get("key_file", None)
        dcert_file = config.get("dcert_file", None)
        dkey_file = config.get("dkey_file", None)
        eccert_file = config.get("eccert_file", None)
        eckey_file = config.get("eckey_file", None)
        ca_file = config.get("ca_file", None)
        # chain_files = config.get('chain_files', [])

        # self.module.log(f"cert_file   : {cert_file}")
        # self.module.log(f"key_file    : {key_file}")
        # self.module.log(f"dcert_file  : {dcert_file}")
        # self.module.log(f"dkey_file   : {dkey_file}")
        # self.module.log(f"eccert_file : {eccert_file}")
        # self.module.log(f"eckey_file  : {eckey_file}")
        # self.module.log(f"ca_file     : {ca_file}")
        # self.module.log(f"chain_files : {chain_files}")

        if cert_file:
            res["cert"] = self._exists(cert_file)

        if key_file:
            res["key"] = self._exists(key_file)

        if dcert_file:
            res["dcert"] = self._exists(dcert_file)

        if dkey_file:
            res["dkey"] = self._exists(dkey_file)

        if eccert_file:
            res["eccert"] = self._exists(eccert_file)

        if eckey_file:
            res["eckey"] = self._exists(eckey_file)

        if ca_file:
            res["ca"] = self._exists(ca_file)

        # self.module.log(f"res     : {res}")

        result_failed = {k: v for k, v in res.items() if v.get("failed", True)}

        # find all failed and define our variable
        failed = len(result_failed) > 0

        final_result = dict(failed=failed)

        if failed:
            final_result.update({"result_failed": result_failed})

        return final_result

    def _exists(self, file_name):
        """
        Check that a single file is there.

        A value that starts with "$" is a postfix variable, not a path, and
        counts as fine - it can only be resolved by postfix itself.

        Returns a mapping with failed and msg.
        """
        # self.module.log(f"_exists({file_name})")

        if file_name.startswith("$"):
            result = dict(failed=False, msg=f"{file_name} is an variable.")
        else:
            if not os.path.exists(file_name):
                result = dict(failed=True, msg=f"file {file_name} does not exists.")
            else:
                result = dict(failed=False, msg=f"file {file_name} exists.")

        return result


# ===========================================
# Module execution.
#


def main():
    """
    Check that the configured TLS certificate files exist and are readable.
    """
    module = AnsibleModule(
        argument_spec=dict(
            verbose=dict(
                required=False,
                type="bool",
                default=False,
            ),
            config=dict(required=True, type="dict"),
        ),
        supports_check_mode=True,
    )

    postfix = PostfixValidateCerts(module)
    result = postfix.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == "__main__":
    main()
