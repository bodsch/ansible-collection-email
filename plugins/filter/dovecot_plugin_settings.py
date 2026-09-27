# python 3 headers, required if submitting to Ansible

import re

from ansible.errors import AnsibleFilterError

# Dovecot 2.4 dropped the plugin { } block - every setting that lived in it is
# global now, and many were renamed on the way.
#
# A pure rename is applied. Anything STRUCTURAL is reported instead, because
# 2.4 refuses to start on an unknown setting: a comment in the generated file
# shows exactly what has to be migrated by hand.
#
# Sources: the 2.3-to-2.4 upgrade guide and "doveconf -a" of dovecot 2.4.1,
# re-checked against 2.4.4.
PLUGIN_RENAMES = {
    "acl": "acl_driver",
    "acl_anyone": "imap_acl_allow_anyone",
    "quota_grace": "quota_storage_grace",
    "quota_max_mail_size": "quota_mail_size",
    "quota_over_flag": "quota_over_status_current",
    "quota_over_flag_lazy_check": "quota_over_status_lazy_check",
    "quota_over_flag_value": "quota_over_status_mask",
    "sieve_default_name": "sieve_script_name",
    "sieve_editheader_forbid_add": "sieve_editheader_header_forbid_add",
    "sieve_editheader_forbid_delete": "sieve_editheader_header_forbid_delete",
    "sieve_quota_max_scripts": "sieve_quota_script_count",
    "sieve_quota_max_storage": "sieve_quota_storage_size",
    "sieve_spamtest_max_header": "sieve_spamtest_score_max_header",
    "sieve_spamtest_max_value": "sieve_spamtest_score_max_value",
    "sieve_user_log": "sieve_user_log_path",
    "sieve_variables_max_scope_size": "sieve_variables_max_scope_count",
    "sieve_variables_max_variable_size": "sieve_variables_max_value_size",
    "sieve_virustest_max_header": "sieve_virustest_score_max_header",
    "sieve_virustest_max_value": "sieve_virustest_score_max_value",
}

# old name -> what to do instead; these need more than a rename
PLUGIN_UNMAPPED = {
    "autosubscribe": 'use "mailbox <name> { auto = subscribe }" in 15-mailboxes',
    "quota": 'configure a "quota <name> { quota_driver = ... }" block',
    "quota_rule": "use quota_storage_size / quota_message_count in a quota block",
    "quota_rule2": "use quota_storage_size / quota_message_count in a quota block",
    "quota_over_script": "use quota_over_status together with an execute filter",
    "quota_warning": 'configure a "quota_warning <name> { }" block',
    "quota_warning2": 'configure a "quota_warning <name> { }" block',
    "sieve": "use sieve_script_path inside a sieve_script block",
    "sieve_after": "use a sieve_script block with sieve_script_type = after",
    "sieve_before": "use a sieve_script block with sieve_script_type = before",
    "sieve_default": "use a sieve_script block with sieve_script_type = default",
    "sieve_dir": "use sieve_script_path inside a sieve_script block",
    "sieve_discard": "use a sieve_script block with sieve_script_type = discard",
    "sieve_global": "use a sieve_script block with sieve_script_type = global",
    "sieve_global_dir": "use sieve_script_path inside a sieve_script block",
    "sieve_global_path": "use sieve_script_path inside a sieve_script block",
    "acl_global_path": (
        "removed in 2.4.4; configure the acl settings inside the mailbox blocks"
    ),
    "sieve_spamtest_text_value": (
        "became a string list; put all values under one sieve_spamtest_text_value"
    ),
    "sieve_virustest_text_value": (
        "became a string list; put all values under one sieve_virustest_text_value"
    ),
    "sieve_editheader_protected": (
        "split into sieve_editheader_header_forbid_add and _forbid_delete"
    ),
    "sieve_vacation_max_subject_codepoints": "removed in 2.4",
}

# What dovecot reads as "on" wherever a 2.3 setting took a boolean.
TRUE_VALUES = ("yes", "true", "1", "on")

# 2.3 acl_anyone took "allow" or "authenticated", 2.4 takes a boolean. Both old
# values enable the anyone/authenticated ACL identifiers.
ACL_ANYONE_ENABLED = ("allow", "authenticated", "yes", "true")

