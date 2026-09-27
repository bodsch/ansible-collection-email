# python 3 headers, required if submitting to Ansible

import re

import netaddr
from ansible.errors import AnsibleFilterError
from ansible.plugins.test.core import version_compare
from ansible.utils.display import Display

display = Display()

# With the 2025-01 release mailcow replaced SOLR with Flatcurve, which runs
# inside dovecot instead of its own container.
# https://mailcow.email/posts/2025/release-2025-01/
MAILCOW_SOLR_REMOVED_IN = "2025-01"


class FilterModule:
    """
    Filters for the mailcow role: port bindings, the set of active compose
    overrides and the check whether the checked out version differs from the
    installed one.
    """

    def filters(self):
        """
        The filters this plugin provides, keyed by the name templates use.
        """
        return {
            "mailcow_ports": self.mailcow_ports,
            "mailcow_compose_active": self.mailcow_compose_active,
            "mailcow_compare_version": self.mailcow_compare_version,
        }

    def mailcow_ports(self, data):
        """
        Build a docker port binding out of an address and a port.

            {address: 10.0.0.1, port: 143}  ->  "10.0.0.1:143"
            {address: "", port: 143}        ->  "143"
            {port: 143}                     ->  "143"

        Without an address docker binds on all interfaces, which is what the
        mailcow defaults do.

        The address has to be a literal IP address - docker cannot bind to a
        host name. An address that is not one fails the run rather than
        quietly binding somewhere else.
        """
        if not isinstance(data, dict):
            raise AnsibleFilterError(
                f"mailcow_ports expects a mapping, got {type(data).__name__}: {data!r}"
            )

        bind = data.get("address", None)
        port = data.get("port", "")

        if not bind:
            return port

        try:
            netaddr.IPAddress(bind, flags=netaddr.INET_PTON | netaddr.ZEROFILL)
        except (netaddr.AddrFormatError, ValueError) as error:
            raise AnsibleFilterError(
                f"mailcow_ports: '{bind}' is not a valid IP address to bind to "
                f"({error}). docker needs a literal address here, not a host name."
            )

        return f"{bind}:{port}"

    def mailcow_compose_active(self, data, git_version=None):
        """
        List the compose override files that should be in place.

        Every entry whose state is not "absent" contributes "<name>.conf".
        When git_version is given, entries the release no longer supports
        are dropped as well:

            [{name: a}, {name: solr}] + "2025-01"  ->  ["a.conf"]

        see MAILCOW_SOLR_REMOVED_IN above.
        """
        if not isinstance(data, list):
            raise AnsibleFilterError(
                f"mailcow_compose_active expects a list, got {type(data).__name__}: {data!r}"
            )

        result = [
            f"{entry.get('name')}.conf"
            for entry in data
            if isinstance(entry, dict) and entry.get("state", "present") == "present"
        ]

        if git_version and version_compare(
            str(git_version), MAILCOW_SOLR_REMOVED_IN, ">="
        ):
            result = [entry for entry in result if not re.search(r".*solr.*", entry)]

        display.vv(f"bodsch.email::mailcow_compose_active({git_version}) = {result}")

        return result

    def mailcow_compare_version(self, data, installed=None):
        """
        Say whether the checked out mailcow differs from the installed one.

        Compares the short commit id of both sides and returns True when an
        update is pending. A missing id on either side falls back to a
        different placeholder, so an unknown state counts as "differs" and
        the playbook errs towards updating rather than skipping:

            repo 1a2b3c / installed 1a2b3c  ->  False
            repo 1a2b3c / installed 9f8e7d  ->  True
            repo {}     / installed {}      ->  True
        """
        data = data or {}
        installed = installed or {}

        repository_id = data.get("git", {}).get("commit_short_id", "left")
        installed_id = installed.get("git", {}).get("commit_short_id", "right")

        result = repository_id != installed_id

        display.vv(
            f"bodsch.email::mailcow_compare_version({repository_id}, {installed_id}) = {result}"
        )

        return result
