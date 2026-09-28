# python 3 headers, required if submitting to Ansible

import re

from ansible.errors import AnsibleFilterError

# Dovecot 2.3 wrote a variable as a single letter, 2.4 as "%{name}" with an
# optional filter, "%{user|domain}".
#
# A DOUBLED percent sign refers to the OWNER of a shared mailbox, a single one
# to the logged in user. The doubled form has to win, otherwise "%%u" would be
# read as a literal percent plus "%u".
#
# The two contexts differ, which is why there are two filters:
#
#   path    the owner is "%{owner_*}"
#   prefix  the owner is "$user" / "$username" / "$domain" - "%{owner_*}" is
#           not valid in a namespace prefix
#
# "%%h" has no counterpart in a prefix, so it stays what dovecot makes of it:
# a literal percent followed by "%{home}".
PATH_VARS = {
    "%%h": "%{owner_home}",
    "%%u": "%{owner_user}",
    "%%n": "%{owner_user|username}",
    "%%d": "%{owner_user|domain}",
    "%h": "%{home}",
    "%u": "%{user}",
    "%n": "%{user|username}",
    "%d": "%{user|domain}",
}

PREFIX_VARS = {
    "%%u": "$user",
    "%%n": "$username",
    "%%d": "$domain",
    "%h": "%{home}",
    "%u": "%{user}",
    "%n": "%{user|username}",
    "%d": "%{user|domain}",
}


# pop3_uidl_format has its own variables, and dovecot 2.4 checks them: a value
# without a single "%{...}" is rejected outright with
#
#   pop3_uidl_format setting doesn't contain any %{variables}
#
# Note that "doveconf -n" accepts the old value - only the service refuses to
# start on it.
#
# The names were verified against dovecot 2.4.4 by starting it with each one.
UIDL_VARS = {
    "u": "uid",
    "v": "uidvalidity",
    "g": "guid",
    "m": "md5",
    "f": "filename",
}

# "%08Xu" - hexadecimal, zero padded to a width - became "%{uid | hex(8)}".
# The width is required here: without a digit the value is left alone rather
# than guessed at.
UIDL_PATTERN = re.compile(r"%(?:0?([0-9]+)[Xx])?([uvgmf])")


def _pattern(table):
    """
    One alternation over the table, longest token first.

    Translating in a single pass is what makes the order of the table
    irrelevant: a chain of replacements would have to make sure that no
    replacement can be matched again by a later one.
    """
    tokens = sorted(table, key=len, reverse=True)

    return re.compile("|".join(re.escape(token) for token in tokens))


PATH_PATTERN = _pattern(PATH_VARS)
PREFIX_PATTERN = _pattern(PREFIX_VARS)


def _translate(value, pattern, table, name):
    if isinstance(value, (dict, list)):
        raise AnsibleFilterError(
            f"{name} expects a scalar, got {type(value).__name__}: {value!r}"
        )

    return pattern.sub(lambda match: table[match.group(0)], str(value))


class FilterModule:
    """
    Filters that translate the dovecot 2.3 variable syntax to the 2.4 one.
    """

    def filters(self):
        """
        The filters this plugin provides, keyed by the name templates use.
        """
        return {
            "dovecot_path_vars": self.path_vars,
            "dovecot_prefix_vars": self.prefix_vars,
            "dovecot_uidl_format": self.uidl_format,
        }

    def path_vars(self, value):
        """
        Translate the variables of a PATH-like value.

            /var/vmail/%d/%n       ->  /var/vmail/%{user|domain}/%{user|username}
            /var/vmail/%%d/%%n     ->  /var/vmail/%{owner_user|domain}/...

        Only safe where the meaning of a letter is unambiguous. Do NOT use it
        on a log format string: there the same letter means different things
        depending on the setting - "%m" is the SASL mechanism in
        login_log_format_elements and the message-id in deliver_log_format.
        """
        return _translate(value, PATH_PATTERN, PATH_VARS, "dovecot_path_vars")

    def prefix_vars(self, value):
        """
        Translate the variables of a NAMESPACE PREFIX.

            shared/%%u/  ->  shared/$user/
            shared/%%n@%%d/  ->  shared/$username@$domain/

        Same idea as dovecot_path_vars, but dovecot expands the owner of a
        shared mailbox as "$user" here, not as "%{owner_user}".
        """
        return _translate(value, PREFIX_PATTERN, PREFIX_VARS, "dovecot_prefix_vars")

    def uidl_format(self, value):
        """
        Translate a dovecot 2.3 pop3_uidl_format to the 2.4 syntax.

            %08Xu%08Xv  ->  %{uid | hex(8)}%{uidvalidity | hex(8)}
            %u%v        ->  %{uid}%{uidvalidity}
            %g          ->  %{guid}

        A value that is already written the 2.4 way is left alone, because
        "%{" is not one of the patterns this replaces.
        """
        if isinstance(value, (dict, list)):
            raise AnsibleFilterError(
                f"dovecot_uidl_format expects a scalar, got "
                f"{type(value).__name__}: {value!r}"
            )

        def replace(match):
            width, letter = match.group(1), match.group(2)
            name = UIDL_VARS[letter]

            return f"%{{{name} | hex({width})}}" if width else f"%{{{name}}}"

        return UIDL_PATTERN.sub(replace, str(value))
