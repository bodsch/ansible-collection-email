
https://cubepath.com/docs/email-server/dkim-configuration-for-email-authentication

/usr/bin/opendkim: invalid option -- '-'
opendkim: usage: opendkim -p socketfile [options]
        -A              auto-restart
        -b modes        select operating modes
        -c canon        canonicalization to use when signing
        -d domlist      domains to sign
        -D              also sign subdomains
        -e name         extract configuration value and exit
        -f              don't fork-and-exit
        -F time         fixed timestamp to use when signing (test mode only)
        -g              do not walk SigningTable when loading config
        -G              force walk SigningTable when loading config
        -k keyfile      location of secret key file
        -l              log activity to system log
        -L limit        signature limit requirements
        -n              check configuration and exit
        -o hdrlist      list of headers to omit from signing
        -O              log activity to standard output (stdout)
        -P pidfile      file into which to write process ID
        -q              quarantine messages that fail to verify
        -Q              query test mode
        -r              require basic RFC5322 header compliance
        -s selector     selector to use when signing
        -S signalg      signature algorithm to use when signing
        -t testfile     evaluate RFC5322 message in "testfile"
        -T timeout      DNS timeout (seconds)
        -u userid       change to specified userid
        -v              increase verbosity during testing
        -V              print version number and terminate
        -W              "why?!" mode (log sign/verify decision logic)
        -x conffile     read configuration from conffile
