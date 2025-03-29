
from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar

import json
import pytest
import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def pp_json(json_thing, sort=True, indents=2):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=indents))
    return None


def base_directory():
    """
    """
    cwd = os.getcwd()

    if 'group_vars' in os.listdir(cwd):
        directory = "../.."
        molecule_directory = "."
    else:
        directory = "."
        molecule_directory = f"molecule/{os.environ.get('MOLECULE_SCENARIO_NAME')}"

    return directory, molecule_directory


def read_ansible_yaml(file_name, role_name):
    """
    """
    read_file = None

    for e in ["yml", "yaml"]:
        test_file = f"{file_name}.{e}"
        if os.path.isfile(test_file):
            read_file = test_file
            break

    return f"file={read_file} name={role_name}"


@pytest.fixture()
def get_vars(host):
    """
        parse ansible variables
        - defaults/main.yml
        - vars/main.yml
        - vars/${DISTRIBUTION}.yaml
        - molecule/${MOLECULE_SCENARIO_NAME}/group_vars/all/vars.yml
    """
    base_dir, molecule_dir = base_directory()
    distribution = host.system_info.distribution
    operation_system = None

    if distribution in ['debian', 'ubuntu']:
        operation_system = "debian"
    elif distribution in ['arch', 'artix']:
        operation_system = f"{distribution}linux"

    # print(" -> {} / {}".format(distribution, os))
    # print(" -> {}".format(base_dir))

    file_defaults = read_ansible_yaml(f"{base_dir}/defaults/main", "role_defaults")
    file_vars = read_ansible_yaml(f"{base_dir}/vars/main", "role_vars")
    file_distibution = read_ansible_yaml(f"{base_dir}/vars/{operation_system}", "role_distibution")
    file_molecule = read_ansible_yaml(f"{molecule_dir}/group_vars/all/vars", "test_vars")
    # file_host_molecule = read_ansible_yaml("{}/host_vars/{}/vars".format(base_dir, HOST), "host_vars")

    defaults_vars = host.ansible("include_vars", file_defaults).get("ansible_facts").get("role_defaults")
    vars_vars = host.ansible("include_vars", file_vars).get("ansible_facts").get("role_vars")
    distibution_vars = host.ansible("include_vars", file_distibution).get("ansible_facts").get("role_distibution")
    molecule_vars = host.ansible("include_vars", file_molecule).get("ansible_facts").get("test_vars")
    # host_vars          = host.ansible("include_vars", file_host_molecule).get("ansible_facts").get("host_vars")

    ansible_vars = defaults_vars
    ansible_vars.update(vars_vars)
    ansible_vars.update(distibution_vars)
    ansible_vars.update(molecule_vars)
    # ansible_vars.update(host_vars)

    templar = Templar(loader=DataLoader(), variables=ansible_vars)
    result = templar.template(ansible_vars, fail_on_undefined=False)

    return result


def local_facts(host):
    """
      return local facts
    """
    local_fact = host.ansible("setup").get("ansible_facts").get("ansible_local")

    print(f"local_fact     : {local_fact}")

    if local_fact:
        return local_fact.get("mailcow", {})
    else:
        return dict()


def test_directories(host, get_vars):

    install_path = get_vars.get("mailcow_install_path")

    directories = [
        f"{install_path}/active/data",
        f"{install_path}/active/data/assets/ssl"
    ]

    for dirs in directories:
        d = host.file(dirs)
        assert d.is_directory


def test_files(host, get_vars):

    install_path = get_vars.get("mailcow_install_path")

    files = [
        f"{install_path}/active/docker-compose.yml",
        f"{install_path}/active/mailcow.conf",
        f"{install_path}/active/.env"
    ]

    for f in files:
        d = host.file(f)
        assert d.is_file


def test_service_running_and_enabled(host, get_vars):
    """
      running service
    """
    service_name = "mailcow"

    mailcow_service = get_vars.get("mailcow_services", {}).get(service_name, False)

    service = host.service(service_name)
    if mailcow_service.get("state") == "started":
        assert service.is_running
    if mailcow_service.get("enabled") == "true":
        assert service.is_enabled


def test_listening_socket(host, get_vars):
    """
    """
    listening = host.socket.get_listening_sockets()

    for i in listening:
        print(i)

    listen = [
        "tcp://0.0.0.0:110",
        "tcp://0.0.0.0:143",
        "tcp://0.0.0.0:993",
        "tcp://0.0.0.0:995",
    ]

    mailcow_service = get_vars.get("mailcow_services", {}).get("mailcow", False)

    for spec in listen:
        socket = host.socket(spec)
        if mailcow_service.get("state") == "started":
            assert socket.is_listening
