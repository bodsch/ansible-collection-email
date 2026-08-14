# python 3 headers, required if submitting to Ansible

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.utils.display import Display

display = Display()


class FilterModule(object):
    """
    ansible filter
    """

    def filters(self):
        return {
            "config_value": self.config_value,
            "database_connection": self.database_connection,
        }

    def config_value(self, data, default=None):
        """ """
        # display.v(f"bodsch.email::config_value({data}, {default})")

        result = None

        if type(data) is None:
            result = False
        elif type(data) is bool:
            result = "yes" if data else "no"
        else:
            result = data

        # display.v(f"return : {result}")
        return result

    def database_connection(self, data):
        """ """
        # display.v(f"bodsch.email::database_connection({data})")

        result = ""

        if isinstance(data, dict):
            _dba_hostname = data.get("host", None)
            _dba_port = data.get("port", None)
            _dba_schemaname = data.get("dbname", None)
            _dba_username = data.get("user", None)
            _dba_password = data.get("password", None)
            _dba_connect = []

            if _dba_hostname:
                _dba_connect.append(f"host={_dba_hostname}")
            if _dba_port:
                _dba_connect.append(f"port={_dba_port}")
            if _dba_schemaname:
                _dba_connect.append(f"dbname={_dba_schemaname}")
            if _dba_username:
                _dba_connect.append(f"user={_dba_username}")
            if _dba_password:
                _dba_connect.append(f"password={_dba_password}")

            result = " ".join(_dba_connect)

        # display.v(f"return : {result}")
        return result
