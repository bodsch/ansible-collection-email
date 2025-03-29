# python 3 headers, required if submitting to Ansible
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import netaddr

from ansible.utils.display import Display


display = Display()


class FilterModule(object):
    """
    """

    def filters(self):
        return {
            'mailcow_ports': self.mailcow_ports,
            'mailcow_compose_active': self.mailcow_compose_active,
        }

    def mailcow_ports(self, data):
        """
        """
        # display.v(f"mailcow_ports({data})")
        result = ""

        if isinstance(data, dict):
            bind = data.get('address', None)
            port = data.get('port', "")

            if bind:
                _ipaddress = netaddr.IPAddress(bind, flags=netaddr.INET_PTON | netaddr.ZEROFILL)
                if _ipaddress is not None:
                    result = f"{bind}:{port}"
                else:
                    result = f"127.0.0.1:{port}"
            else:
                result = port

        return result

    def mailcow_compose_active(self, data, git_version=None):
        """
        """
        # display.v(f"mailcow_compose_active(data, {git_version})")
        result = [f"{x.get("name")}.conf" for x in data if x.get("state", "present") == "present"]

        if git_version:
            # https://github.com/mailcow/mailcow-dockerized/releases/tag/2025-01a
            # https://mailcow.email/posts/2025/release-2025-01/
            # With 2025-01 SOLR is saying arrivederci to mailcow.
            # It will be replaced with Flatcurve instead, which is not using a seperate container like SOLR and is directly integrated into the Dovecot Core.
            compare = self.version_compare(git_version, '2025-01', '>=')
            if compare:
                import re
                result = [x for x in result if not re.search(r".*solr.*", x)]

        return result

    def version_compare(self, value, version, compare_operator='eq'):
        ''' Perform a version comparison on a value '''
        import operator
        from packaging.version import Version
        # from ansible import errors
        from ansible.module_utils.common.text.converters import to_native, to_text

        op_map = {
            '==': 'eq', '=': 'eq', 'eq': 'eq',
            '<': 'lt', 'lt': 'lt',
            '<=': 'le', 'le': 'le',
            '>': 'gt', 'gt': 'gt',
            '>=': 'ge', 'ge': 'ge',
            '!=': 'ne', '<>': 'ne', 'ne': 'ne'
        }

        if not value:
            raise ("Input version value cannot be empty")

        if not version:
            raise ("Version parameter to compare against cannot be empty")

        if compare_operator in op_map:
            compare_operator = op_map[compare_operator]
        else:
            valid_compare = ", ".join(map(repr, op_map))

            raise (
                f'Invalid operator type ({compare_operator}). Must be one of {valid_compare}')

        try:
            method = getattr(operator, compare_operator)
            return method(Version(to_text(value)), Version(to_text(version)))

        except Exception as e:
            raise (f'Version comparison failed: {to_native(e)}')
