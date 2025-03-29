
# Ansible Role:  `bodsch.email.mailcow`

Ansible role to install and configure [mailcow](https://github.com/mailcow/mailcow-dockerized) on various linux systems.

## usage 

```yaml
mailcow_version: latest

mailcow_source: git

mailcow_git:
  repository: https://github.com/mailcow/mailcow-dockerized
  version: master

mailcow_install_path: "/opt/mailcow"

mailcow_services:
  mailcow:
    state: stopped
    enabled: false
  mailcow-config:
    state: stopped
    enabled: true
  mailcow-pull:
    state: stopped
    enabled: true

mailcow_config:
  hostname: "{{ inventory_hostname }}"
  password_scheme: BLF-CRYPT
  timezone: Europe/Berlin
  compose:
    project_name: cow
    command: docker compose     # ['docker compose' or 'docker-compose']
  log_lines: 99

mailcow_tls_certificate:
  source_files:
    cert: ""
    ca: ""
    dh: ""
    key: ""

mailcow_database:
  schema_name: mailcow
  username: mailcow
  password: mailcow
  root_password: mailcow_root

mailcow_redis:
  password: redis

mailcow_bindings:
  http:
    address: "127.0.0.1"
    port: 80
  https:
    address: ""
    port: 443
  smtp:
    address: ""
    port: 25
  smtps:
    address: ""
    port: 465
  submission:
    address: ""
    port: 587
  imap:
    address: ""
    port: 143
  imaps:
    address: ""
    port: 993
  "pop":
    address: ""
    port: 110
  pops:
    address: ""
    port: 995
  sieve:
    address: ""
    port: 4190
  doveadm:
    address: 127.0.0.1
    port: 19991
  database:
    address: 127.0.0.1
    port: 13306
  redis:
    address: 127.0.0.1
    port: 7654

mailcow_san:
  additional_sans: []
  autodiscover: false

mailcow_additional_server_names: []

mailcow_lets_encrypt:
  enabled: false

mailcow_api:
  allow_from: []
  read_only: []
  key: ""

mailcow_sni:
  enabled: true

mailcow_ip_check:
  enabled: true

mailcow_http_verification:
  enabled: false

mailcow_unbound_healthcheck:
  enabled: true

mailcow_clamd:
  enabled: true

mailcow_sogo:
  enabled: false
  expire_session: 480

mailcow_fts:
  enabled: true
  heap_memory: 128  # MiB
  procs: 1

mailcow_network:
  ipv4: "172.22.1"
  ipv6: "fd4d:6169:6c63:6f77::/64"

mailcow_snat:
  ipv4:
    to_source: ""
  ipv6:
    to_source: ""

mailcow_dovecot:
  master_user: ""
  master_pass: ""

mailcow_acme:
  contact: ""

mailcow_spamhaus:
  dqs_key: ""

mailcow_watchdog:
  enabled: true
  notify:
    emails: []
    webhook: ""
    webhook_body: ""
    ban: true
    start: false
  subject: ""
  external_checks: false
  verbose: false

mailcow_maildir:
  home: "Maildir"
  gc_time: 60
  
mailcow_compose: {}

mailcow_compose_networks: []
mailcow_compose_services: []
mailcow_compose_volumes: []
```

### `mailcow_compose_networks`

```yaml
mailcow_compose_networks:
  - name: mailcow-network
    state: present
    driver: bridge
    driver_opts:
      com.docker.network.bridge.name: br-mailcow
    enable_ipv6: true
    ipam:
      driver: default
      config:
        - subnet: "{{ mailcow_network.ipv4 }}.0/24"
        - subnet: "{{ mailcow_network.ipv6 }}"
```


### `mailcow_compose_services`

```yaml
mailcow_compose_services:
  - name: unbound-mailcow
    image: mailcow/unbound:1.23
    environment:
      - TZ=${TZ}
      - SKIP_UNBOUND_HEALTHCHECK=${SKIP_UNBOUND_HEALTHCHECK:-n}
    volumes:
      - "{{ mailcow_install_path }}/active/data/hooks/unbound:/hooks:Z"
      - "{{ mailcow_install_path }}/active/data/conf/unbound/unbound.conf:/etc/unbound/unbound.conf:ro,Z"
    restart: unless-stopped
    tty: true
    networks:
      mailcow-network:
        ipv4_address: "{{ mailcow_network.ipv4 }}.254"
        aliases:
          - unbound

  - name: dockerapi-mailcow
    image: mailcow/dockerapi:2.10
    security_opt:
      - label=disable
    restart: unless-stopped
    dns:
      - "{{ mailcow_network.ipv4 }}.254"
    environment:
      - DBROOT=${DBROOT}
      - TZ=${TZ}
      - REDIS_SLAVEOF_IP=${REDIS_SLAVEOF_IP:-}
      - REDIS_SLAVEOF_PORT=${REDIS_SLAVEOF_PORT:-}
      - REDISPASS=${REDISPASS}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      mailcow-network:
        aliases:
          - dockerapi

  - name: mysql-mailcow
    image: mariadb:10.5
    depends_on:
      - dockerapi-mailcow
      - unbound-mailcow
      - netfilter-mailcow
    stop_grace_period: 45s
    volumes:
      - "{{ mailcow_install_path }}/mailcow-data/mysql-data:/var/lib/mysql/"
      - "{{ mailcow_install_path }}/mailcow-data/mysql-sock:/var/run/mysqld/"
      - "{{ mailcow_install_path }}/active/data/conf/mysql/:/etc/mysql/conf.d/:ro"
    environment:
      - TZ=${TZ}
      - MYSQL_ROOT_PASSWORD=${DBROOT}
      - MYSQL_DATABASE=${DBNAME}
      - MYSQL_USER=${DBUSER}
      - MYSQL_PASSWORD=${DBPASS}
      - MYSQL_INITDB_SKIP_TZINFO=1
    restart: unless-stopped
    ports:
      - "${SQL_PORT:-127.0.0.1:13306}:3306"
    networks:
      mailcow-network:
        aliases:
          - mysql

  - name: redis-mailcow
    image: redis:7-alpine
    entrypoint: /redis-conf.sh
    volumes:
      - "{{ mailcow_install_path }}/mailcow-data/redis-data:/data/"
      - "{{ mailcow_install_path }}/active/data/conf/redis/redis-conf.sh:/redis-conf.sh:z"
    restart: unless-stopped
    depends_on:
      - netfilter-mailcow
      - dockerapi-mailcow
    ports:
      - "${REDIS_PORT:-127.0.0.1:7654}:6379"
    environment:
      - TZ=${TZ}
      - REDISPASS=${REDISPASS}
    sysctls:
      - net.core.somaxconn=4096
    networks:
      mailcow-network:
        ipv4_address: "{{ mailcow_network.ipv4 }}.249"
        aliases:
          - redis

  - name: php-fpm-mailcow
    image: mailcow/phpfpm:1.92
    command: "php-fpm -d date.timezone=${TZ} -d expose_php=0"
    depends_on:
      - redis-mailcow
      - dockerapi-mailcow
    volumes:
      - "{{ mailcow_install_path }}/active/data/hooks/phpfpm:/hooks:Z"
      - "{{ mailcow_install_path }}/active/data/web:/web:z"
      - "{{ mailcow_install_path }}/active/data/conf/rspamd/dynmaps:/dynmaps:ro,z"
      - "{{ mailcow_install_path }}/active/data/conf/rspamd/custom/:/rspamd_custom_maps:z"
      - "{{ mailcow_install_path }}/mailcow-data/rspamd-data:/var/lib/rspamd"
      - "{{ mailcow_install_path }}/mailcow-data/mysql-sock:/var/run/mysqld/"
      - "{% if mailcow_sogo.enabled | default('false') | bool %}{{ mailcow_install_path }}/active/data/conf/sogo/:/etc/sogo/:z{% endif %}"
      - "{{ mailcow_install_path }}/active/data/conf/rspamd/meta_exporter:/meta_exporter:ro,z"
      - "{% if mailcow_sogo.enabled | default('false') | bool %}{{ mailcow_install_path }}/active/data/conf/phpfpm/sogo-sso/:/etc/sogo-sso/:z{% endif %}"
      - "{{ mailcow_install_path }}/active/data/conf/phpfpm/php-fpm.d/pools.conf:/usr/local/etc/php-fpm.d/z-pools.conf:Z"
      - "{{ mailcow_install_path }}/active/data/conf/phpfpm/php-conf.d/opcache-recommended.ini:/usr/local/etc/php/conf.d/opcache-recommended.ini:Z"
      - "{{ mailcow_install_path }}/active/data/conf/phpfpm/php-conf.d/upload.ini:/usr/local/etc/php/conf.d/upload.ini:Z"
      - "{{ mailcow_install_path }}/active/data/conf/phpfpm/php-conf.d/other.ini:/usr/local/etc/php/conf.d/zzz-other.ini:Z"
      - "{{ mailcow_install_path }}/active/data/conf/dovecot/global_sieve_before:/global_sieve/before:z"
      - "{{ mailcow_install_path }}/active/data/conf/dovecot/global_sieve_after:/global_sieve/after:z"
      - "{{ mailcow_install_path }}/active/data/assets/templates:/tpls:z"
      - "{{ mailcow_install_path }}/active/data/conf/nginx/:/etc/nginx/conf.d/:z"
    dns:
      - "{{ mailcow_network.ipv4 }}.254"
    environment:
      - REDIS_SLAVEOF_IP=${REDIS_SLAVEOF_IP:-}
      - REDIS_SLAVEOF_PORT=${REDIS_SLAVEOF_PORT:-}
      - REDISPASS=${REDISPASS}
      - LOG_LINES=${LOG_LINES:-9999}
      - TZ=${TZ}
      - DBNAME=${DBNAME}
      - DBUSER=${DBUSER}
      - DBPASS=${DBPASS}
      - MAILCOW_HOSTNAME=${MAILCOW_HOSTNAME}
      - MAILCOW_PASS_SCHEME=${MAILCOW_PASS_SCHEME:-BLF-CRYPT}
      - IMAP_PORT=${IMAP_PORT:-143}
      - IMAPS_PORT=${IMAPS_PORT:-993}
      - POP_PORT=${POP_PORT:-110}
      - POPS_PORT=${POPS_PORT:-995}
      - SIEVE_PORT=${SIEVE_PORT:-4190}
      - IPV4_NETWORK=${IPV4_NETWORK:-172.22.1}
      - IPV6_NETWORK=${IPV6_NETWORK:-fd4d:6169:6c63:6f77::/64}
      - SUBMISSION_PORT=${SUBMISSION_PORT:-587}
      - SMTPS_PORT=${SMTPS_PORT:-465}
      - SMTP_PORT=${SMTP_PORT:-25}
      - API_KEY=${API_KEY:-invalid}
      - API_KEY_READ_ONLY=${API_KEY_READ_ONLY:-invalid}
      - API_ALLOW_FROM=${API_ALLOW_FROM:-invalid}
      - COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME:-dockerized}
      - SKIP_FTS=${SKIP_FTS:-y}
      - SKIP_CLAMD=${SKIP_CLAMD:-n}
      - SKIP_SOGO=${SKIP_SOGO:-y}
      - ALLOW_ADMIN_EMAIL_LOGIN=${ALLOW_ADMIN_EMAIL_LOGIN:-n}
      - MASTER=${MASTER:-y}
      - DEV_MODE=${DEV_MODE:-n}
      - DEMO_MODE=${DEMO_MODE:-n}
      - WEBAUTHN_ONLY_TRUSTED_VENDORS=${WEBAUTHN_ONLY_TRUSTED_VENDORS:-n}
      - CLUSTERMODE=${CLUSTERMODE:-}
    restart: unless-stopped
    networks:
      mailcow-network:
        aliases:
          - phpfpm

  - name: clamd-mailcow
    hostname: clamd-mailcow
    image: mailcow/clamd:1.66
    restart: unless-stopped
    depends_on:
      unbound-mailcow:
        condition: service_healthy
    dns:
      - "{{ mailcow_network.ipv4 }}.254"
    environment:
      - TZ=${TZ}
      - SKIP_CLAMD=${SKIP_CLAMD:-n}
    volumes:
      - "{{ mailcow_install_path }}/active/data/conf/clamav/:/etc/clamav/:Z"
      - "{{ mailcow_install_path }}/mailcow-data/clamd-data:/var/lib/clamav"
    networks:
      mailcow-network:
        aliases:
          - clamd

  - name: rspamd-mailcow
    hostname: rspamd-mailcow
    image: mailcow/rspamd:1.99
    stop_grace_period: 30s
    depends_on:
      - dovecot-mailcow
      - clamd-mailcow
    environment:
      - TZ=${TZ}
      - IPV4_NETWORK=${IPV4_NETWORK:-172.22.1}
      - IPV6_NETWORK=${IPV6_NETWORK:-fd4d:6169:6c63:6f77::/64}
      - REDIS_SLAVEOF_IP=${REDIS_SLAVEOF_IP:-}
      - REDIS_SLAVEOF_PORT=${REDIS_SLAVEOF_PORT:-}
      - REDISPASS=${REDISPASS}
      - SPAMHAUS_DQS_KEY=${SPAMHAUS_DQS_KEY:-}
    volumes:
      - "{{ mailcow_install_path }}/active/data/hooks/rspamd:/hooks:Z"
      - "{{ mailcow_install_path }}/active/data/conf/rspamd/custom/:/etc/rspamd/custom:z"
      - "{{ mailcow_install_path }}/active/data/conf/rspamd/override.d/:/etc/rspamd/override.d:Z"
      - "{{ mailcow_install_path }}/active/data/conf/rspamd/local.d/:/etc/rspamd/local.d:Z"
      - "{{ mailcow_install_path }}/active/data/conf/rspamd/plugins.d/:/etc/rspamd/plugins.d:Z"
      - "{{ mailcow_install_path }}/active/data/conf/rspamd/lua/:/etc/rspamd/lua/:ro,Z"
      - "{{ mailcow_install_path }}/active/data/conf/rspamd/rspamd.conf.local:/etc/rspamd/rspamd.conf.local:Z"
      - "{{ mailcow_install_path }}/active/data/conf/rspamd/rspamd.conf.override:/etc/rspamd/rspamd.conf.override:Z"
      - "{{ mailcow_install_path }}/mailcow-data/rspamd-data:/var/lib/rspamd"
    restart: unless-stopped
    hostname: rspamd
    dns:
      - "{{ mailcow_network.ipv4 }}.254"
    networks:
      mailcow-network:
        aliases:
          - rspamd

  - name: dovecot-mailcow
    hostname: dovecot-mailcow
    image: mailcow/dovecot:2.3
    depends_on:
      - mysql-mailcow
      - netfilter-mailcow
      - redis-mailcow
    dns:
      - "{{ mailcow_network.ipv4 }}.254"
    cap_add:
      - NET_BIND_SERVICE
    volumes:
      - "{{ mailcow_install_path }}/active/data/hooks/dovecot:/hooks:Z"
      - "{{ mailcow_install_path }}/active/data/conf/dovecot:/etc/dovecot:z"
      - "{{ mailcow_install_path }}/active/data/assets/ssl:/etc/ssl/mail/:ro,z"
      - "{{ mailcow_install_path }}/active/data/conf/sogo/:/etc/sogo/:z"
      - "{{ mailcow_install_path }}/active/data/conf/phpfpm/sogo-sso/:/etc/phpfpm/:z"
      - "{{ mailcow_install_path }}/mailcow-data/vmail:/var/vmail"
      - "{{ mailcow_install_path }}/mailcow-data/vmail-index:/var/vmail_index"
      - "{{ mailcow_install_path }}/mailcow-data/crypt:/mail_crypt/"
      - "{{ mailcow_install_path }}/active/data/conf/rspamd/custom/:/etc/rspamd/custom:z"
      - "{{ mailcow_install_path }}/active/data/assets/templates:/templates:z"
      - "{{ mailcow_install_path }}/mailcow-data/rspamd-data:/var/lib/rspamd"
      - "{{ mailcow_install_path }}/mailcow-data/mysql-sock:/var/run/mysqld/"
    environment:
      - DOVECOT_MASTER_USER=${DOVECOT_MASTER_USER:-}
      - DOVECOT_MASTER_PASS=${DOVECOT_MASTER_PASS:-}
      - MAILCOW_REPLICA_IP=${MAILCOW_REPLICA_IP:-}
      - DOVEADM_REPLICA_PORT=${DOVEADM_REPLICA_PORT:-}
      - LOG_LINES=${LOG_LINES:-9999}
      - DBNAME=${DBNAME}
      - DBUSER=${DBUSER}
      - DBPASS=${DBPASS}
      - TZ=${TZ}
      - MAILCOW_HOSTNAME=${MAILCOW_HOSTNAME}
      - MAILCOW_PASS_SCHEME=${MAILCOW_PASS_SCHEME:-BLF-CRYPT}
      - IPV4_NETWORK=${IPV4_NETWORK:-172.22.1}
      - ALLOW_ADMIN_EMAIL_LOGIN=${ALLOW_ADMIN_EMAIL_LOGIN:-n}
      - MAILDIR_GC_TIME=${MAILDIR_GC_TIME:-7200}
      - ACL_ANYONE=${ACL_ANYONE:-disallow}
      - SKIP_FTS=${SKIP_FTS:-y}
      - FTS_HEAP=${FTS_HEAP:-512}
      - FTS_PROCS=${FTS_PROCS:-3}
      - MAILDIR_SUB=${MAILDIR_SUB:-}
      - MASTER=${MASTER:-y}
      - REDIS_SLAVEOF_IP=${REDIS_SLAVEOF_IP:-}
      - REDIS_SLAVEOF_PORT=${REDIS_SLAVEOF_PORT:-}
      - REDISPASS=${REDISPASS}
      - COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME:-dockerized}
    ports:
      - "${DOVEADM_PORT:-127.0.0.1:19991}:12345"
      - "${IMAP_PORT:-143}:143"
      - "${IMAPS_PORT:-993}:993"
      - "${POP_PORT:-110}:110"
      - "${POPS_PORT:-995}:995"
      - "${SIEVE_PORT:-4190}:4190"
    restart: unless-stopped
    tty: true
    labels:
      ofelia.enabled: "true"
      ofelia.job-exec.dovecot_imapsync_runner.schedule: "@every 1m"
      ofelia.job-exec.dovecot_imapsync_runner.no-overlap: "true"
      ofelia.job-exec.dovecot_imapsync_runner.command: "/bin/bash -c \"[[ $${MASTER} == y ]] && /usr/local/bin/gosu nobody /usr/local/bin/imapsync_runner.pl || exit 0\""
      ofelia.job-exec.dovecot_trim_logs.schedule: "@every 1m"
      ofelia.job-exec.dovecot_trim_logs.command: "/bin/bash -c \"[[ $${MASTER} == y ]] && /usr/local/bin/gosu vmail /usr/local/bin/trim_logs.sh || exit 0\""
      ofelia.job-exec.dovecot_quarantine.schedule: "@every 20m"
      ofelia.job-exec.dovecot_quarantine.command: "/bin/bash -c \"[[ $${MASTER} == y ]] && /usr/local/bin/gosu vmail /usr/local/bin/quarantine_notify.py || exit 0\""
      ofelia.job-exec.dovecot_clean_q_aged.schedule: "@every 24h"
      ofelia.job-exec.dovecot_clean_q_aged.command: "/bin/bash -c \"[[ $${MASTER} == y ]] && /usr/local/bin/gosu vmail /usr/local/bin/clean_q_aged.sh || exit 0\""
      ofelia.job-exec.dovecot_maildir_gc.schedule: "@every 30m"
      ofelia.job-exec.dovecot_maildir_gc.command: "/bin/bash -c \"source /source_env.sh ; /usr/local/bin/gosu vmail /usr/local/bin/maildir_gc.sh\""
      ofelia.job-exec.dovecot_sarules.schedule: "@every 24h"
      ofelia.job-exec.dovecot_sarules.command: "/bin/bash -c \"/usr/local/bin/sa-rules.sh\""
      ofelia.job-exec.dovecot_fts.schedule: "@every 24h"
      ofelia.job-exec.dovecot_fts.command: "/bin/bash -c \"/usr/local/bin/gosu vmail /usr/local/bin/optimize-fts.sh\""
      ofelia.job-exec.dovecot_repl_health.schedule: "@every 5m"
      ofelia.job-exec.dovecot_repl_health.command: "/bin/bash -c \"/usr/local/bin/gosu vmail /usr/local/bin/repl_health.sh\""
    ulimits:
      nproc: 65535
      nofile:
        soft: 20000
        hard: 40000
    networks:
      mailcow-network:
        ipv4_address: "{{ mailcow_network.ipv4 }}.250"
        aliases:
          - dovecot

  - name: postfix-mailcow
    image: mailcow/postfix:1.78
    depends_on:
      mysql-mailcow:
        condition: service_started
      unbound-mailcow:
        condition: service_healthy
    volumes:
      - "{{ mailcow_install_path }}/active/data/hooks/postfix:/hooks:Z"
      - "{{ mailcow_install_path }}/active/data/conf/postfix:/opt/postfix/conf:z"
      - "{{ mailcow_install_path }}/active/data/assets/ssl:/etc/ssl/mail/:ro,z"
      - "{{ mailcow_install_path }}/mailcow-data/postfix-data:/var/spool/postfix"
      - "{{ mailcow_install_path }}/mailcow-data/crypt:/var/lib/zeyple"
      - "{{ mailcow_install_path }}/mailcow-data/rspamd-data:/var/lib/rspamd"
      - "{{ mailcow_install_path }}/mailcow-data/mysql-sock:/var/run/mysqld/"
    environment:
      - LOG_LINES=${LOG_LINES:-9999}
      - TZ=${TZ}
      - DBNAME=${DBNAME}
      - DBUSER=${DBUSER}
      - DBPASS=${DBPASS}
      - REDIS_SLAVEOF_IP=${REDIS_SLAVEOF_IP:-}
      - REDIS_SLAVEOF_PORT=${REDIS_SLAVEOF_PORT:-}
      - REDISPASS=${REDISPASS}
      - MAILCOW_HOSTNAME=${MAILCOW_HOSTNAME}
      - SPAMHAUS_DQS_KEY=${SPAMHAUS_DQS_KEY:-}
    cap_add:
      - NET_BIND_SERVICE
    ports:
      - "${SMTP_PORT:-25}:25"
      - "${SMTPS_PORT:-465}:465"
      - "${SUBMISSION_PORT:-587}:587"
    restart: unless-stopped
    dns:
      - "{{ mailcow_network.ipv4 }}.254"
    networks:
      mailcow-network:
        ipv4_address: "{{ mailcow_network.ipv4 }}.253"
        aliases:
          - postfix

  - name: nginx-mailcow
    hostname: nginx-mailcow
    depends_on:
      - redis-mailcow
      - php-fpm-mailcow
      - rspamd-mailcow
    image: mailcow/nginx:1.01
    dns:
      - "{{ mailcow_network.ipv4 }}.254"
    environment:
      - HTTPS_PORT=${HTTPS_PORT:-443}
      - HTTP_PORT=${HTTP_PORT:-80}
      - MAILCOW_HOSTNAME=${MAILCOW_HOSTNAME}
      - ADDITIONAL_SERVER_NAMES=${ADDITIONAL_SERVER_NAMES:-}
      - TZ=${TZ}
      - SKIP_SOGO="Y"
      - SKIP_RSPAMD=${SKIP_RSPAMD:-n}
      - DISABLE_IPv6=${DISABLE_IPv6:-n}
      - PHPFPMHOST=${PHPFPMHOST:-php-fpm-mailcow}
      # - SOGOHOST=${SOGOHOST:-}
      - RSPAMDHOST=${RSPAMDHOST:-rspamd-mailcow}
      - REDISHOST=${REDISHOST:-redis-mailcow}
      - IPV4_NETWORK=${IPV4_NETWORK:-172.22.1}
    volumes:
      - "{{ mailcow_install_path }}/active/data/web:/web:ro,z"
      - "{{ mailcow_install_path }}/active/data/conf/rspamd/dynmaps:/dynmaps:ro,z"
      - "{{ mailcow_install_path }}/active/data/assets/ssl/:/etc/ssl/mail/:ro,z"
      - "{{ mailcow_install_path }}/active/data/conf/nginx/:/etc/nginx/conf.d/:z"
      - "{{ mailcow_install_path }}/active/data/conf/rspamd/meta_exporter:/meta_exporter:ro,z"
      # - "{{ mailcow_install_path }}/mailcow-data/sogo-data:/usr/lib/GNUstep/SOGo/"
    ports:
      - "${HTTPS_BIND:-}:${HTTPS_PORT:-443}:${HTTPS_PORT:-443}"
      - "${HTTP_BIND:-}:${HTTP_PORT:-80}:${HTTP_PORT:-80}"
    restart: unless-stopped
    networks:
      mailcow-network:
        aliases:
          - nginx

  - name: acme-mailcow
    hostname: acme-mailcow
    depends_on:
      nginx-mailcow:
        condition: service_started
      unbound-mailcow:
        condition: service_healthy
    image: mailcow/acme:1.91
    dns:
      - "{{ mailcow_network.ipv4 }}.254"
    environment:
      - LOG_LINES=${LOG_LINES:-9999}
      - ACME_CONTACT=${ACME_CONTACT:-}
      - ADDITIONAL_SAN=${ADDITIONAL_SAN}
      - AUTODISCOVER_SAN=${AUTODISCOVER_SAN:-y}
      - MAILCOW_HOSTNAME=${MAILCOW_HOSTNAME}
      - DBNAME=${DBNAME}
      - DBUSER=${DBUSER}
      - DBPASS=${DBPASS}
      - SKIP_LETS_ENCRYPT=${SKIP_LETS_ENCRYPT:-n}
      - COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME:-dockerized}
      - DIRECTORY_URL=${DIRECTORY_URL:-}
      - ENABLE_SSL_SNI=${ENABLE_SSL_SNI:-n}
      - SKIP_IP_CHECK=${SKIP_IP_CHECK:-n}
      - SKIP_HTTP_VERIFICATION=${SKIP_HTTP_VERIFICATION:-n}
      - ONLY_MAILCOW_HOSTNAME=${ONLY_MAILCOW_HOSTNAME:-n}
      - LE_STAGING=${LE_STAGING:-n}
      - TZ=${TZ}
      - REDIS_SLAVEOF_IP=${REDIS_SLAVEOF_IP:-}
      - REDIS_SLAVEOF_PORT=${REDIS_SLAVEOF_PORT:-}
      - REDISPASS=${REDISPASS}
      - SNAT_TO_SOURCE=${SNAT_TO_SOURCE:-n}
      - SNAT6_TO_SOURCE=${SNAT6_TO_SOURCE:-n}
    volumes:
      - "{{ mailcow_install_path }}/active/data/web/.well-known/acme-challenge:/var/www/acme:z"
      - "{{ mailcow_install_path }}/active/data/assets/ssl:/var/lib/acme/:z"
      - "{{ mailcow_install_path }}/active/data/assets/ssl-example:/var/lib/ssl-example/:ro,Z"
      - "{{ mailcow_install_path }}/mailcow-data/mysql-sock:/var/run/mysqld/"
    restart: unless-stopped
    networks:
      mailcow-network:
        aliases:
          - acme

  - name: netfilter-mailcow
    hostname: netfiler-mailcow
    image: mailcow/netfilter:1.60
    stop_grace_period: 30s
    restart: unless-stopped
    privileged: true
    environment:
      - TZ=${TZ}
      - IPV4_NETWORK=${IPV4_NETWORK:-172.22.1}
      - IPV6_NETWORK=${IPV6_NETWORK:-fd4d:6169:6c63:6f77::/64}
      - SNAT_TO_SOURCE=${SNAT_TO_SOURCE:-n}
      - SNAT6_TO_SOURCE=${SNAT6_TO_SOURCE:-n}
      - REDIS_SLAVEOF_IP=${REDIS_SLAVEOF_IP:-}
      - REDIS_SLAVEOF_PORT=${REDIS_SLAVEOF_PORT:-}
      - REDISPASS=${REDISPASS}
      - MAILCOW_REPLICA_IP=${MAILCOW_REPLICA_IP:-}
      - DISABLE_NETFILTER_ISOLATION_RULE=${DISABLE_NETFILTER_ISOLATION_RULE:-n}
    network_mode: "host"
    volumes:
      - /lib/modules:/lib/modules:ro

  - name: watchdog-mailcow
    hostname: watchdog-mailcow
    image: mailcow/watchdog:2.06
    dns:
      - "{{ mailcow_network.ipv4 }}.254"
    tmpfs:
      - /tmp
    volumes:
      - "{{ mailcow_install_path }}/mailcow-data/rspamd-data:/var/lib/rspamd"
      - "{{ mailcow_install_path }}/mailcow-data/mysql-sock:/var/run/mysqld/"
      - "{{ mailcow_install_path }}/mailcow-data/postfix-data:/var/spool/postfix"
      - "{{ mailcow_install_path }}/active/data/assets/ssl:/etc/ssl/mail/:ro,z"
    restart: unless-stopped
    depends_on:
      - postfix-mailcow
      - dovecot-mailcow
      - mysql-mailcow
      - acme-mailcow
      - redis-mailcow
    deploy:
      resources:
        limits:
          cpus: '0.1'
          memory: "20M"
        reservations:
          cpus: '0.1'
          memory: "6M"
    environment:
      - IPV6_NETWORK=${IPV6_NETWORK:-fd4d:6169:6c63:6f77::/64}
      - LOG_LINES=${LOG_LINES:-9999}
      - TZ=${TZ}
      - DBNAME=${DBNAME}
      - DBUSER=${DBUSER}
      - DBPASS=${DBPASS}
      - DBROOT=${DBROOT}
      - USE_WATCHDOG=${USE_WATCHDOG:-n}
      - WATCHDOG_NOTIFY_EMAIL=${WATCHDOG_NOTIFY_EMAIL:-}
      - WATCHDOG_NOTIFY_BAN=${WATCHDOG_NOTIFY_BAN:-y}
      - WATCHDOG_NOTIFY_START=${WATCHDOG_NOTIFY_START:-y}
      - WATCHDOG_SUBJECT=${WATCHDOG_SUBJECT:-Watchdog ALERT}
      - WATCHDOG_NOTIFY_WEBHOOK=${WATCHDOG_NOTIFY_WEBHOOK:-}
      - WATCHDOG_NOTIFY_WEBHOOK_BODY=${WATCHDOG_NOTIFY_WEBHOOK_BODY:-}
      - WATCHDOG_EXTERNAL_CHECKS=${WATCHDOG_EXTERNAL_CHECKS:-n}
      - WATCHDOG_MYSQL_REPLICATION_CHECKS=${WATCHDOG_MYSQL_REPLICATION_CHECKS:-n}
      - WATCHDOG_VERBOSE=${WATCHDOG_VERBOSE:-n}
      - MAILCOW_HOSTNAME=${MAILCOW_HOSTNAME}
      - COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME:-dockerized}
      - IPV4_NETWORK=${IPV4_NETWORK:-172.22.1}
      - IP_BY_DOCKER_API=${IP_BY_DOCKER_API:-0}
      - CHECK_UNBOUND=${CHECK_UNBOUND:-1}
      - SKIP_CLAMD=${SKIP_CLAMD:-n}
      - SKIP_LETS_ENCRYPT=${SKIP_LETS_ENCRYPT:-n}
      - SKIP_SOGO=${SKIP_SOGO:-n}
      - HTTPS_PORT=${HTTPS_PORT:-443}
      - REDIS_SLAVEOF_IP=${REDIS_SLAVEOF_IP:-}
      - REDIS_SLAVEOF_PORT=${REDIS_SLAVEOF_PORT:-}
      - REDISPASS=${REDISPASS}
      - EXTERNAL_CHECKS_THRESHOLD=${EXTERNAL_CHECKS_THRESHOLD:-1}
      - NGINX_THRESHOLD=${NGINX_THRESHOLD:-5}
      - UNBOUND_THRESHOLD=${UNBOUND_THRESHOLD:-5}
      - REDIS_THRESHOLD=${REDIS_THRESHOLD:-5}
      - MYSQL_THRESHOLD=${MYSQL_THRESHOLD:-5}
      - MYSQL_REPLICATION_THRESHOLD=${MYSQL_REPLICATION_THRESHOLD:-1}
      - SOGO_THRESHOLD=${SOGO_THRESHOLD:-3}
      - POSTFIX_THRESHOLD=${POSTFIX_THRESHOLD:-8}
      - CLAMD_THRESHOLD=${CLAMD_THRESHOLD:-15}
      - DOVECOT_THRESHOLD=${DOVECOT_THRESHOLD:-12}
      - DOVECOT_REPL_THRESHOLD=${DOVECOT_REPL_THRESHOLD:-20}
      - PHPFPM_THRESHOLD=${PHPFPM_THRESHOLD:-5}
      - RATELIMIT_THRESHOLD=${RATELIMIT_THRESHOLD:-1}
      - FAIL2BAN_THRESHOLD=${FAIL2BAN_THRESHOLD:-1}
      - ACME_THRESHOLD=${ACME_THRESHOLD:-1}
      - RSPAMD_THRESHOLD=${RSPAMD_THRESHOLD:-5}
      - OLEFY_THRESHOLD=${OLEFY_THRESHOLD:-5}
      - MAILQ_THRESHOLD=${MAILQ_THRESHOLD:-20}
      - MAILQ_CRIT=${MAILQ_CRIT:-30}
    networks:
      mailcow-network:
        aliases:
          - watchdog

  - name: olefy-mailcow
    hostname: olefy-mailcow
    image: mailcow/olefy:1.13
    restart: unless-stopped
    environment:
      - TZ=${TZ}
      - OLEFY_BINDADDRESS=0.0.0.0
      - OLEFY_BINDPORT=10055
      - OLEFY_TMPDIR=/tmp
      - OLEFY_PYTHON_PATH=/usr/bin/python3
      - OLEFY_OLEVBA_PATH=/usr/bin/olevba
      - OLEFY_LOGLVL=20
      - OLEFY_MINLENGTH=500
      - OLEFY_DEL_TMP=1
    networks:
      mailcow-network:
        aliases:
          - olefy

  - name: ofelia-mailcow
    hostname: ofelia-mailcow
    image: mcuadros/ofelia:latest
    restart: unless-stopped
    command: daemon --docker -f label=com.docker.compose.project=${COMPOSE_PROJECT_NAME}
    environment:
      - TZ=${TZ}
      - COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME}
    depends_on:
      - dovecot-mailcow
    labels:
      ofelia.enabled: "true"
    security_opt:
      - label=disable
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      mailcow-network:
        aliases:
          - ofelia

  - name: ipv6nat-mailcow
    hostname: ipv6nat-mailcow
    image: robbertkl/ipv6nat
    environment:
      - TZ=${TZ}
    security_opt:
      - label=disable
    restart: unless-stopped
    privileged: true
    network_mode: "host"
    depends_on:
      - unbound-mailcow
      - mysql-mailcow
      - redis-mailcow
      - clamd-mailcow
      - rspamd-mailcow
      - php-fpm-mailcow
      - dovecot-mailcow
      - postfix-mailcow
      - nginx-mailcow
      - acme-mailcow
      - netfilter-mailcow
      - watchdog-mailcow
      - dockerapi-mailcow
    deploy:
      resources:
        limits:
          cpus: '0.1'
          memory: "10M"
        reservations:
          cpus: '0.1'
          memory: "6M"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /lib/modules:/lib/modules:ro

  - name: sogo-mailcow
    state: absent
    image: mailcow/sogo:1.128
    environment:
      - DBNAME=${DBNAME}
      - DBUSER=${DBUSER}
      - DBPASS=${DBPASS}
      - TZ=${TZ}
      - LOG_LINES=${LOG_LINES:-9999}
      - MAILCOW_HOSTNAME=${MAILCOW_HOSTNAME}
      - MAILCOW_PASS_SCHEME=${MAILCOW_PASS_SCHEME:-BLF-CRYPT}
      - ACL_ANYONE=${ACL_ANYONE:-disallow}
      - ALLOW_ADMIN_EMAIL_LOGIN=${ALLOW_ADMIN_EMAIL_LOGIN:-n}
      - IPV4_NETWORK=${IPV4_NETWORK:-172.22.1}
      - SOGO_EXPIRE_SESSION=${SOGO_EXPIRE_SESSION:-480}
      - SKIP_SOGO=${SKIP_SOGO:-n}
      - MASTER=${MASTER:-y}
      - REDIS_SLAVEOF_IP=${REDIS_SLAVEOF_IP:-}
      - REDIS_SLAVEOF_PORT=${REDIS_SLAVEOF_PORT:-}
      - REDISPASS=${REDISPASS}
    dns:
      - ${IPV4_NETWORK:-172.22.1}.254
    volumes:
      - "{{ mailcow_install_path }}/active/data/hooks/sogo:/hooks:Z"
      - "{{ mailcow_install_path }}/active/data/conf/sogo/:/etc/sogo/:z"
      - "{{ mailcow_install_path }}/active/data/web/inc/init_db.inc.php:/init_db.inc.php:z"
      - "{{ mailcow_install_path }}/active/data/conf/sogo/custom-favicon.ico:/usr/lib/GNUstep/SOGo/WebServerResources/img/sogo.ico:z"
      - "{{ mailcow_install_path }}/active/data/conf/sogo/custom-theme.js:/usr/lib/GNUstep/SOGo/WebServerResources/js/theme.js:z"
      - "{{ mailcow_install_path }}/active/data/conf/sogo/custom-sogo.js:/usr/lib/GNUstep/SOGo/WebServerResources/js/custom-sogo.js:z"
      - "{{ mailcow_install_path }}/mailcow-data/mysql-sock:/var/run/mysqld/"
      - "{{ mailcow_install_path }}/mailcow-data/sogo-data:/sogo_web"
      - "{{ mailcow_install_path }}/mailcow-data/sogo-backup:/sogo_backup"
    labels:
      ofelia.enabled: "true"
      ofelia.job-exec.sogo_sessions.schedule: "@every 1m"
      ofelia.job-exec.sogo_sessions.command: "/bin/bash -c \"[[ $${MASTER} == y ]] && /usr/local/bin/gosu sogo /usr/sbin/sogo-tool -v expire-sessions $${SOGO_EXPIRE_SESSION} || exit 0\""
      ofelia.job-exec.sogo_ealarms.schedule: "@every 1m"
      ofelia.job-exec.sogo_ealarms.command: "/bin/bash -c \"[[ $${MASTER} == y ]] && /usr/local/bin/gosu sogo /usr/sbin/sogo-ealarms-notify -p /etc/sogo/cron.creds || exit 0\""
      ofelia.job-exec.sogo_eautoreply.schedule: "@every 5m"
      ofelia.job-exec.sogo_eautoreply.command: "/bin/bash -c \"[[ $${MASTER} == y ]] && /usr/local/bin/gosu sogo /usr/sbin/sogo-tool update-autoreply -p /etc/sogo/cron.creds || exit 0\""
      ofelia.job-exec.sogo_backup.schedule: "@every 24h"
      ofelia.job-exec.sogo_backup.command: "/bin/bash -c \"[[ $${MASTER} == y ]] && /usr/local/bin/gosu sogo /usr/sbin/sogo-tool backup /sogo_backup ALL || exit 0\""
    restart: unless-stopped
    networks:
      mailcow-network:
        ipv4_address: ${IPV4_NETWORK:-172.22.1}.248
        aliases:
          - sogo

  - name: memcached-mailcow
    state: absent
    image: memcached:alpine
    restart: unless-stopped
    environment:
      - TZ=${TZ}
    networks:
      mailcow-network:
        aliases:
          - memcached
```


## Requirements & Dependencies

Installed docker.  
For example the collection [bodsch.docker](https://github.com/bodsch/ansible-collection-docker)

---

## Contribution

Please read [Contribution](CONTRIBUTING.md)

## Development,  Branches (Git Tags)

## Author

- Bodo Schulz

## License

[Apache](LICENSE)

**FREE SOFTWARE, HELL YEAH!**
