# python 3 headers, required if submitting to Ansible
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import netaddr
from ansible.plugins.test.core import version_compare
from ansible.utils.display import Display

display = Display()


class FilterModule(object):
    """ """

    def filters(self):
        return {
            "mailcow_ports": self.mailcow_ports,
            "mailcow_compose_active": self.mailcow_compose_active,
            "mailcow_compare_version": self.mailcow_compare_version,
        }

    def mailcow_ports(self, data):
        """ """
        # display.v(f"bodsch.email::mailcow_ports({data})")
        result = ""

        if isinstance(data, dict):
            bind = data.get("address", None)
            port = data.get("port", "")

            if bind:
                _ipaddress = netaddr.IPAddress(
                    bind, flags=netaddr.INET_PTON | netaddr.ZEROFILL
                )
                if _ipaddress is not None:
                    result = f"{bind}:{port}"
                else:
                    result = f"127.0.0.1:{port}"
            else:
                result = port

        return result

    def mailcow_compose_active(self, data, git_version=None):
        """ """
        display.v(f"bodsch.email::mailcow_compose_active(data, {git_version})")
        result = [
            f"{x.get('name')}.conf"
            for x in data
            if x.get("state", "present") == "present"
        ]

        display.v(f" - {result}")

        if git_version:
            # https://github.com/mailcow/mailcow-dockerized/releases/tag/2025-01a
            # https://mailcow.email/posts/2025/release-2025-01/
            # With 2025-01 SOLR is saying arrivederci to mailcow.
            # It will be replaced with Flatcurve instead, which is not using a seperate container like SOLR and is directly integrated into the Dovecot Core.
            compare = version_compare(str(git_version), "2025-01", ">=")
            if compare:
                import re

                result = [x for x in result if not re.search(r".*solr.*", x)]

        return result

    def mailcow_compare_version(self, data, installed={}):
        """ """
        display.v(f"bodsch.email::mailcow_compare_version({data}, {installed})")

        # not mailcow_repository_information.git.commit_short_id | default('left') ==
        #    mailcow_installed_information.git.commit_short_id | default('right')
        repository_information = data.get("git", {}).get("commit_short_id", "left")
        installed_information = installed.get("git", {}).get("commit_short_id", "right")

        display.v(f"  - {repository_information}")
        display.v(f"  - {installed_information}")

        result = not (repository_information == installed_information)

        display.v(f"= {result}")

        return result
