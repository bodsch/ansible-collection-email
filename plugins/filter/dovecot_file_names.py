# python 3 headers, required if submitting to Ansible

import os

from ansible.errors import AnsibleFilterError
from ansible.utils.display import Display

display = Display()


class FilterModule:
    """
    ansible filter
    """

    def filters(self):
        """
        The filters this plugin provides, keyed by the name templates use.
        """
        return {
            "file_names": self.file_names,
        }

    def file_names(self, data):
        """
        Turn template paths into the file names they are rendered to.

        Used to derive the list of configuration files a dovecot version
        owns, from the templates that exist for it.

            ["…/2.4/conf.d/10-auth.conf.j2", "…/2.4/conf.d/10-mail.conf.j2"]
            -> ["10-auth.conf", "10-mail.conf"]

        Only a trailing ".j2" is removed, so a name that contains ".j2"
        somewhere else stays intact. Empty entries - a fileglob that matched
        nothing returns one - are dropped.
        """
        if not isinstance(data, list):
            raise AnsibleFilterError(
                f"file_names expects a list, got {type(data).__name__}"
            )

        return [
            os.path.basename(entry).removesuffix(".j2")
            for entry in data
            if entry
        ]
