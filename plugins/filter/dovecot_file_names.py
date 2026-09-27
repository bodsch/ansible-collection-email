# python 3 headers, required if submitting to Ansible

import os

from ansible.utils.display import Display

display = Display()


class FilterModule:
    """
    ansible filter
    """

    def filters(self):
        return {
            "file_names": self.file_names,
        }

    def file_names(self, data):
        """
            input: [
                '... /email/roles/dovecot/templates/etc/dovecot/conf.d/2.4/10-auth.conf.j2',
                '... /email/roles/dovecot/templates/etc/dovecot/conf.d/2.4/10-director.conf.j2',
                '... /email/roles/dovecot/templates/etc/dovecot/conf.d/2.4/10-logging.conf.j2'
            ]

            output: [
                '10-auth.conf', '10-director.conf', '10-logging.conf',
            ]

        """
        display.vv(f"bodsch.email::file_names({data})")

        result = []

        result = [os.path.basename(x).replace(".j2","") for x in data]

        display.vv(f"return : {result}")
        return result
