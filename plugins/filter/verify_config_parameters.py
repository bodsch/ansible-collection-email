# python 3 headers, required if submitting to Ansible

from ansible.errors import AnsibleFilterError
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
        """
        Check a mail_attachment_hash value against the allowed hashes.

        Two cases:

        - the value carries arguments, such as "%{sha1:2}/%{sha1:2}". Those
          are recognised by the colon, and the allowed patterns are then
          matched without their closing brace, so "%{sha1}" also covers
          "%{sha1:2}".
        - otherwise the value has to appear in the list verbatim.

            "%{sha256}"            + ["%{sha256}"]  -> True
            "%{sha1:2}/%{sha1:2}"  + ["%{sha1}"]    -> True
            "%{md5}"               + ["%{sha1}"]    -> False
            "sha1"                 + ["%{sha1}"]    -> False
        """
        if not isinstance(data, str):
            raise AnsibleFilterError(
                f"validate_attachment_hash expects a string, got {type(data).__name__}: {data!r}"
            )

        if not isinstance(compare_to_list, list):
            raise AnsibleFilterError(
                "validate_attachment_hash expects a list of allowed hashes, got "
                f"{type(compare_to_list).__name__}: {compare_to_list!r}"
            )

        display.v(
            f"bodsch.email::validate_attachment_hash('{data}', '{compare_to_list}')"
        )

        if ":" in data:
            # "%{sha1}" has to match "%{sha1:2}" as well, so compare without
            # the closing brace
            return any(
                pattern.rstrip("}") in data
                for pattern in compare_to_list
                if isinstance(pattern, str)
            )

        return data in compare_to_list
