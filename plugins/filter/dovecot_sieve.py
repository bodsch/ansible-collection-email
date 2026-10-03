# python 3 headers, required if submitting to Ansible

import re

from ansible.errors import AnsibleFilterError

# Dovecot 2.3 described every sieve script location with a setting of its own,
# its value a location string:
#
#   sieve = file:~/sieve;active=~/.dovecot.sieve
#
# 2.4 turned each of them into a "sieve_script <name> { }" named filter, and
# the location string into separate settings. The type of a block is what the
# 2.3 setting name used to express.
LOCATION_TYPES = {
    "sieve": "personal",
    "sieve_before": "before",
    "sieve_after": "after",
    "sieve_default": "default",
    "sieve_global_path": "default",
    "sieve_discard": "discard",
    "sieve_global": "global",
    "sieve_global_dir": "global",
}

# The options of a 2.3 location string, ";active=..." for instance.
LOCATION_OPTIONS = {
    "active": "active_path",
    "bindir": "bin_path",
    "name": "name",
}

# Extensions dovecot 2.4 no longer knows - it ignores them with a warning, it
# does not refuse to start. Verified against pigeonhole 2.4.1: each name below
# makes doveconf report "ignored unknown extension". The successor is enabled
# by default.
REMOVED_EXTENSIONS = {
    "notify": "enotify",
    "imapflags": "imap4flags",
    "vnd.dovecot.duplicate": "duplicate",
}

# sieve_before2, sieve_after3, ... mean the same as their base name.
NUMBERED = re.compile(r"^([a-z_]+?)([0-9]+)$")


def _flatten(plugins):
    """
    The settings of dovecot_sieve.plugins as one ordered list of pairs.

    The variable is a list of mappings, and a mapping either holds the
    settings themselves or groups them under a name of its own:

        - sieve: file:~/sieve              - default:
                                               sieve: file:~/sieve
    """
    if plugins is None:
        return []
    if isinstance(plugins, dict):
        plugins = [plugins]
    if not isinstance(plugins, list):
        raise AnsibleFilterError(
            f"dovecot_sieve_scripts expects a list of mappings, "
            f"got {type(plugins).__name__}: {plugins!r}"
        )

    pairs = []
    for entry in plugins:
        if not isinstance(entry, dict):
            continue
        for key, value in entry.items():
            if isinstance(value, dict):
                pairs.extend(value.items())
            else:
                pairs.append((key, value))
    return pairs


def _location(value):
    """
    Split a 2.3 location string into the settings of a sieve_script block.

        file:~/sieve;active=~/.dovecot.sieve
            -> {driver: file, path: ~/sieve, active_path: ~/.dovecot.sieve}

    The driver prefix is optional and defaults to "file". An option that has
    no 2.4 counterpart is returned separately, so it can be reported instead
    of silently dropped.
    """
    text = str(value).strip()
    parts = text.split(";")
    head, options = parts[0], parts[1:]

    driver = "file"
    match = re.match(r"^([a-z]+):(.*)$", head)
    if match:
        driver, head = match.group(1), match.group(2)

    settings = {"driver": driver}
    if head:
        settings["path"] = head

    unknown = []
    for option in options:
        name, _, option_value = option.partition("=")
        name = name.strip()
        if name in LOCATION_OPTIONS and option_value:
            settings[LOCATION_OPTIONS[name]] = option_value
        elif name:
            unknown.append(option)

    return settings, unknown


def _extension_names(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(token) for item in value for token in str(item).split()]
    return str(value).split()


class FilterModule:
    """
    Filters that translate the dovecot 2.3 sieve configuration to its 2.4 form.
    """

    def filters(self):
        """
        The filters this plugin provides, keyed by the name templates use.
        """
        return {
            "dovecot_sieve_scripts": self.sieve_scripts,
            "dovecot_sieve_extensions": self.sieve_extensions,
        }

    def sieve_scripts(self, plugins):
        """
        Turn the 2.3 script location settings of dovecot_sieve.plugins into
        2.4 sieve_script blocks.

        Returns
            scripts    {block name: {setting: value}}, in the order of the input
            consumed   the 2.3 setting names that went into a block - the
                       template must not write them a second time
            notes      complete comment lines for what could not be carried over

        sieve_dir is the old name of the personal script directory. It is only
        used when "sieve" does not name a directory itself: with
        "sieve = ~/.dovecot.sieve" the file is the ACTIVE script, and sieve_dir
        holds the scripts - which is "path" plus "active_path" in 2.4.

        Variables are left alone; paths go through dovecot_path_vars in the
        template, like every other path.
        """
        pairs = _flatten(plugins)
        settings = {}
        for key, value in pairs:
            if value is None or str(value).strip() == "":
                continue
            settings[key] = value

        scripts = {}
        consumed = []
        notes = []

        for key, value in settings.items():
            match = NUMBERED.match(key)
            base = match.group(1) if match and match.group(1) in LOCATION_TYPES else key
            if base not in LOCATION_TYPES:
                continue

            block, unknown = _location(value)
            script_type = LOCATION_TYPES[base]

            # the block name is the 2.3 setting name minus its "sieve_" prefix:
            # before, before2, after, default, ... - unique by construction,
            # and recognisable in the generated file.
            name = "personal" if key == "sieve" else key.removeprefix("sieve_")
            if script_type != "personal":
                block["type"] = script_type

            if script_type == "default" and "sieve_default_name" in settings:
                block.setdefault("name", settings["sieve_default_name"])
                consumed.append("sieve_default_name")

            for option in unknown:
                notes.append(f"# NOTE {key}: option '{option}' has no dovecot 2.4 counterpart")

            scripts[name] = block
            consumed.append(key)

        if "sieve_dir" in settings:
            consumed.append("sieve_dir")
            personal = scripts.get("personal")
            if personal is None:
                scripts = {"personal": {"driver": "file", "path": settings["sieve_dir"]}, **scripts}
            elif "active_path" not in personal and personal.get("driver") == "file":
                # "sieve" named the active script, sieve_dir the storage
                personal["active_path"] = personal.get("path")
                personal["path"] = settings["sieve_dir"]

        return {
            "scripts": scripts,
            "consumed": list(dict.fromkeys(consumed)),
            "notes": notes,
        }

    def sieve_extensions(self, value):
        """
        Translate a 2.3 extension list (sieve_extensions,
        sieve_global_extensions) to a 2.4 boolean list.

        2.3 had two forms in one string:

            +a -b      adjust the default list
            a b +c     REPLACE the default list (a plain entry resets it)

        2.4 writes the first as a block, "name { a = yes  b = no }", and the
        second as an assignment, "name = a b c".

        Returns
            replace    true for the assignment form
            enable     names to switch on (or the whole list when replace)
            disable    names to switch off
            removed    {name: successor} for names 2.4 no longer knows; they
                       are dropped from enable/disable
        """
        replace = False
        enable = []
        disable = []
        removed = {}

        for token in _extension_names(value):
            if token[0] in "+-":
                sign, name = token[0], token[1:]
            else:
                sign, name = "", token
                replace = True
            if not name:
                continue
            if name in REMOVED_EXTENSIONS:
                removed[name] = REMOVED_EXTENSIONS[name]
                continue
            target = disable if sign == "-" else enable
            if name not in target:
                target.append(name)

        if replace:
            enable = [name for name in enable if name not in disable]
            disable = []

        return {
            "replace": replace,
            "enable": enable,
            "disable": disable,
            "removed": removed,
        }
