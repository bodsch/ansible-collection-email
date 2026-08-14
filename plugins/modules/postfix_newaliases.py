#!/usr/bin/python3
# -*- coding: utf-8 -*-

# (c) 2020, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function

from ansible.module_utils.basic import AnsibleModule

# ----------------------------------------------------------------------

DOCUMENTATION = r"""
---
module: postfix_newaliases
author: Bodo 'bodsch' Schulz <bodo@boone-schulz.de>
version_added: 1.0.0

short_description: TBD
description:
    - TBD

options:
  alias_database:
    description: TBD
    required: false
    type: str
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

# ----------------------------------------------------------------------


class PostfixNewaliases(object):
    """
    Main Class
    """

    module = None

    def __init__(self, module):
        """
        Initialize all needed Variables
        """
        self.module = module

        self._newaliases = module.get_bin_path("newaliases", True)
        self.alias_database = module.params.get("alias_database")

    def run(self):
        """
        runner
        """
        result = dict(
            rc=127,
            failed=True,
            changed=False,
        )

        args = []
        args.append(self._newaliases)

        if self.alias_database:
            args.append("-oA")
            args.append(self.alias_database)

        rc, out, err = self._exec(args)

        if rc == 0:
            result["failed"] = False
            result["changed"] = True
            result["msg"] = out
        else:
            result["failed"] = True
            result["changed"] = False
            result["msg"] = err

        return result

    def _exec(self, cmd):
        """ """
        rc, out, err = self.module.run_command(cmd, check_rc=True)

        return rc, out, err


# ===========================================
# Module execution.
#


def main():

    module = AnsibleModule(
        argument_spec=dict(
            alias_database=dict(
                required=False,
            )
        ),
        supports_check_mode=True,
    )

    newaliases = PostfixNewaliases(module)
    result = newaliases.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == "__main__":
    main()

"""
       The following options are recognized:

       -Am (ignored)

       -Ac (ignored)
              Postfix  sendmail uses the same configuration file regardless of
              whether or not a message is an initial submission.

       -B body_type
              The message body MIME type: 7BIT or 8BITMIME.

       -bd    Go into daemon mode. This mode of operation  is  implemented  by
              executing the "postfix start" command.

       -bh (ignored)

       -bH (ignored)
              Postfix has no persistent host status database.

       -bi    Initialize alias database. See the newaliases command above.

       -bl    Go  into  daemon  mode. To accept only local connections as with
              Sendmail's -bl option, specify "inet_interfaces =  loopback"  in
              the Postfix main.cf configuration file.

       -bm    Read mail from standard input and arrange for delivery.  This is
              the default mode of operation.

       -bp    List the mail queue. See the mailq command above.

       -bs    Stand-alone SMTP server mode. Read SMTP commands  from  standard
              input,  and  write responses to standard output.  In stand-alone
              SMTP server mode, mail relaying and other  access  controls  are
              disabled  by  default.  To  enable  them, run the process as the
              mail_owner user.

              This mode of operation is implemented by  running  the  smtpd(8)
              daemon.

       -bv    Do  not  collect  or  deliver  a message. Instead, send an email
              report after verifying each recipient address.  This  is  useful
              for testing address rewriting and routing configurations.

              This feature is available in Postfix version 2.1 and later.

       -C config_file

       -C config_dir
              The  path  name  of  the  Postfix main.cf file, or of its parent
              directory. This information is  ignored  with  Postfix  versions
              before 2.3.

              With Postfix version 3.2 and later, a non-default directory must
              be authorized in the default main.cf file,  through  the  alter-
              nate_config_directories  or  multi_instance_directories  parame-
              ters.

              With all Postfix versions, you can specify a directory  pathname
              with  the MAIL_CONFIG environment variable to override the loca-
              tion of configuration files.

       -F full_name
              Set the sender full name. This overrides  the  NAME  environment
              variable, and is used only with messages that have no From: mes-
              sage header.

       -f sender
              Set the envelope sender  address.  This  is  the  address  where
              delivery problems are sent to. With Postfix versions before 2.1,
              the  Errors-To:  message  header  overrides  the  error   return
              address.

       -G     Gateway  (relay)  submission, as opposed to initial user submis-
              sion.  Either do not rewrite addresses at all, or update  incom-
              plete  addresses  with  the  domain  information  specified with
              remote_header_rewrite_domain.

              This option is ignored before Postfix version 2.3.

       -h hop_count (ignored)
              Hop count limit. Use the hopcount_limit configuration  parameter
              instead.

       -I     Initialize alias database. See the newaliases command above.

       -i     When  reading  a message from standard input, don't treat a line
              with only a . character as the end of input.

       -L label (ignored)
              The logging label. Use the syslog_name  configuration  parameter
              instead.

       -m (ignored)
              Backwards compatibility.

       -N dsn (default: 'delay, failure')
              Delivery   status   notification   control.   Specify  either  a
              comma-separated list with one or more of failure (send notifica-
              tion  when delivery fails), delay (send notification when deliv-
              ery is delayed), or success (send notification when the  message
              is delivered); or specify never (don't send any notifications at
              all).

              This feature is available in Postfix 2.3 and later.

       -n (ignored)
              Backwards compatibility.

       -oAalias_database
              Non-default alias database. Specify pathname  or  type:pathname.
              See postalias(1) for details.

       -O option=value (ignored)
              Set  the named option to value. Use the equivalent configuration
              parameter in main.cf instead.

       -o7 (ignored)

       -o8 (ignored)
              To send 8-bit or binary content, use an appropriate MIME  encap-
              sulation and specify the appropriate -B command-line option.

       -oi    When  reading  a message from standard input, don't treat a line
              with only a . character as the end of input.

       -om (ignored)
              The sender is never eliminated from alias etc. expansions.

       -o x value (ignored)
              Set option x to value. Use the equivalent configuration  parame-
              ter in main.cf instead.

       -r sender
              Set  the  envelope  sender  address.  This  is the address where
              delivery problems are sent to. With Postfix versions before 2.1,
              the   Errors-To:  message  header  overrides  the  error  return
              address.

       -R return
              Delivery status notification control.  Specify "hdrs" to  return
              only  the header when a message bounces, "full" to return a full
              copy (the default behavior).

              The -R option specifies an upper bound; Postfix will return only
              the  header, when a full copy would exceed the bounce_size_limit
              setting.

              This option is ignored before Postfix version 2.10.

       -q     Attempt to deliver all queued mail. This is implemented by  exe-
              cuting the postqueue(1) command.

              Warning:  flushing  undeliverable mail frequently will result in
              poor delivery performance of all other mail.

       -qinterval (ignored)
              The interval between queue runs. Use the queue_run_delay config-
              uration parameter instead.

       -qIqueueid
              Schedule immediate delivery of mail with the specified queue ID.
              This option is implemented by executing  the  postqueue(1)  com-
              mand, and is available with Postfix version 2.4 and later.

       -qRsite
              Schedule  immediate  delivery of all mail that is queued for the
              named site. This option accepts only site names that are  eligi-
              ble  for the "fast flush" service, and is implemented by execut-
              ing the postqueue(1) command.  See flush(8) for more information
              about the "fast flush" service.

       -qSsite
              This  command  is  not implemented. Use the slower "sendmail -q"
              command instead.

       -t     Extract recipients from message headers. These are added to  any
              recipients specified on the command line.

              With Postfix versions prior to 2.1, this option requires that no
              recipient addresses are specified on the command line.

       -U (ignored)
              Initial user submission.

       -V envid
              Specify the envelope ID for notification by servers that support
              DSN.

              This feature is available in Postfix 2.3 and later.

       -XV (Postfix 2.2 and earlier: -V)
              Variable  Envelope Return Path. Given an envelope sender address
              of the form owner-listname@origin,  each  recipient  user@domain
              receives mail with a personalized envelope sender address.

              By   default,   the  personalized  envelope  sender  address  is
              owner-listname+user=domain@origin. The default + and  =  charac-
              ters  are configurable with the default_verp_delimiters configu-
              ration parameter.

       -XVxy (Postfix 2.2 and earlier: -Vxy)
              As -XV, but uses x and  y  as  the  VERP  delimiter  characters,
              instead of the characters specified with the default_verp_delim-
              iters configuration parameter.

       -v     Send an email report of the first delivery attempt (Postfix ver-
              sions  2.1 and later). Mail delivery always happens in the back-
              ground. When multiple -v options are given, enable verbose  log-
              ging for debugging purposes.

       -X log_file (ignored)
              Log mailer traffic. Use the debug_peer_list and debug_peer_level
              configuration parameters instead.
"""
