# python 3 headers, required if submitting to Ansible

import re

from ansible.errors import AnsibleFilterError
from ansible.utils.display import Display

display = Display()

# The template tree is laid out per dovecot version:
#
#   templates/etc/dovecot/2.3/dovecot.conf.j2
#   templates/etc/dovecot/2.3/dovecot-sql.conf.ext.j2
#   templates/etc/dovecot/2.3/conf.d/10-auth.conf.j2
#   templates/etc/dovecot/2.3/auth.d/auth-sql.conf.ext.j2
#   templates/etc/dovecot/2.4/...
#
# A directory whose name is a short version ("2.3", "2.4") is a supported
# version, everything below it belongs to exactly that version.
VERSION_DIR = re.compile(r"\d+\.\d+")

# Written by its own task, and removing it would take the whole configuration
# with it, so it never appears in the file lists below.
MAIN_CONFIG = "dovecot.conf"

# The sub directories of a version, plus "root" for the dovecot-*.conf.ext
# files that sit directly in the version directory.
CONF_D = "conf.d"
AUTH_D = "auth.d"
ROOT = "root"


class FilterModule:
    """
    Filters for the dovecot role that work on its template tree.
    """

    def filters(self):
        """
        The filters this plugin provides, keyed by the name templates use.
        """
        return {
            "dovecot_template_versions": self.template_versions,
        }

    def template_versions(self, data, version: str):
        """
        Sort a template tree into the files of one dovecot version and the
        files that belong to another one.

        "data" is what community.general.filetree returns for
        templates/etc/dovecot, "version" the short version of the installed
        dovecot ("2.4").

        Returns

            available  the tree has a directory for that version
            versions   every version the tree supports, sorted
            selected   the version that was asked for, or None
            files      the files of that version, without the .j2 suffix,
                       keyed by conf.d / auth.d / root
            stale      the files of EVERY OTHER version that the selected one
                       does not have, keyed the same way

        "stale" is what makes an upgrade work. Dovecot reads every file in
        conf.d, so a 10-director.conf left behind by 2.3 keeps being parsed
        after the upgrade to 2.4 - which has no such setting any more and
        refuses to start. The role removes those files, and this is the list
        it removes.

        Only the files of a version the tree actually knows are reported, so
        a file the role never wrote is never removed.

        This replaces a fileglob lookup, which cannot do the job: fileglob
        resolves everything up to the last "/" as a literal directory, so a
        wildcard in the directory part - "2.*/conf.d/*.j2" - never matches.
        """
        if not isinstance(data, list):
            raise AnsibleFilterError(
                f"dovecot_template_versions expects the filetree as a list, "
                f"got {type(data).__name__}: {data!r}"
            )

        # version -> {conf.d: set(), auth.d: set(), root: set()}
        tree = {}

        for entry in data:
            if not isinstance(entry, dict):
                continue

            path = entry.get("path", "")
            parts = path.split("/")

            if not VERSION_DIR.fullmatch(parts[0]):
                continue

            bucket = tree.setdefault(
                parts[0], {CONF_D: set(), AUTH_D: set(), ROOT: set()}
            )

            if entry.get("state") != "file":
                continue

            name = parts[-1].removesuffix(".j2")

            if not name:
                continue

            if len(parts) == 2 and name != MAIN_CONFIG:
                bucket[ROOT].add(name)
            elif len(parts) == 3 and parts[1] in (CONF_D, AUTH_D):
                bucket[parts[1]].add(name)

        versions = sorted(tree.keys())
        available = version in tree

        selected = tree.get(version, {CONF_D: set(), AUTH_D: set(), ROOT: set()})

        # Everything the other versions ship, so a file that both versions
        # have is never treated as stale.
        others = {CONF_D: set(), AUTH_D: set(), ROOT: set()}

        # A version the tree does not know leaves "stale" empty on purpose.
        # The role stops on it anyway, and without a selected version every
        # file of every version would look stale - which would wipe a working
        # configuration instead of cleaning up after an upgrade.
        if available:
            for name, bucket in tree.items():
                if name == version:
                    continue
                for where in others:
                    others[where] |= bucket[where]

        result = {
            "available": available,
            "versions": versions,
            "selected": version if available else None,
            "files": {where: sorted(selected[where]) for where in selected},
            "stale": {
                where: sorted(others[where] - selected[where]) for where in others
            },
        }

        display.vv(
            f"bodsch.email::dovecot_template_versions({version}) = "
            f"available={result['available']}, versions={result['versions']}, "
            f"stale={result['stale']}"
        )

        return result
