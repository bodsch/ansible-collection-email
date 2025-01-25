#!/usr/bin/python3
# -*- coding: utf-8 -*-

# (c) 2020, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
import os

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r"""
---
module: postfix_postmap
author: Bodo 'bodsch' Schulz <bodo@boone-schulz.de>
version_added: 1.0.0

short_description: TBD
description:
    - TBD

options:
  map_type:
    description:
      - (C(btree))
      - (C(cdb))
      - (C(dbm))
      - (C(fail))
      - (C(lmdb))
      - (C(sdbm))
    required: true
    default: lmdb

  filename:
    description: TBD
    required: true
    type: str
    type: bool
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

# ----------------------------------------------------------------------


class PostfixPostmap(object):
    """
      Main Class
    """
    module = None

    def __init__(self, module):
        """
          Initialize all needed Variables
        """
        self.module = module

        self._postmap = module.get_bin_path('postmap', True)
        self.map_type = module.params.get("map_type")
        self.filename = module.params.get("filename")

    def run(self):
        """
          runner
        """
        result = dict(
            rc=127,
            failed=True,
            changed=False,
        )

        if not os.path.exists(self.filename):
            return dict(
                failed=True,
                changed=False,
                msg=f"file {self.file_name} does not exists."
            )

        args = []
        args.append(self._postmap)
        args.append(f"{self.map_type}:{self.filename}")

        rc, out, err = self._exec(args)

        result['rc'] = rc

        if rc == 0:
            result['failed'] = False
            result['changed'] = True
            result['msg'] = out
        else:
            result['failed'] = True
            result['changed'] = False
            result['msg'] = err

        return result

    def _exec(self, cmd):
        """
        """
        rc, out, err = self.module.run_command(cmd, check_rc=True)

        return rc, out, err


# ===========================================
# Module execution.
#


def main():
    """
    """
    module = AnsibleModule(
        argument_spec=dict(
            map_type=dict(
                type="str",
                choices=["btree", "cdb", "dbm", "fail", "lmdb", "sdbm"],
                default="lmdb",
            ),
            filename=dict(
                required=True,
                type="str"
            ),
        ),
        supports_check_mode=True,
    )

    postmap = PostfixPostmap(module)
    result = postmap.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()

"""
COMMAND-LINE ARGUMENTS
       -b     Enable  message  body  query mode. When reading lookup keys from
              standard input with "-q -", process the input as  if  it  is  an
              email  message  in  RFC  5322 format.  Each line of body content
              becomes one lookup key.

              By default, the -b option starts generating lookup keys  at  the
              first  non-header line, and stops when the end of the message is
              reached.  To simulate  body_checks(5)  processing,  enable  MIME
              parsing   with  -m.  With  this,  the  -b  option  generates  no
              body-style lookup keys  for  attachment  MIME  headers  and  for
              attached message/* headers.

              NOTE: with "smtputf8_enable = yes", the -b option disables UTF-8
              syntax checks on query keys and lookup results. Specify  the  -U
              option to force UTF-8 syntax checks anyway.

              This feature is available in Postfix version 2.6 and later.

       -c config_dir
              Read  the  main.cf  configuration  file  in  the named directory
              instead of the default configuration directory.

       -d key Search the specified maps for key and remove one entry per  map.
              The  exit  status  is  zero  when  the requested information was
              found.

              If a key value of - is specified, the program reads  key  values
              from  the standard input stream. The exit status is zero when at
              least one of the requested keys was found.

       -f     Do not fold the lookup key  to  lower  case  while  creating  or
              querying a table.

              With  Postfix  version  2.3 and later, this option has no effect
              for regular expression tables. There, case folding is controlled
              by appending a flag to a pattern.

       -F     When querying a map, or listing a map, base64-decode each value.
              When creating a map from source file, process each  value  as  a
              list  of  filenames, concatenate the content of those files, and
              store the base64-encoded result instead of the value (see  INPUT
              FILE FORMAT for details).

              This feature is available in Postfix version 3.4 and later.

       -h     Enable  message header query mode. When reading lookup keys from
              standard input with "-q -", process the input as  if  it  is  an
              email  message  in  RFC  5322  format.  Each logical header line
              becomes one lookup key. A multi-line header becomes  one  lookup
              key with one or more embedded newline characters.

              By  default, the -h option generates lookup keys until the first
              non-header line is reached.  To simulate  header_checks(5)  pro-
              cessing,  enable  MIME parsing with -m. With this, the -h option
              also generates header-style  lookup  keys  for  attachment  MIME
              headers and for attached message/* headers.

              NOTE:  with  "smtputf8_enable  = yes", the -b option option dis-
              ables UTF-8 syntax checks on  query  keys  and  lookup  results.
              Specify the -U option to force UTF-8 syntax checks anyway.

              This feature is available in Postfix version 2.6 and later.

       -i     Incremental  mode.  Read  entries from standard input and do not
              truncate an existing database. By default, postmap(1) creates  a
              new database from the entries in file_name.

       -m     Enable MIME parsing with "-b" and "-h".

              This feature is available in Postfix version 2.6 and later.

       -N     Include  the  terminating  null character that terminates lookup
              keys and values. By default, postmap(1)  does  whatever  is  the
              default for the host operating system.

       -n     Don't  include  the  terminating  null character that terminates
              lookup keys and values. By default, postmap(1) does whatever  is
              the default for the host operating system.

       -o     Do  not release root privileges when processing a non-root input
              file. By default, postmap(1) drops root privileges and  runs  as
              the source file owner instead.

       -p     Do  not  inherit the file access permissions from the input file
              when creating a new file.   Instead,  create  a  new  file  with
              default access permissions (mode 0644).

       -q key Search  the  specified  maps  for  key and write the first value
              found to the standard output stream. The  exit  status  is  zero
              when the requested information was found.

              Note:  this  performs  a single query with the key as specified,
              and does not make iterative queries with substrings of  the  key
              as  described  for  access(5),  canonical(5), transport(5), vir-
              tual(5) and other Postfix table-driven features.

              If a key value of - is specified, the program reads  key  values
              from  the standard input stream and writes one line of key value
              output for each key that was found. The exit status is zero when
              at least one of the requested keys was found.

       -r     When  updating a table, do not complain about attempts to update
              existing entries, and make those updates anyway.

       -s     Retrieve all database elements, and write one line of key  value
              output  for  each  element. The elements are printed in database
              order, which is not necessarily the same as the  original  input
              order.

              This  feature is available in Postfix version 2.2 and later, and
              is not available for all database types.

       -u     Disable UTF-8 support. UTF-8 support is enabled by default  when
              "smtputf8_enable  =  yes".  It requires that keys and values are
              valid UTF-8 strings.

       -U     With "smtputf8_enable = yes", force UTF-8 syntax checks with the
              -b and -h options.

       -v     Enable  verbose  logging  for  debugging  purposes.  Multiple -v
              options make the software increasingly verbose.

       -w     When updating a table, do not complain about attempts to  update
              existing entries, and ignore those attempts.

       Arguments:

       file_type
              The database type. To find out what types are supported, use the
              "postconf -m" command.

              The postmap(1) command can query any supported file type, but it
              can create only the following file types:

              btree  The  output  file  is  a  btree file, named file_name.db.
                     This is available on systems with support  for  db  data-
                     bases.

              cdb    The  output  consists  of  one file, named file_name.cdb.
                     This is available on systems with support for  cdb  data-
                     bases.

              dbm    The output consists of two files, named file_name.pag and
                     file_name.dir.  This is available on systems with support
                     for dbm databases.

              fail   A  table that reliably fails all requests. The lookup ta-
                     ble name is used for logging only. This table  exists  to
                     simplify Postfix error tests.

              hash   The  output  file  is  a hashed file, named file_name.db.
                     This is available on systems with support  for  db  data-
                     bases.

              lmdb   The  output  is a btree-based file, named file_name.lmdb.
                     lmdb supports concurrent writes and reads from  different
                     processes,  unlike  other  supported  file-based  tables.
                     This is available on systems with support for lmdb  data-
                     bases.

              sdbm   The output consists of two files, named file_name.pag and
                     file_name.dir.  This is available on systems with support
                     for sdbm databases.

              When  no  file_type is specified, the software uses the database
              type  specified  via  the  default_database_type   configuration
              parameter.

       file_name
              The name of the lookup table source file when rebuilding a data-
              base.
"""
