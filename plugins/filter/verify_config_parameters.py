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
            "validate_attachment_hash": self.validate_attachment_hash,
        }

    def validate_attachment_hash(self, data, compare_to_list):
        """ """
        display.v(f"bodsch.email::validate_attachment_hash('{data}', '{compare_to_list}')")

        if ":" in data:
            for i in compare_to_list:
                if i[:-1] in data:
                    return True
        else:
            if data in compare_to_list:
                return True
        return False
