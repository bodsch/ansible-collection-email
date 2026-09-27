# python 3 headers, required if submitting to Ansible

import re

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
            "dovecot_template_versions": self.template_versions,
        }

    def template_versions(self, data, version: str):
        """ """

        versions = sorted({
            entry["path"]
            for entry in data
            if entry.get("state") == "directory"
            and re.fullmatch(r"\d+\.\d+", entry.get("path", ""))
        })

        if version in versions:
            return {"available": True, "versions": versions}
        else:
            return {"available": False, "versions": versions}
