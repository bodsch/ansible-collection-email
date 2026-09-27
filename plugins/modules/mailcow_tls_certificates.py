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

short_description: TBD
description:
    - TBD

"""

EXAMPLES = r"""
"""

RETURN = r"""
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

        Note: the three copy_file() calls each overwrite `changed`, so only
        the result of the LAST one survives - a renewed cert.pem alone is
        reported as unchanged. ssl_ca is required by verify_source_files()
        but never copied. And the early return passes the verification flag
        straight into `failed`, so a failed verification is reported as
        failed=False.
        """
        failed = False
        changed = False
        msg = "module init."

        verify_sources, msg = self.verify_source_files()

        if not verify_sources:
            return dict(changed=False, failed=verify_sources, msg=msg)

        if len(self.destination) == 0:
            return dict(
                changed=False,
                failed=True,
                msg="The destination directory was not properly defined!",
            )

        result = self.create_destination_directory()

        if not result.get("failed", False):
            """
            cert file
            """
            changed, failed = self.copy_file(source=self.ssl_cert, dest="cert.pem")
            changed, failed = self.copy_file(source=self.ssl_key, dest="key.pem")
            changed, failed = self.copy_file(source=self.ssl_dh, dest="dhparams.pem")

            # changed, failed = self.copy_files()
            if changed:
                msg = "The certificate files have been copied successfully."
            else:
                msg = "The certificate files are up to date."

        return dict(failed=failed, changed=changed, msg=msg)

    def verify_source_files(self):
        """
        Check that the configured source files were given and exist.

        Returns (ok, msg). Note that the "were they all given" check only
        runs when fewer than three of the four files are set, so exactly
        three configured files pass without the fourth being reported.
        """
        missing = []

        if len(self.ssl_files) < 3:
            if not self.ssl_cert:
                missing.append("cert")
            if not self.ssl_key:
                missing.append("key")
            if not self.ssl_ca:
                missing.append("ca")
            if not self.ssl_dh:
                missing.append("dh")

        if len(missing) > 0:
            return (
                False,
                f"The source files were not specified completely! The following files are missing: {', '.join(missing)}",
            )

        for f in self.ssl_files:
            if not os.path.exists(f):
                missing.append(f)

        if len(missing) > 0:
            return False, f"The source file(s) does not exist: {', '.join(missing)}"

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

    def copy_files(self):
        """
        Copy every source file, keeping its own base name.

        Unused: run() calls copy_file() per file instead, because mailcow
        expects fixed names (cert.pem, key.pem, dhparams.pem).
        """
        changed = False
        failed = False

        for f in self.ssl_files:
            differ = True
            s = f
            d = os.path.join(self.destination, os.path.basename(f))

            if os.path.isfile(d):
                differ = self.verify(s, d)

            self.module.log(msg=f" - {s} -> {d}, differ: {differ}")

            if differ:
                shutil.copyfile(s, d)
                os.chmod(d, 0o0440)
                changed = True

        # for root, dirs, files in os.walk(self.destination):
        #     # shutil.chown(root, self.owner, self.group)
        #     for item in dirs:
        #         shutil.chown(os.path.join(root, item), self.owner, self.group)
        #     for item in files:
        #         shutil.chown(os.path.join(root, item), self.owner, self.group)

        return changed, failed

    def copy_file(self, source, dest=None):
        """
        Copy one source file to a fixed name in the destination directory.

        The file is only written when its content differs, so an unchanged
        certificate does not restart mailcow. The copy is set to mode 0440.

        Returns (changed, failed).
        """
        changed = False
        failed = False

        differ = True
        d = os.path.join(self.destination, dest)

        if os.path.isfile(d):
            differ = self.verify(source, d)

        self.module.log(msg=f" - {source} -> {d}, differ: {differ}")

        if differ:
            shutil.copyfile(source, d)
            os.chmod(d, 0o0440)
            changed = True

        return changed, failed

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
