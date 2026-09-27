#!/usr/bin/python3

# (c) 2020-2024, Bodo Schulz <bodo@boone-schulz.de>
# Apache (see LICENSE or https://opensource.org/licenses/Apache-2.0)


# import grp
# import pwd
import hashlib
import os
import shutil

# from ansible.module_utils import distro
from ansible.module_utils.basic import AnsibleModule

# ----------------------------------------------------------------------


DOCUMENTATION = r"""
---
module: mailcow_tls_certificates
author: Bodo 'bodsch' Schulz <bodo@boone-schulz.de>
version_added: 1.0.0

short_description: Copy TLS certificates into the mailcow asset directory.
description:
    - >-
      Copies the certificate files into C(data/assets/ssl), where mailcow serves
      them as C(cert.pem), C(key.pem) and C(dhparams.pem).
    - >-
      A file is only written when its content differs, so an unchanged
      certificate does not restart mailcow. Every configured file is checked,
      so a single renewed file is enough to report a change and fire the
      handlers.
    - The copies are written with mode C(0440).
    - This module does not support check mode.

options:
  source:
    description:
      - The source files.
      - C(ssl_cert), C(ssl_key) and C(ssl_dh) are required - those are the files mailcow serves.
      - >-
        C(ssl_ca) is optional; a CA is normally part of the chain in cert.pem.
        When given it is copied as C(ca.pem).
    required: true
    type: dict
  destination:
    description: The mailcow asset directory to copy into.
    required: true
    type: path
"""

EXAMPLES = r"""
- name: copy tls certificates
  become: true
  bodsch.email.mailcow_tls_certificates:
    source:
      ssl_cert: /etc/letsencrypt/live/example.com/fullchain.pem
      ssl_key: /etc/letsencrypt/live/example.com/privkey.pem
      ssl_dh: /etc/ssl/dhparams.pem
    destination: /opt/mailcow-dockerized/data/assets/ssl/
  notify:
    - restart mailcow
"""

RETURN = r"""
changed:
    description: Whether at least one file was copied.
    returned: always
    type: bool
failed:
    description: Whether a source file was missing or a copy failed.
    returned: always
    type: bool
msg:
    description: What happened.
    returned: always
    type: str
    sample: The certificate files are up to date.
"""

# ----------------------------------------------------------------------


