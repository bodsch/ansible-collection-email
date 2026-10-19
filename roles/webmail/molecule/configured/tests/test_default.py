# coding: utf-8
from __future__ import annotations, unicode_literals

import pytest
from helper.molecule import get_vars, infra_hosts, local_facts

testinfra_hosts = infra_hosts(host_name="instance")

# --- tests -----------------------------------------------------------------

# _facts = local_facts(host=host, fact="webmail")

def test_directories(host, get_vars):
    """ """
    directories = [
        "/etc/webmail",
        "/var/lib/webmail",
    ]
    # directories.append(get_vars.get("webmail_config_directory"))

    for dirs in directories:
        d = host.file(dirs)
        assert d.is_directory


def test_files(host, get_vars):
    """
    created config files
    """
    files = [
        "/etc/webmail/config.yaml",
        "/etc/default/webmail",
    ]

    for _file in files:
        f = host.file(_file)
        assert f.is_file


def test_user(host, get_vars):
    """
    created user
    """
    user_name = "webmail"
    u = host.user(user_name)
    g = host.group(user_name)
    shell = "/usr/bin/nologin"

    assert g.exists
    assert u.exists
    assert user_name in u.groups
    assert u.shell == shell


def test_service_running_and_enabled(host, get_vars):
    """
    running service
    """
    service_name = "webmail"

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
    listen.append("tcp://127.0.0.1:9109")

    for spec in listen:
        socket = host.socket(spec)
        assert socket.is_listening
