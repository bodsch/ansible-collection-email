# coding: utf-8
from __future__ import annotations, unicode_literals

import re
import pytest
from helper.molecule import get_vars, infra_hosts, local_facts

testinfra_hosts = infra_hosts(host_name="instance")

# --- tests -----------------------------------------------------------------

# _facts = local_facts(host=host, fact="dovecot")

@pytest.mark.parametrize(
    "dirs",
    [
        "/etc/dovecot",
        "/etc/dovecot/conf.d",
        "/etc/dovecot/auth.d",
        "/etc/dovecot/sql.d",
        "/var/log/dovecot",
    ],
)
def test_directories(host, dirs):
    d = host.file(dirs)
    assert d.is_directory


# The configuration files the role writes, split by the template version that
# owns them. templates/etc/dovecot/<version>/ is the source of truth for these
# lists - keep them in sync when a template is added or removed.
CONFIG_FILES = {
    "common": [
        "/etc/dovecot/dovecot.conf",
        "/etc/dovecot/auth.d/auth-deny.conf.ext",
        "/etc/dovecot/auth.d/auth-ldap.conf.ext",
        "/etc/dovecot/auth.d/auth-master.conf.ext",
        "/etc/dovecot/auth.d/auth-passwdfile.conf.ext",
        "/etc/dovecot/auth.d/auth-sql.conf.ext",
        "/etc/dovecot/auth.d/auth-static.conf.ext",
        "/etc/dovecot/auth.d/auth-system.conf.ext",
        "/etc/dovecot/conf.d/10-auth.conf",
        "/etc/dovecot/conf.d/10-logging.conf",
        "/etc/dovecot/conf.d/10-mail.conf",
        "/etc/dovecot/conf.d/10-master.conf",
        "/etc/dovecot/conf.d/10-ssl.conf",
        "/etc/dovecot/conf.d/15-lda.conf",
        "/etc/dovecot/conf.d/15-mailboxes.conf",
        "/etc/dovecot/conf.d/20-imap.conf",
        "/etc/dovecot/conf.d/20-lmtp.conf",
        "/etc/dovecot/conf.d/20-managesieve.conf",
        "/etc/dovecot/conf.d/20-pop3.conf",
        "/etc/dovecot/conf.d/20-submission.conf",
        "/etc/dovecot/conf.d/90-acl.conf",
        "/etc/dovecot/conf.d/90-plugin.conf",
        "/etc/dovecot/conf.d/90-quota.conf",
        "/etc/dovecot/conf.d/90-sieve-extprograms.conf",
        "/etc/dovecot/conf.d/90-sieve.conf",
    ],
    # dovecot 2.3 only
    "2.3": [
        "/etc/dovecot/auth.d/auth-checkpassword.conf.ext",
        "/etc/dovecot/auth.d/auth-dict.conf.ext",
        "/etc/dovecot/auth.d/auth-vpopmail.conf.ext",
        "/etc/dovecot/conf.d/10-director.conf",
        "/etc/dovecot/conf.d/10-tcpwrapper.conf",
        "/etc/dovecot/dovecot-dict-auth.conf.ext",
        "/etc/dovecot/dovecot-dict-sql.conf.ext",
        "/etc/dovecot/dovecot-ldap.conf.ext",
        "/etc/dovecot/dovecot-sql.conf.ext",
    ],
    # dovecot 2.4 only
    "2.4": [
        "/etc/dovecot/auth.d/auth-oauth2.conf.ext",
        "/etc/dovecot/conf.d/10-metrics.conf",
        "/etc/dovecot/conf.d/30-dict-server.conf",
        "/etc/dovecot/conf.d/90-fts.conf",
    ],
}


def dovecot_short_version(host):
    """
    The major.minor version of the installed dovecot, "2.4".

    It decides which template directory the role used, and therefore which
    files have to be there.
    """
    match = re.match(r"(\d+\.\d+)", host.run("dovecot --version").stdout.strip())

    assert match, "could not read the dovecot version"

    return match.group(1)


def test_files(host):
    """
    Every file of the installed version is written.
    """
    version = dovecot_short_version(host)

    assert version in CONFIG_FILES, f"no expected files for dovecot {version}"

    expected = CONFIG_FILES["common"] + CONFIG_FILES[version]
    missing = [path for path in expected if not host.file(path).is_file]

    assert not missing, f"dovecot {version}: {len(missing)} file(s) missing: {missing}"


def test_files_of_another_version_are_removed(host):
    """
    Nothing is left over from another template version.

    Dovecot reads every file in conf.d, so a 10-director.conf written by the
    2.3 templates keeps being parsed after an upgrade to 2.4 - which does not
    know that setting any more and refuses to start. The role removes those
    files, and this is what proves it on a real host.
    """
    version = dovecot_short_version(host)
    stale = [
        path
        for other, paths in CONFIG_FILES.items()
        if other not in ("common", version)
        for path in paths
        if path not in CONFIG_FILES[version]
    ]

    assert stale, "nothing to check - are there still two template versions?"

    left = [path for path in stale if host.file(path).exists]

    assert not left, f"dovecot {version}: {len(left)} file(s) left over: {left}"


def test_service_running_and_enabled(host, get_vars):
    """
    running service
    """
    service_name = "dovecot"

    service = host.service(service_name)
    assert service.is_running
    assert service.is_enabled


def test_listening_socket(host, get_vars):
    """ """
    listening = host.socket.get_listening_sockets()

    for i in listening:
        print(i)

    listen = []
    listen.append("tcp://127.0.0.1:110")
    listen.append("tcp://127.0.0.1:143")
    listen.append("tcp://127.0.0.1:993")
    listen.append("tcp://127.0.0.1:995")

    for spec in listen:
        socket = host.socket(spec)
        assert socket.is_listening
