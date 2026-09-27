# python 3 headers, required if submitting to Ansible

from ansible.errors import AnsibleFilterError
from ansible.utils.display import Display

display = Display()


class FilterModule:
    """
    Filters for the postfix role: lookup table entries, relay hosts and the
    SASL credentials that belong to them.
    """

    def filters(self):
        """
        The filters this plugin provides, keyed by the name templates use.
        """
        return {
            "postfix_map_data": self.postfix_map_data,
            "valid_list_data": self.valid_list_data,
            "sasl_data": self.sasl_data,
            "relay_data": self.relay_data,
        }

    @staticmethod
    def _relay_host(data, mxlookup=False):
        """
        Fold host and port into the single "host" value postfix expects.

        Square brackets around the host name switch MX lookups off, which is
        what you want for a fixed smarthost:

            host=smtp.example.com port=587
              mxlookup=False -> "[smtp.example.com]:587"
              mxlookup=True  -> "smtp.example.com:587"

        Without host or port the username is used, which covers the case
        where the username already is the relay host.

        see https://www.postfix.org/postconf.5.html#relayhost
        """
        username = data.get("username", None)
        host = data.get("host", None)
        port = data.get("port", None)

        if not host or not port:
            data["host"] = username
            return data

        data.pop("port", None)
        data["host"] = f"[{host}]:{port}" if not mxlookup else f"{host}:{port}"

        return data

    def postfix_map_data(self, data):
        """
        Split one lookup table entry into its key and its value.

        The mapping is read BY POSITION, not by name: the value of the first
        key becomes the table key, the value of the second key becomes the
        table value. That is deliberate - every map type uses its own names:

            {virtual: a@x, alias: b@y}       -> ("a@x", "b@y")
            {virtual: a@x, aliases: [b, c]}  -> ("a@x", "b, c")
            {pattern: "*", result: ":"}      -> ("*", ":")

        A list value is joined with ", ". A third key and beyond is ignored
        and reported as a warning, because postfix lookup tables only have
        two columns.
        """
        if not isinstance(data, dict):
            raise AnsibleFilterError(
                f"postfix_map_data expects a mapping, got {type(data).__name__}: {data!r}"
            )

        keys = list(data.keys())

        if len(keys) < 2:
            raise AnsibleFilterError(
                "postfix_map_data expects a mapping with at least two entries "
                f"(the lookup key and its value), got {data!r}"
            )

        if len(keys) > 2:
            display.warning(
                f"postfix_map_data: only the first two entries of {data!r} are used, "
                f"ignoring {', '.join(keys[2:])}"
            )

        key = data[keys[0]]
        values = data[keys[1]]

        if isinstance(values, list):
            values = ", ".join(values)

        return key, values

    def valid_list_data(self, data, valid_entries):
        """
        Keep only the entries that are also in the list of allowed values.

        The result is sorted and free of duplicates, so the generated
        configuration does not change order between runs.

            ["b", "x", "a"] + ["a", "b", "c"]  ->  ["a", "b"]

        Both input lists are left untouched.
        """
        if not isinstance(data, list):
            raise AnsibleFilterError(
                f"valid_list_data expects a list, got {type(data).__name__}: {data!r}"
            )

        if not isinstance(valid_entries, list):
            raise AnsibleFilterError(
                "valid_list_data expects a list of valid entries, got "
                f"{type(valid_entries).__name__}: {valid_entries!r}"
            )

        return sorted(set(data).intersection(valid_entries))

    def sasl_data(self, data, mxlookup=False):
        """
        Bring one SASL entry into the notation postfix expects.

        Host and port are folded into a single "host" value, see
        _relay_host() for the exact rules.

            {username: u, host: smtp.example.com, port: 587}
            -> {username: u, host: "[smtp.example.com]:587"}

        The input mapping is not modified, a copy is returned.
        """
        if not isinstance(data, dict):
            raise AnsibleFilterError(
                f"sasl_data expects a mapping, got {type(data).__name__}: {data!r}"
            )

        return self._relay_host(dict(data), mxlookup)

    def relay_data(self, data, sasl_data, mxlookup=False):
        """
        Same as sasl_data(), plus the check that credentials exist.

        The username of the relay entry has to appear in sasl_data. If it
        does not, the entry comes back marked instead of raising, so a
        playbook can report every broken relay at once rather than stopping
        at the first:

            {error: True, msg: "The user name '<u>' is not present in the
             SASL configuration."}

        On success error is False, msg is None and host is built the way
        sasl_data() builds it.

        The input mapping is not modified, a copy is returned.
        """
        if not isinstance(data, dict):
            raise AnsibleFilterError(
                f"relay_data expects a mapping, got {type(data).__name__}: {data!r}"
            )

        if not isinstance(sasl_data, list):
            raise AnsibleFilterError(
                "relay_data expects the SASL entries as a list, got "
                f"{type(sasl_data).__name__}: {sasl_data!r}"
            )

        result = dict(data)
        username = result.get("username", None)

        known = any(
            entry.get("username") == username
            for entry in sasl_data
            if isinstance(entry, dict)
        )

        if not known:
            result["error"] = True
            result["msg"] = (
                f"The user name '{username}' is not present in the SASL configuration."
            )
            return result

        result["error"] = False
        result["msg"] = None

        return self._relay_host(result, mxlookup)
