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
