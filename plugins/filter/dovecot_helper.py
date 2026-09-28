# python 3 headers, required if submitting to Ansible

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
            "config_value": self.config_value,
            "database_connection": self.database_connection,
        }

    def config_value(self, data, default=False):
        """
        Render a value the way a dovecot configuration file expects it.

        Booleans become the strings "yes" / "no", everything else is passed
        through unchanged. Templates also use the return value as a truth
        test, so a value that must not be written has to stay falsy.

            True    -> "yes"
            False   -> "no"
            "256M"  -> "256M"
            0       -> 0        (falsy: the template skips the line)
            None    -> default  (False unless given)
        """
        if data is None:
            return default

        if isinstance(data, bool):
            return "yes" if data else "no"

        return data

    def database_connection(self, data):
        """
        Build a dovecot 2.3 "connect" string from a mapping.

        Only the keys that carry a value end up in the result, always in the
        same order, so the generated file does not change between runs.

            {host: localhost, dbname: mails, user: u, password: p}
            -> "host=localhost dbname=mails user=u password=p"

        An empty mapping yields an empty string; the caller decides whether
        that is an error.

        Note: dovecot 2.4 has no connect string any more - the connection is
        expressed as driver specific settings (mysql_host, mysql_dbname, ...)
        inside the passdb / userdb block.
        """
        if not isinstance(data, dict):
            raise AnsibleFilterError(
                f"database_connection expects a mapping, got {type(data).__name__}"
            )

        # fixed order, so the rendered file is stable
        keys = ("host", "port", "dbname", "user", "password")

        return " ".join(
            f"{key}={data[key]}" for key in keys if data.get(key) not in (None, "")
        )
