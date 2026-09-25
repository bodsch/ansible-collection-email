# python 3 headers, required if submitting to Ansible



from ansible.utils.display import Display

display = Display()


class FilterModule:
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
