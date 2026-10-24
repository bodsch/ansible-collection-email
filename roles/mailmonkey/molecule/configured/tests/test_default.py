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
        "/etc/mailmonkey",
        "/var/lib/mailmonkey",
        "/usr/local/opt/mailmonkey",
    ]

    for dirs in directories:
        d = host.file(dirs)
        assert d.is_directory


def test_files(host, get_vars):
    """
    created config files
    """
    files = [
        "/etc/mailmonkey/mailmonkey.yaml",
        "/etc/mailmonkey/acme.yaml",
        "/etc/mailmonkey/db-password",
        "/etc/mailmonkey/acme-db-password",
        "/usr/bin/mailmonkey",
        "/usr/bin/mailmonkey-acme",
        "/usr/lib/systemd/system/mailmonkey.service",
        "/usr/lib/systemd/system/mailmonkey-acme.service",
    ]

    for _file in files:
        f = host.file(_file)
        assert f.is_file


def test_mailmonkey_acme_user(host, get_vars):
    """
    created user
    """
    shell = "/usr/sbin/nologin"
    user_name = "mailmonkey-acme"
    u = host.user(user_name)
    g = host.group(user_name)

    assert g.exists
    assert u.exists
    assert user_name in u.groups
    assert u.shell == shell


def test_mailmonkey_user(host, get_vars):
    """
    created user
    """
    shell = "/usr/sbin/nologin"
    user_name = "mailmonkey"
    u = host.user(user_name)
    g = host.group(user_name)

    assert g.exists
    assert u.exists
    assert user_name in u.groups
    assert u.shell == shell


def test_service_mailmonkey(host, get_vars):
    """
    running service
    """
    service_name = "mailmonkey"

    service = host.service(service_name)
    assert service.is_running
    assert service.is_enabled


def test_service_mailmonkey_acme(host, get_vars):
    """
    running service
    """
    service_name = "mailmonkey-acme"

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

    listen = []
    listen.append("tcp://127.0.0.1:8080")
    listen.append("tcp://127.0.0.1:9110")
    listen.append("tcp://127.0.0.1:9111")

    for spec in listen:
        socket = host.socket(spec)
        assert socket.is_listening