ACL_ANYONE_NOTE = [
    "# NOTE acl_anyone = authenticated has no 2.4 equivalent that distinguishes it",
    '#   from "allow"; imap_acl_allow_anyone only enables or disables the',
    "#   anyone/authenticated ACL identifiers.",
]

QUOTA_GRACE_HINT = [
    "dovecot 2.4: quota_storage_grace is a size, not a percentage.",
    "Restate it as an absolute size, e.g. quota_storage_grace = 10M",
]

# 2.3 escaped a literal percent sign as "%%", because "%" started a variable.
# 2.4 writes a variable as "%{...}", so a bare "%" is literal and "%%" is wrong
# (a quota grace of "10%%", for instance). Only a "%%" that is NOT followed by
# a letter is unescaped - "%%u" and friends are shared mailbox variables and
# belong to the dovecot_path_vars / dovecot_prefix_vars filters.
LITERAL_PERCENT = re.compile(r"%%(?![A-Za-z])")

# 2.3 numbered its repeatable plugin settings: quota2, quota2_rule,
# sieve_before2, sieve_before3, autosubscribe4, ... They mean the same as their
# base name, and 2.4 replaced all of them with named filters.
DIGITS = re.compile(r"[0-9]+")


class FilterModule:
    """
    Filter that translates a dovecot 2.3 plugin setting to its 2.4 form.
    """

    def filters(self):
        """
        The filters this plugin provides, keyed by the name templates use.
        """
        return {
            "dovecot_plugin_setting": self.plugin_setting,
        }

    def plugin_setting(self, key, value):
        """
        Decide what a 2.3 plugin setting becomes in 2.4.

        Returns what to write, never the text itself - the template owns the
        layout. One of three shapes, told apart by "kind":

            {kind: setting, key, value, notes}
                write "key = value". "notes" are complete comment lines to put
                in front of it, usually empty.

            {kind: unmapped, key, value, hints}
                the setting is structural and has no 2.4 counterpart. Write it
                as a comment: the original key and value, plus every line of
                "hints" as an indented comment.

            {kind: acl_sharing_map, driver, path}
                acl_shared_dict became a named filter holding a dict.

        A numbered variant falls back to its base name (quota2 -> quota,
        sieve_before3 -> sieve_before), but only when that base name is
        actually known - otherwise a setting that legitimately contains a digit
        would be mangled.
        """
        if not isinstance(key, str):
            raise AnsibleFilterError(
                f"dovecot_plugin_setting expects the setting name as a string, "
                f"got {type(key).__name__}: {key!r}"
            )

        base = DIGITS.sub("", key)
        text = str(value)

        unmapped = key if key in PLUGIN_UNMAPPED else base
        if unmapped in PLUGIN_UNMAPPED:
            return {
                "kind": "unmapped",
                "key": key,
                "value": value,
                "hints": [f"dovecot 2.4: {PLUGIN_UNMAPPED[unmapped]}"],
            }

        if key == "sieve_vacation_dont_check_recipient":
            # the meaning was inverted along with the rename
            return self._setting(
                "sieve_vacation_check_recipient",
                "no" if text.lower() in TRUE_VALUES else "yes",
            )

        if key == "quota_grace" and "%" in text:
            # 2.3 quota_grace was a percentage of the quota (default 10%%).
            # 2.4 quota_storage_grace is a SIZE (default 10M) - a percentage
            # cannot be carried over, it has to be restated.
            return {
                "kind": "unmapped",
                "key": key,
                "value": value,
                "hints": QUOTA_GRACE_HINT,
            }

        if key == "acl_shared_dict":
            # 2.3: acl_shared_dict = file:/var/vmail/shared-mailboxes
            # 2.4: a named filter holding a dict, the driver comes from the
            #      prefix
            driver, _, path = text.partition(":")
            return {"kind": "acl_sharing_map", "driver": driver, "path": path}

        if key == "acl_anyone":
            return self._setting(
                "imap_acl_allow_anyone",
                "yes" if text.lower() in ACL_ANYONE_ENABLED else "no",
                notes=ACL_ANYONE_NOTE if text.lower() == "authenticated" else [],
            )

        return self._setting(
            PLUGIN_RENAMES.get(key, PLUGIN_RENAMES.get(base, key)),
            LITERAL_PERCENT.sub("%", text),
        )

    @staticmethod
    def _setting(key, value, notes=None):
        return {"kind": "setting", "key": key, "value": value, "notes": notes or []}
