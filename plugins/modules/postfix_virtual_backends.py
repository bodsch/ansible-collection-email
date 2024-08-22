#!/usr/bin/python3
# -*- coding: utf-8 -*-

# (c) 2023, Bodo Schulz <bodo@boone-schulz.de>

# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
import os
import hashlib
import json

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.bodsch.core.plugins.module_utils.checksum import Checksum
from ansible_collections.bodsch.core.plugins.module_utils.directory import create_directory
from ansible_collections.bodsch.core.plugins.module_utils.template.template import write_template
from ansible_collections.bodsch.core.plugins.module_utils.module_results import results

TPL_BACKEND = """# generated by ansible
user     = {{ item.username }}
password = {{ item.password }}
hosts    = {{ item.hosts }}
dbname   = {{ item.dbname }}

query    =
  {{ item.query | indent(2, first=False, blank=False) }}
"""


class PostfixVirtualBackends(object):
    """
    """

    def __init__(self, module):
        """
        """
        self.module = module

        self.dest = module.params.get("dest")
        self.backends = module.params.get("backends")
        self.cache_directory = "/var/cache/ansible/postfix"

    def run(self):
        """
        """
        _changed = False
        _failed = True
        _msg = "module init"

        self.checksum = Checksum(self.module)

        result_state = []

        create_directory(self.cache_directory)
        checksum_file = os.path.join(self.cache_directory, "backends")

        changed, checksum, old_checksum = self.checksum.validate(
            checksum_file=checksum_file,
            data=self.backends
        )

        # TODO
        # check written files!
        if not changed:
            """
            """
            return dict(
                changed=False,
                msg="The backend configuration has not been changed."
            )

        for backend_type, backend_def in self.backends.items():
            res = {}
            create_directory(os.path.join(self.dest, backend_type))

            for backend_data in backend_def:
                file_name = backend_data.get('name', None)

                if not file_name:
                    # password param should not be logged!
                    backend_data["password"] = "******"

                    # valid = False
                    msg = f"ERROR: missing 'name' for this broken backend definition: {backend_data}"

                    res["general"] = dict(
                        failed=True,
                        msg=msg
                    )

                else:
                    res[file_name] = dict()

                    valid, _msg = self._validate_backend(backend_data)

                    if valid:
                        _failed, _changed, _msg = self._write_template(os.path.join(self.dest, backend_type, file_name), backend_data)

                        res[file_name] = dict(
                            failed=_failed,
                            changed=_changed,
                            msg=_msg
                        )

                    else:
                        res[file_name] = dict(
                            failed=True,
                            msg=_msg
                        )

            result_state.append(res)

        _state, _changed, _failed, state, changed, failed = results(self.module, result_state)

        if not _failed:
            self.checksum.write_checksum(
                checksum_file=checksum_file,
                checksum=checksum
            )

        result = dict(
            changed=_changed,
            failed=_failed,
            result=result_state
        )

        return result

    def _validate_backend(self, backend_data):
        """
        """
        valid = False
        msg = "alles ist um seife"

        error_msg = []

        # self.module.log(f"    {backend}")
        file_name = backend_data.get('name', None)
        db_username = backend_data.get('username', None)
        db_password = backend_data.get('password', None)
        db_hosts = backend_data.get('hosts', None)
        db_name = backend_data.get('dbname', None)
        db_query = backend_data.get('query', None)

        if not file_name:
            error_msg.append("name")
            # password param schould not be logged!
            backend_data["password"] = "******"
            msg = f"ERROR: broken backend definition: {backend_data}"

        else:
            if not db_username:
                error_msg.append("username")
            if not db_password:
                error_msg.append("password")
            if not db_hosts:
                error_msg.append("hosts")
            if not db_name:
                error_msg.append("dbname")
            if not db_query:
                error_msg.append("query")

            if len(error_msg) > 0:
                msg = f"The variables for '{file_name}' have not been defined: "
                msg += ", ".join(error_msg)
            else:
                valid = True
                msg = None

        return (valid, msg)

    def _write_template(self, file_name, data):
        """
        """
        if isinstance(data, dict):
            """
                sort data
            """
            data = json.dumps(data, sort_keys=True)
            if isinstance(data, str):
                data = json.loads(data)

        checksum_file = os.path.join(self.cache_directory, f"{os.path.basename(file_name)}.checksum")

        changed, checksum, old_checksum = self.checksum.validate(
            checksum_file=checksum_file,
            data=data
        )

        if not changed:
            return False, False, "The configuration file has not been changed."

        write_template(file_name, TPL_BACKEND, data)

        self.checksum.write_checksum(
            checksum_file=checksum_file,
            checksum=checksum
        )

        return False, True, "The configuration file was written successfully."


# ===========================================
# Module execution.


def main():
    """
    """
    args = dict(
        backends=dict(
            required=True,
            type='dict'
        ),
        dest=dict(
            required=True,
            type='str'
        )
    )

    module = AnsibleModule(
        argument_spec=args,
        supports_check_mode=True,
    )

    p = PostfixVirtualBackends(module)
    result = p.run()

    module.log(msg=f"= result: {result}")
    module.exit_json(**result)


if __name__ == '__main__':
    main()
