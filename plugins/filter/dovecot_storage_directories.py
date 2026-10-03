# python 3 headers, required if submitting to Ansible

import re

from ansible.errors import AnsibleFilterError

# Dovecot creates the PER USER part of a storage path itself, but not the
# static parent above it. With
#
#   mail_control_path = /var/mail/CONTROL/%{user|domain}/%{user|username}
#
# and /var/mail owned by root, the first subscription fails with
#
#   mkdir(/var/mail/CONTROL/example.com) failed: Permission denied
#   cmd mailbox subscribe: ... Internal error occurred.
#
# and the client reports that it cannot subscribe. The same happens to the
# index path, and to mail_home when the mail root does not exist yet.
#
# This filter returns the static parents, so the role can create them for the
# virtual mail user.

# Path settings of dovecot_mail and of a single namespace. Everything else in
# those dictionaries is not a path.
PATH_SETTINGS = (
    "mail_home",
    "mail_path",
    "mail_inbox_path",
    "mail_index_path",
    "mail_index_private_path",
    "mail_control_path",
    "mail_volatile_path",
    "mail_alt_path",
    "mail_attachment_dir",
    "mail_ext_attachment_path",
)

# Options of a 2.3 "driver:path:OPTION=value" location that carry a path.
# LAYOUT and the other flags do not.
LOCATION_OPTIONS = (
    "INDEX",
    "INDEXPVT",
    "CONTROL",
    "VOLATILEDIR",
    "ALT",
    "INBOX",
)

# The settings that hold a "driver:path:OPTION=value" string.
LOCATION_SETTINGS = ("mail_location", "location")

# Everything from the first variable on is per user and dovecot's job.
VARIABLE = re.compile(r"[%~$]")


def _static_prefix(value):
    """
    The directory of a path up to its first variable.

        /var/mail/INDEX/%{user|domain}/%{user|username}  ->  /var/mail/INDEX
        /srv/mail/idx-%{user}                            ->  /srv/mail
        /srv/mail/PUBLIC                                 ->  /srv/mail/PUBLIC
        ~/Maildir                                        ->  None
        %{home}                                          ->  None

    Returns None for anything that is not an absolute path, and for a path
    whose static part is a top level directory: "/", "/var" and the like are
    never ours to create or to chown.
    """
    if not value:
        return None

    text = str(value).strip()
    match = VARIABLE.search(text)

    if match is not None:
        text = text[: match.start()]
        # a variable in the middle of a name ("idx-%{user}") leaves a partial
        # segment behind - the directory is the one above it.
        if not text.endswith("/"):
            text = text.rsplit("/", 1)[0]

    text = text.rstrip("/")

    if not text.startswith("/"):
        return None

    # "/var" has one segment, "/var/mail" has two.
    if len([segment for segment in text.split("/") if segment]) < 2:
        return None

    return text


def _location_paths(value):
    """
    The paths of a "driver:path:OPTION=value:..." location string.

        maildir:%h:INDEX=/srv/mail/INDEX/%d/%n:LAYOUT=maildir++
            ->  ["%h", "/srv/mail/INDEX/%d/%n"]

    The first field is the driver and never a path.
    """
    parts = str(value).split(":")
    paths = parts[1:2]

    for option in parts[2:]:
        name, separator, argument = option.partition("=")
        if separator and name.strip().upper() in LOCATION_OPTIONS:
            paths.append(argument)

    return paths


def _collect(source):
    """Every path-like value of one mapping."""
    paths = []

    for setting in PATH_SETTINGS:
        paths.append(source.get(setting))

    for setting in LOCATION_SETTINGS:
        value = source.get(setting)
        if value:
            paths.extend(_location_paths(value))

    return paths


class FilterModule:
    """
    The directories a dovecot mail configuration needs on disk.
    """

    def filters(self):
        return {
            "dovecot_storage_directories": self.storage_directories,
        }

    def storage_directories(self, mail, mailboxes=None):
        """
        Return the static parent directories of every storage path in
        dovecot_mail, sorted and without duplicates.
        """
        if not isinstance(mail, dict):
            raise AnsibleFilterError(
                f"dovecot_storage_directories expects a dictionary, got "
                f"{type(mail).__name__}: {mail!r}"
            )

        candidates = _collect(mail)

        for namespace in mail.get("namespaces") or []:
            if isinstance(namespace, dict):
                candidates.extend(_collect(namespace))

        # dovecot_mailboxes carries its namespaces keyed BY name, and a
        # namespace there can bring a location of its own.
        for entry in (mailboxes or {}).get("namespaces") or []:
            if not isinstance(entry, dict):
                continue
            for namespace in entry.values():
                if isinstance(namespace, dict):
                    candidates.extend(_collect(namespace))

        directories = {
            prefix
            for prefix in (_static_prefix(candidate) for candidate in candidates)
            if prefix
        }

        return sorted(directories)
