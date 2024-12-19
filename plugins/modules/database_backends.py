# python 3 headers, required if submitting to Ansible
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.utils.display import Display

display = Display()


class FilterModule(object):
    """
    """

    def filters(self):
        """ """
        return {
            'database_schema': self.database_schema,
            'database_upgrade_directory': self.database_upgrade_directory,
        }

    def database_schema(self, data, database_type="postfixadmin"):
        """
        """
        display.v(f"database_schema({data}, {database_type})")

        result = []

        files = data.get("files")
        path = [x.get("path") for x in files]

        result = [x for x in path if database_type in x]

        return result

    def database_upgrade_directory(self, data, database_type="postfixadmin"):
        """
        """
        display.v(f"database_upgrade_directory({data}, {database_type})")

        result = []

        files = data.get("files")
        path = [x.get("path") for x in files]

        result = [x for x in path if database_type in x]

        if isinstance(result, list) and len(result) > 0:
            return result[0]

        return result
