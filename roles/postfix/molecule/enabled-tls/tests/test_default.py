# coding: utf-8
from __future__ import annotations, unicode_literals

import pytest
from helper.molecule import get_vars, infra_hosts, local_facts

testinfra_hosts = infra_hosts(host_name="instance")

# --- tests -----------------------------------------------------------------

# _facts = local_facts(host=host, fact="postfix")

def test_directories(host, get_vars):
    """ """
    directories = [
        "/etc/postfix",
        "/etc/postfix/maps.d",
        "/etc/postfix/postfix-files.d",
        "/etc/postfix/dynamicmaps.cf.d",
    ]
    directories.append(get_vars.get("postfix_config_directory"))

    for dirs in directories:
        d = host.file(dirs)
        assert d.is_directory


def test_files(host, get_vars):
    """
    created config files
    """
    files = [
        "/etc/postfix/main.cf",
        "/etc/postfix/maps.d/generic",
        "/etc/postfix/maps.d/generic.lmdb",
        "/etc/postfix/maps.d/header_checks",
        "/etc/postfix/maps.d/header_checks",
        "/etc/postfix/maps.d/recipient_canonical_maps",
        "/etc/postfix/maps.d/recipient_canonical_maps.lmdb",
        "/etc/postfix/maps.d/sasl_passwd",
        "/etc/postfix/maps.d/sasl_passwd.lmdb",
        "/etc/postfix/maps.d/sender_canonical_maps",
        "/etc/postfix/maps.d/sender_canonical_maps.lmdb",
        "/etc/postfix/maps.d/sender_dependent_relayhost_maps",
        "/etc/postfix/maps.d/sender_dependent_relayhost_maps.lmdb",
        "/etc/postfix/maps.d/transport_maps",
        "/etc/postfix/maps.d/transport_maps.lmdb",
        "/etc/postfix/maps.d/virtual",
        "/etc/postfix/master.cf",
    ]
    files.append(get_vars.get("postfix_mailname_file"))
    files.append(get_vars.get("postfix_aliases_file"))

    for _file in files:
        f = host.file(_file)
        assert f.is_file


def test_user(host, get_vars):
    """
    created user
    """
    shell = "/usr/sbin/nologin"

    distribution = host.system_info.distribution

    if distribution == "arch":
        shell = "/usr/bin/nologin"
    elif distribution == "artix":
        shell = "/bin/nologin"

    user_name = "postfix"
    u = host.user(user_name)
    g = host.group(user_name)

    assert g.exists
    assert u.exists
    assert user_name in u.groups
    assert u.shell == shell


def test_service_running_and_enabled(host, get_vars):
    """
    running service
    """
    service_name = "postfix"

    service = host.service(service_name)
    assert service.is_running
    assert service.is_enabled


def test_listening_socket(host, get_vars):
    """ """
    listening = host.socket.get_listening_sockets()
    interfaces = host.interface.names()
    eth = []

    if "eth0" in interfaces:
        eth = host.interface("eth0").addresses

    for i in listening:
        print(i)

    for i in interfaces:
        print(i)

    for i in eth:
        print(i)

    distribution = host.system_info.distribution
    release = host.system_info.release

    bind_address = eth[0]
    bind_port = 25
    socket_name = "private/smtp"

    listen = []
    listen.append(f"tcp://{bind_address}:{bind_port}")

    if not (distribution == "ubuntu" and release == "18.04"):
        listen.append(f"unix://{socket_name}")

    for spec in listen:
        socket = host.socket(spec)
        assert socket.is_listening
