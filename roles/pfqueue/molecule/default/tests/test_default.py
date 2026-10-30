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
        "/usr/local/opt/pfqueue",
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
        "/usr/bin/pfqueue",
    ]

    for _file in files:
        f = host.file(_file)
        assert f.is_file