class MailcowTLSCerts:
    """
    Main Class
    """

    module = None

    def __init__(self, module):
        """
        Initialize all needed Variables
        """
        self.module = module
        self.source = module.params.get("source")
        self.destination = module.params.get("destination")
        # self.owner = module.params.get("owner")
        # self.group = module.params.get("group")

        self.ssl_cert = self.source.get("ssl_cert", None)
        self.ssl_key = self.source.get("ssl_key", None)
        self.ssl_ca = self.source.get("ssl_ca", None)
        self.ssl_dh = self.source.get("ssl_dh", None)

        self.ssl_files = []
        if self.ssl_cert:
            self.ssl_files.append(self.ssl_cert)
        if self.ssl_key:
            self.ssl_files.append(self.ssl_key)
        if self.ssl_ca:
            self.ssl_files.append(self.ssl_ca)
        if self.ssl_dh:
            self.ssl_files.append(self.ssl_dh)

    # def get_file_ownership(self, filename):
    #     return (
    #         pwd.getpwuid(os.stat(filename).st_uid).pw_name,
    #         grp.getgrgid(os.stat(filename).st_gid).gr_name
    #     )

    def run(self):
        """
        Verify the sources, create the destination and copy the files.

        Every configured file is copied; changed and failed are accumulated
        over all of them, so a single renewed file still reports changed and
        the handlers fire.
        """
        verified, msg = self.verify_source_files()

        if not verified:
            return dict(changed=False, failed=True, msg=msg)

        if len(self.destination) == 0:
            return dict(
                changed=False,
                failed=True,
                msg="The destination directory was not properly defined!",
            )

        result = self.create_destination_directory()

        if result.get("failed", False):
            return result

        changed = False
        failed = False

        for source, dest in self.destination_names().items():
            file_changed, file_failed = self.copy_file(source=source, dest=dest)
            # accumulate: one renewed file is enough to fire the handlers
            changed = changed or file_changed
            failed = failed or file_failed

        if failed:
            msg = "At least one certificate file could not be copied."
        elif changed:
            msg = "The certificate files have been copied successfully."
        else:
            msg = "The certificate files are up to date."

        return dict(failed=failed, changed=changed, msg=msg)

    def destination_names(self):
        """
        Map each configured source file to the name mailcow reads it under.

        mailcow serves cert.pem, key.pem and dhparams.pem from
        data/assets/ssl. A CA is normally part of the certificate chain in
        cert.pem; when one is configured separately it is copied as ca.pem
        so nothing is silently dropped.
        """
        names = {
            self.ssl_cert: "cert.pem",
            self.ssl_key: "key.pem",
            self.ssl_dh: "dhparams.pem",
            self.ssl_ca: "ca.pem",
        }

        return {source: dest for source, dest in names.items() if source}

    def verify_source_files(self):
        """
        Check that the required source files were given and exist.

        cert, key and dh are required - those are the three files mailcow
        serves. A CA is optional, it is normally part of the chain in
        cert.pem.

        Returns (ok, msg).
        """
        required = {
            "cert": self.ssl_cert,
            "key": self.ssl_key,
            "dh": self.ssl_dh,
        }

        missing = [name for name, value in required.items() if not value]

        if missing:
            return (
                False,
                "The source files were not specified completely! "
                f"The following files are missing: {', '.join(missing)}",
            )

        absent = [path for path in self.ssl_files if not os.path.exists(path)]

        if absent:
            return False, f"The source file(s) does not exist: {', '.join(absent)}"

        return True, ""

    def create_destination_directory(self):
        """
        Create the destination directory if it is not there yet.

        Returns a result mapping with failed / changed / msg.
        """
        if os.path.isdir(self.destination):
            return dict(
                failed=False,
                changed=False,
                msg=f"Directory {self.destination} already exists.",
            )

        # Create the directory
        try:
            os.makedirs(self.destination, exist_ok=True)
            msg = f"Directory '{self.destination}' created successfully."

            # shutil.chown(self.destination, self.owner, self.group)

            return dict(failed=False, changed=True, msg=msg)

        except OSError as error:
            msg = f"Directory '{self.destination}' can not be created. ({error})"

            return dict(failed=True, changed=False, msg=msg)

    def copy_file(self, source, dest=None):
        """
        Copy one source file to a fixed name in the destination directory.

        The file is only written when its content differs, so an unchanged
        certificate does not restart mailcow.

        The copy is written next to the target and moved into place, because
        the destination is left read only (0440) and could otherwise not be
        replaced by a renewed certificate.

        Returns (changed, failed).
        """
        target = os.path.join(self.destination, dest)

        differ = True
        if os.path.isfile(target):
            differ = self.verify(source, target)

        self.module.log(msg=f" - {source} -> {target}, differ: {differ}")

        if not differ:
            return False, False

        temporary = f"{target}.ansible_tmp"

        try:
            shutil.copyfile(source, temporary)
            os.chmod(temporary, 0o0440)
            os.replace(temporary, target)
        except OSError as error:
            if os.path.exists(temporary):
                os.unlink(temporary)
            self.module.log(msg=f"   copy failed: {error}")
            return False, True

        return True, False

    def verify(self, source_file, destination_file):
        """
        Say whether two files differ, by comparing their checksums.

        Returns False when either file is missing, so a missing source does
        not trigger a copy.
        """
        # self.module.log(msg=f"verify({source_file} : {destination_file})")
        s_checksum = None
        d_checksum = None

        if os.path.isfile(source_file):
            s_checksum = self.__create_checksum_file(source_file)

        if os.path.isfile(destination_file):
            d_checksum = self.__create_checksum_file(destination_file)

        # self.module.log(msg=f" - {s_checksum} : {d_checksum}")

        if s_checksum and d_checksum:
            return not (s_checksum == d_checksum)
        else:
            return False

    def __create_checksum_file(self, filename):
        """
        Checksum of a file's content, with the trailing newline stripped.

        Reads in text mode, which is fine for PEM but not for binary data.
        """
        with open(filename, "r") as d:
            _data = d.read().rstrip("\n")
            return self.__checksum(_data)

    def __checksum(self, plaintext):
        """
        SHA256 of a string, as hex.
        """
        _bytes = plaintext.encode("utf-8")
        _hash = hashlib.sha256(_bytes)
        return _hash.hexdigest()


def main():
    """
    Copy the TLS certificate files into the directory mailcow reads them
    from, and report whether anything changed.
    """
    specs = dict(
        source=dict(
            required=True,
            type="dict",
        ),
        destination=dict(required=True, type="path"),
    )

    module = AnsibleModule(
        argument_spec=specs,
        supports_check_mode=False,
    )

    helper = MailcowTLSCerts(module)
    result = helper.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == "__main__":
    main()
