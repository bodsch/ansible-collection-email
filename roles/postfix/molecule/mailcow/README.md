# Mailcow

transport_maps = pcre:/opt/postfix/conf/custom_transport.pcre,
  pcre:/opt/postfix/conf/local_transport,
  proxy:mysql:/opt/postfix/conf/sql/mysql_relay_ne.cf,
  proxy:mysql:/opt/postfix/conf/sql/mysql_transport_maps.cf

smtp_tls_policy_maps = proxy:mysql:/opt/postfix/conf/sql/mysql_tls_policy_override_maps.cf

smtp_sasl_password_maps = proxy:mysql:/opt/postfix/conf/sql/mysql_sasl_passwd_maps_sender_dependent.cf

virtual_mailbox_maps = proxy:mysql:/opt/postfix/conf/sql/mysql_virtual_mailbox_maps.cf

recipient_canonical_maps = proxy:mysql:/opt/postfix/conf/sql/mysql_recipient_canonical_maps.cf

virtual_mailbox_domains = proxy:mysql:/opt/postfix/conf/sql/mysql_virtual_domains_maps.cf

virtual_alias_maps = proxy:mysql:/opt/postfix/conf/sql/mysql_virtual_alias_maps.cf,
  proxy:mysql:/opt/postfix/conf/sql/mysql_virtual_resource_maps.cf,
  proxy:mysql:/opt/postfix/conf/sql/mysql_virtual_spamalias_maps.cf,
  proxy:mysql:/opt/postfix/conf/sql/mysql_virtual_alias_domain_maps.cf

smtpd_sender_login_maps = proxy:mysql:/opt/postfix/conf/sql/mysql_virtual_sender_acl.cf

smtpd_recipient_restrictions = check_recipient_mx_access proxy:mysql:/opt/postfix/conf/sql/mysql_mbr_access_maps.cf,
  permit_sasl_authenticated,
  permit_mynetworks,
  check_recipient_access proxy:mysql:/opt/postfix/conf/sql/mysql_tls_enforce_in_policy.cf,
  reject_invalid_helo_hostname,
  reject_unauth_destination

sender_dependent_default_transport_maps = proxy:mysql:/opt/postfix/conf/sql/mysql_sender_dependent_default_transport_maps.cf

relay_domains = proxy:mysql:/opt/postfix/conf/sql/mysql_virtual_relay_domain_maps.cf
relay_recipient_maps = proxy:mysql:/opt/postfix/conf/sql/mysql_relay_recipient_maps.cf

proxy_read_maps = proxy:mysql:/opt/postfix/conf/sql/mysql_sasl_passwd_maps_transport_maps.cf,
  proxy:mysql:/opt/postfix/conf/sql/mysql_mbr_access_maps.cf,
  proxy:mysql:/opt/postfix/conf/sql/mysql_tls_enforce_in_policy.cf,
  $sender_dependent_default_transport_maps,
  $smtp_tls_policy_maps,
  $local_recipient_maps,
  $mydestination,
  $virtual_alias_maps,
  $virtual_alias_domains,
  $virtual_mailbox_maps,
  $virtual_mailbox_domains,
  $relay_recipient_maps,
  $relay_domains,
  $canonical_maps,
  $sender_canonical_maps,
  $sender_bcc_maps,
  $recipient_bcc_maps,
  $recipient_canonical_maps,
  $relocated_maps,
  $transport_maps,
  $mynetworks,
  $smtpd_sender_login_maps,
  $smtp_sasl_password_maps
  
