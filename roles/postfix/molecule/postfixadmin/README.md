# Postfix Admin


virtual_alias_maps                      = proxy:mysql:/etc/postfix/virtual/mysql/alias_maps.cf
```bash
cat alias_maps.cf 
# - virtual config

user     = postfix
password = 
hosts    = 127.0.0.1
dbname   = postfix
#
query = SELECT goto FROM alias WHERE address='%s' AND active = 1
```

virtual_mailbox_domains                 = proxy:mysql:/etc/postfix/virtual/mysql/domains_maps.cf
```bash
cat domains_maps.cf 
# - virtual config

user     = postfix
password = 
hosts    = 127.0.0.1
dbname   = postfix
#
query = SELECT domain FROM domain WHERE domain='%s' AND active = 1
```

smtpd_sender_login_maps                 = proxy:mysql:/etc/postfix/virtual/mysql/login_maps.cf
```bash
cat login_maps.cf 
# - virtual config

user     = postfix
password = 
hosts    = 127.0.0.1
dbname   = postfix
#
query = SELECT username AS allowedUser FROM mailbox WHERE username='%s' AND active = 1 UNION SELECT goto FROM alias WHERE address='%s' AND active = 1
```

virtual_mailbox_maps                    = proxy:mysql:/etc/postfix/virtual/mysql/mailbox_maps.cf
```bash
cat mailbox_maps.cf 
# - virtual config

user     = postfix
password = 
hosts    = 127.0.0.1
dbname   = postfix
#
query = SELECT maildir FROM mailbox WHERE username='%s' AND active = 1
```

