-- MariaDB dump 10.19  Distrib 10.5.23-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: mailcow
-- ------------------------------------------------------
-- Server version       10.5.23-MariaDB-1:10.5.23+maria~ubu2004

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin` (
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `superadmin` tinyint(1) NOT NULL DEFAULT 0,
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  `modified` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  `active` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alias`
--

DROP TABLE IF EXISTS `alias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alias` (
  `address` varchar(255) NOT NULL,
  `goto` text NOT NULL,
  `domain` varchar(255) NOT NULL,
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  `modified` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  `active` tinyint(1) NOT NULL DEFAULT 1,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `private_comment` text DEFAULT NULL,
  `public_comment` text DEFAULT NULL,
  `sogo_visible` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `address` (`address`),
  KEY `domain` (`domain`)
) ENGINE=InnoDB AUTO_INCREMENT=142 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alias_domain`
--

DROP TABLE IF EXISTS `alias_domain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alias_domain` (
  `alias_domain` varchar(255) NOT NULL,
  `target_domain` varchar(255) NOT NULL,
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  `modified` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  `active` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`alias_domain`),
  KEY `active` (`active`),
  KEY `target_domain` (`target_domain`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `api`
--

DROP TABLE IF EXISTS `api`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `api` (
  `api_key` varchar(255) NOT NULL,
  `allow_from` varchar(512) NOT NULL,
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  `modified` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  `active` tinyint(1) NOT NULL DEFAULT 1,
  `skip_ip_check` tinyint(1) NOT NULL DEFAULT 0,
  `access` enum('ro','rw') NOT NULL DEFAULT 'rw',
  PRIMARY KEY (`api_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `app_passwd`
--

DROP TABLE IF EXISTS `app_passwd`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `app_passwd` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `mailbox` varchar(255) NOT NULL,
  `domain` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  `modified` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  `active` tinyint(1) NOT NULL DEFAULT 1,
  `imap_access` tinyint(1) NOT NULL DEFAULT 1,
  `smtp_access` tinyint(1) NOT NULL DEFAULT 1,
  `dav_access` tinyint(1) NOT NULL DEFAULT 1,
  `eas_access` tinyint(1) NOT NULL DEFAULT 1,
  `pop3_access` tinyint(1) NOT NULL DEFAULT 1,
  `sieve_access` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `mailbox` (`mailbox`),
  KEY `password` (`password`),
  KEY `domain` (`domain`),
  CONSTRAINT `fk_username_app_passwd` FOREIGN KEY (`mailbox`) REFERENCES `mailbox` (`username`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bcc_maps`
--

DROP TABLE IF EXISTS `bcc_maps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bcc_maps` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `local_dest` varchar(255) NOT NULL,
  `bcc_dest` varchar(255) NOT NULL,
  `domain` varchar(255) NOT NULL,
  `type` enum('sender','rcpt') DEFAULT NULL,
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  `modified` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  `active` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `local_dest` (`local_dest`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `da_acl`
--

DROP TABLE IF EXISTS `da_acl`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `da_acl` (
  `username` varchar(255) NOT NULL,
  `syncjobs` tinyint(1) NOT NULL DEFAULT 1,
  `quarantine` tinyint(1) NOT NULL DEFAULT 1,
  `login_as` tinyint(1) NOT NULL DEFAULT 1,
  `bcc_maps` tinyint(1) NOT NULL DEFAULT 1,
  `filters` tinyint(1) NOT NULL DEFAULT 1,
  `ratelimit` tinyint(1) NOT NULL DEFAULT 1,
  `spam_policy` tinyint(1) NOT NULL DEFAULT 1,
  `alias_domains` tinyint(1) NOT NULL DEFAULT 0,
  `unlimited_quota` tinyint(1) NOT NULL DEFAULT 0,
  `extend_sender_acl` tinyint(1) NOT NULL DEFAULT 0,
  `sogo_access` tinyint(1) NOT NULL DEFAULT 1,
  `app_passwds` tinyint(1) NOT NULL DEFAULT 1,
  `pushover` tinyint(1) NOT NULL DEFAULT 0,
  `domain_desc` tinyint(1) NOT NULL DEFAULT 0,
  `protocol_access` tinyint(1) NOT NULL DEFAULT 1,
  `smtp_ip_access` tinyint(1) NOT NULL DEFAULT 1,
  `mailbox_relayhost` tinyint(1) NOT NULL DEFAULT 1,
  `domain_relayhost` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `da_sso`
--

DROP TABLE IF EXISTS `da_sso`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `da_sso` (
  `username` varchar(255) NOT NULL,
  `token` varchar(255) NOT NULL,
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`token`,`created`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `domain`
--

DROP TABLE IF EXISTS `domain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `domain` (
  `domain` varchar(255) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `aliases` int(10) NOT NULL DEFAULT 0,
  `mailboxes` int(10) NOT NULL DEFAULT 0,
  `maxquota` bigint(20) NOT NULL DEFAULT 102400,
  `quota` bigint(20) NOT NULL DEFAULT 102400,
  `relayhost` varchar(255) NOT NULL DEFAULT '0',
  `backupmx` tinyint(1) NOT NULL DEFAULT 0,
  `relay_all_recipients` tinyint(1) NOT NULL DEFAULT 0,
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  `modified` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  `active` tinyint(1) NOT NULL DEFAULT 1,
  `gal` tinyint(1) NOT NULL DEFAULT 1,
  `defquota` bigint(20) NOT NULL DEFAULT 3072,
  `relay_unknown_only` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`domain`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `domain_admins`
--

DROP TABLE IF EXISTS `domain_admins`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `domain_admins` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `domain` varchar(255) NOT NULL,
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  `active` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `fido2`
--

DROP TABLE IF EXISTS `fido2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fido2` (
  `username` varchar(255) NOT NULL,
  `friendlyName` varchar(255) DEFAULT NULL,
  `rpId` varchar(255) NOT NULL,
  `credentialPublicKey` text NOT NULL,
  `certificateChain` text DEFAULT NULL,
  `certificate` text DEFAULT NULL,
  `certificateIssuer` varchar(255) DEFAULT NULL,
  `certificateSubject` varchar(255) DEFAULT NULL,
  `signatureCounter` int(11) DEFAULT NULL,
  `AAGUID` blob DEFAULT NULL,
  `credentialId` blob NOT NULL,
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  `modified` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  `active` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `filterconf`
--

DROP TABLE IF EXISTS `filterconf`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `filterconf` (
  `object` varchar(255) NOT NULL DEFAULT '',
  `option` varchar(50) NOT NULL DEFAULT '',
  `value` varchar(100) NOT NULL DEFAULT '',
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  `modified` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  `prefid` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`prefid`),
  KEY `object` (`object`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `forwarding_hosts`
--

DROP TABLE IF EXISTS `forwarding_hosts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `forwarding_hosts` (
  `host` varchar(255) NOT NULL,
  `source` varchar(255) NOT NULL,
  `filter_spam` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`host`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `grouped_domain_alias_address`
--

DROP TABLE IF EXISTS `grouped_domain_alias_address`;
/*!50001 DROP VIEW IF EXISTS `grouped_domain_alias_address`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `grouped_domain_alias_address` AS SELECT
 1 AS `username`,
  1 AS `ad_alias` */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `grouped_mail_aliases`
--

DROP TABLE IF EXISTS `grouped_mail_aliases`;
/*!50001 DROP VIEW IF EXISTS `grouped_mail_aliases`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `grouped_mail_aliases` AS SELECT
 1 AS `username`,
  1 AS `aliases` */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `grouped_sender_acl`
--

DROP TABLE IF EXISTS `grouped_sender_acl`;
/*!50001 DROP VIEW IF EXISTS `grouped_sender_acl`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `grouped_sender_acl` AS SELECT
 1 AS `username`,
  1 AS `send_as_acl` */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `grouped_sender_acl_external`
--

DROP TABLE IF EXISTS `grouped_sender_acl_external`;
/*!50001 DROP VIEW IF EXISTS `grouped_sender_acl_external`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `grouped_sender_acl_external` AS SELECT
 1 AS `username`,
  1 AS `send_as_acl` */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `imapsync`
--

DROP TABLE IF EXISTS `imapsync`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `imapsync` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user2` varchar(255) NOT NULL,
  `host1` varchar(255) NOT NULL,
  `authmech1` enum('PLAIN','LOGIN','CRAM-MD5') DEFAULT 'PLAIN',
  `regextrans2` varchar(255) DEFAULT '',
  `authmd51` tinyint(1) NOT NULL DEFAULT 0,
  `domain2` varchar(255) NOT NULL DEFAULT '',
  `subfolder2` varchar(255) NOT NULL DEFAULT '',
  `user1` varchar(255) NOT NULL,
  `password1` varchar(255) NOT NULL,
  `exclude` varchar(500) NOT NULL DEFAULT '',
  `maxage` smallint(6) NOT NULL DEFAULT 0,
  `mins_interval` smallint(5) unsigned NOT NULL DEFAULT 0,
  `maxbytespersecond` varchar(50) NOT NULL DEFAULT '0',
  `port1` smallint(5) unsigned NOT NULL,
  `enc1` enum('TLS','SSL','PLAIN') DEFAULT 'TLS',
  `delete2duplicates` tinyint(1) NOT NULL DEFAULT 1,
  `delete1` tinyint(1) NOT NULL DEFAULT 0,
  `delete2` tinyint(1) NOT NULL DEFAULT 0,
  `automap` tinyint(1) NOT NULL DEFAULT 0,
  `skipcrossduplicates` tinyint(1) NOT NULL DEFAULT 0,
  `is_running` tinyint(1) NOT NULL DEFAULT 0,
  `returned_text` longtext DEFAULT NULL,
  `last_run` timestamp NULL DEFAULT NULL,
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  `modified` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  `active` tinyint(1) NOT NULL DEFAULT 0,
  `custom_params` varchar(512) NOT NULL DEFAULT '',
  `timeout1` smallint(6) NOT NULL DEFAULT 600,
  `timeout2` smallint(6) NOT NULL DEFAULT 600,
  `subscribeall` tinyint(1) NOT NULL DEFAULT 1,
  `success` tinyint(1) unsigned DEFAULT NULL,
  `exit_status` varchar(50) DEFAULT NULL,
  `dry` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `logs`
--

DROP TABLE IF EXISTS `logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `task` char(32) NOT NULL DEFAULT '000000',
  `type` varchar(32) DEFAULT '',
  `msg` text DEFAULT NULL,
  `call` text DEFAULT NULL,
  `user` varchar(64) NOT NULL,
  `role` varchar(32) NOT NULL,
  `remote` varchar(39) NOT NULL,
  `time` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=695 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mailbox`
--

DROP TABLE IF EXISTS `mailbox`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mailbox` (
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `quota` bigint(20) NOT NULL DEFAULT 102400,
  `local_part` varchar(255) NOT NULL,
  `domain` varchar(255) NOT NULL,
  `attributes` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`attributes`)),
  `kind` varchar(100) NOT NULL DEFAULT '',
  `multiple_bookings` int(11) NOT NULL DEFAULT -1,
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  `modified` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  `active` tinyint(1) NOT NULL DEFAULT 1,
  `mailbox_path_prefix` varchar(150) DEFAULT '/var/vmail/',
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`username`),
  KEY `domain` (`domain`),
  KEY `kind` (`kind`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `oauth_access_tokens`
--

DROP TABLE IF EXISTS `oauth_access_tokens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oauth_access_tokens` (
  `access_token` varchar(40) NOT NULL,
  `client_id` varchar(80) NOT NULL,
  `user_id` varchar(80) DEFAULT NULL,
  `expires` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `scope` varchar(4000) DEFAULT NULL,
  PRIMARY KEY (`access_token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `oauth_authorization_codes`
--

DROP TABLE IF EXISTS `oauth_authorization_codes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oauth_authorization_codes` (
  `authorization_code` varchar(40) NOT NULL,
  `client_id` varchar(80) NOT NULL,
  `user_id` varchar(80) DEFAULT NULL,
  `redirect_uri` varchar(2000) DEFAULT NULL,
  `expires` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `scope` varchar(4000) DEFAULT NULL,
  `id_token` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`authorization_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `oauth_clients`
--

DROP TABLE IF EXISTS `oauth_clients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oauth_clients` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `client_id` varchar(80) NOT NULL,
  `client_secret` varchar(80) DEFAULT NULL,
  `redirect_uri` varchar(2000) DEFAULT NULL,
  `grant_types` varchar(80) DEFAULT NULL,
  `scope` varchar(4000) DEFAULT NULL,
  `user_id` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`client_id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `oauth_refresh_tokens`
--

DROP TABLE IF EXISTS `oauth_refresh_tokens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oauth_refresh_tokens` (
  `refresh_token` varchar(40) NOT NULL,
  `client_id` varchar(80) NOT NULL,
  `user_id` varchar(80) DEFAULT NULL,
  `expires` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `scope` varchar(4000) DEFAULT NULL,
  PRIMARY KEY (`refresh_token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pushover`
--

DROP TABLE IF EXISTS `pushover`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pushover` (
  `username` varchar(255) NOT NULL,
  `key` varchar(255) NOT NULL,
  `token` varchar(255) NOT NULL,
  `title` text DEFAULT NULL,
  `text` text DEFAULT NULL,
  `active` tinyint(1) NOT NULL DEFAULT 1,
  `attributes` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`attributes`)),
  `senders` text DEFAULT NULL,
  `senders_regex` text DEFAULT NULL,
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quarantine`
--

DROP TABLE IF EXISTS `quarantine`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quarantine` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `qid` varchar(30) NOT NULL,
  `score` float(8,2) DEFAULT NULL,
  `ip` varchar(50) DEFAULT NULL,
  `action` char(20) NOT NULL DEFAULT 'unknown',
  `symbols` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`symbols`)),
  `sender` varchar(255) NOT NULL DEFAULT 'unknown',
  `rcpt` varchar(255) DEFAULT NULL,
  `msg` longtext DEFAULT NULL,
  `domain` varchar(255) DEFAULT NULL,
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  `user` varchar(255) NOT NULL DEFAULT 'unknown',
  `subject` varchar(500) DEFAULT NULL,
  `notified` tinyint(1) NOT NULL DEFAULT 0,
  `fuzzy_hashes` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`fuzzy_hashes`)),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2873 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quota2`
--

DROP TABLE IF EXISTS `quota2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quota2` (
  `username` varchar(255) NOT NULL,
  `bytes` bigint(20) NOT NULL DEFAULT 0,
  `messages` bigint(20) NOT NULL DEFAULT 0,
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quota2replica`
--

DROP TABLE IF EXISTS `quota2replica`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quota2replica` (
  `username` varchar(255) NOT NULL,
  `bytes` bigint(20) NOT NULL DEFAULT 0,
  `messages` bigint(20) NOT NULL DEFAULT 0,
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `recipient_maps`
--

DROP TABLE IF EXISTS `recipient_maps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recipient_maps` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `old_dest` varchar(255) NOT NULL,
  `new_dest` varchar(255) NOT NULL,
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  `modified` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  `active` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `local_dest` (`old_dest`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `relayhosts`
--

DROP TABLE IF EXISTS `relayhosts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `relayhosts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `hostname` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `active` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `hostname` (`hostname`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sasl_log`
--

DROP TABLE IF EXISTS `sasl_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sasl_log` (
  `service` varchar(32) NOT NULL DEFAULT '',
  `app_password` int(11) DEFAULT NULL,
  `username` varchar(255) NOT NULL,
  `real_rip` varchar(64) NOT NULL,
  `datetime` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`service`,`real_rip`,`username`),
  KEY `username` (`username`),
  KEY `service` (`service`),
  KEY `datetime` (`datetime`),
  KEY `real_rip` (`real_rip`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sasl_logs`
--

DROP TABLE IF EXISTS `sasl_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sasl_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `success` tinyint(1) NOT NULL DEFAULT 0,
  `service` varchar(32) NOT NULL DEFAULT '',
  `app_password` int(11) DEFAULT NULL,
  `username` varchar(255) NOT NULL,
  `real_rip` varchar(64) NOT NULL,
  `datetime` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `username` (`username`),
  KEY `service` (`service`),
  KEY `success` (`success`),
  KEY `datetime` (`datetime`),
  KEY `real_rip` (`real_rip`)
) ENGINE=InnoDB AUTO_INCREMENT=18333 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sender_acl`
--

DROP TABLE IF EXISTS `sender_acl`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sender_acl` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `logged_in_as` varchar(255) NOT NULL,
  `send_as` varchar(255) NOT NULL,
  `external` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `settingsmap`
--

DROP TABLE IF EXISTS `settingsmap`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `settingsmap` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `desc` varchar(255) NOT NULL,
  `content` longtext NOT NULL,
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  `modified` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  `active` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `sieve_after`
--

DROP TABLE IF EXISTS `sieve_after`;
/*!50001 DROP VIEW IF EXISTS `sieve_after`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `sieve_after` AS SELECT
 1 AS `id`,
  1 AS `username`,
  1 AS `script_name`,
  1 AS `script_data` */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `sieve_before`
--

DROP TABLE IF EXISTS `sieve_before`;
/*!50001 DROP VIEW IF EXISTS `sieve_before`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `sieve_before` AS SELECT
 1 AS `id`,
  1 AS `username`,
  1 AS `script_name`,
  1 AS `script_data` */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `sieve_filters`
--

DROP TABLE IF EXISTS `sieve_filters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sieve_filters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `script_desc` varchar(255) NOT NULL,
  `script_name` enum('active','inactive') DEFAULT NULL,
  `script_data` text NOT NULL,
  `filter_type` enum('postfilter','prefilter') DEFAULT NULL,
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  `modified` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `username` (`username`),
  KEY `script_desc` (`script_desc`),
  CONSTRAINT `fk_username_sieve_global_before` FOREIGN KEY (`username`) REFERENCES `mailbox` (`username`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `spamalias`
--

DROP TABLE IF EXISTS `spamalias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `spamalias` (
  `address` varchar(255) NOT NULL,
  `goto` text NOT NULL,
  `validity` int(11) DEFAULT NULL,
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  `modified` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (`address`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tags_domain`
--

DROP TABLE IF EXISTS `tags_domain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tags_domain` (
  `tag_name` varchar(255) NOT NULL,
  `domain` varchar(255) NOT NULL,
  UNIQUE KEY `tag_name` (`tag_name`,`domain`),
  KEY `fk_tags_domain` (`domain`),
  CONSTRAINT `fk_tags_domain` FOREIGN KEY (`domain`) REFERENCES `domain` (`domain`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tags_mailbox`
--

DROP TABLE IF EXISTS `tags_mailbox`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tags_mailbox` (
  `tag_name` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL,
  UNIQUE KEY `tag_name` (`tag_name`,`username`),
  KEY `fk_tags_mailbox` (`username`),
  CONSTRAINT `fk_tags_mailbox` FOREIGN KEY (`username`) REFERENCES `mailbox` (`username`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `templates`
--

DROP TABLE IF EXISTS `templates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `templates` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `template` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  `attributes` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`attributes`)),
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  `modified` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tfa`
--

DROP TABLE IF EXISTS `tfa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tfa` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `key_id` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL,
  `authmech` enum('yubi_otp','u2f','hotp','totp','webauthn') DEFAULT NULL,
  `secret` varchar(255) DEFAULT NULL,
  `keyHandle` varchar(1023) DEFAULT NULL,
  `publicKey` varchar(4096) DEFAULT NULL,
  `counter` int(11) NOT NULL DEFAULT 0,
  `certificate` text DEFAULT NULL,
  `active` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tls_policy_override`
--

DROP TABLE IF EXISTS `tls_policy_override`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tls_policy_override` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dest` varchar(255) NOT NULL,
  `policy` enum('none','may','encrypt','dane','dane-only','fingerprint','verify','secure') NOT NULL,
  `parameters` varchar(255) DEFAULT '',
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  `modified` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  `active` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `dest` (`dest`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `transports`
--

DROP TABLE IF EXISTS `transports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `transports` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `destination` varchar(255) NOT NULL,
  `nexthop` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL DEFAULT '',
  `password` varchar(255) NOT NULL DEFAULT '',
  `active` tinyint(1) NOT NULL DEFAULT 1,
  `is_mx_based` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `destination` (`destination`),
  KEY `nexthop` (`nexthop`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_acl`
--

DROP TABLE IF EXISTS `user_acl`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_acl` (
  `username` varchar(255) NOT NULL,
  `spam_alias` tinyint(1) NOT NULL DEFAULT 1,
  `tls_policy` tinyint(1) NOT NULL DEFAULT 1,
  `spam_score` tinyint(1) NOT NULL DEFAULT 1,
  `spam_policy` tinyint(1) NOT NULL DEFAULT 1,
  `delimiter_action` tinyint(1) NOT NULL DEFAULT 1,
  `syncjobs` tinyint(1) NOT NULL DEFAULT 0,
  `eas_reset` tinyint(1) NOT NULL DEFAULT 1,
  `quarantine` tinyint(1) NOT NULL DEFAULT 1,
  `sogo_profile_reset` tinyint(1) NOT NULL DEFAULT 0,
  `quarantine_attachments` tinyint(1) NOT NULL DEFAULT 1,
  `quarantine_notification` tinyint(1) NOT NULL DEFAULT 1,
  `app_passwds` tinyint(1) NOT NULL DEFAULT 1,
  `pushover` tinyint(1) NOT NULL DEFAULT 1,
  `quarantine_category` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`username`),
  CONSTRAINT `fk_username` FOREIGN KEY (`username`) REFERENCES `mailbox` (`username`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `versions`
--

DROP TABLE IF EXISTS `versions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `versions` (
  `application` varchar(255) NOT NULL,
  `version` varchar(100) NOT NULL,
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`application`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Final view structure for view `grouped_domain_alias_address`
--

/*!50001 DROP VIEW IF EXISTS `grouped_domain_alias_address`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`mailcow`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `grouped_domain_alias_address` AS select `mailbox`.`username` AS `username`,ifnull(group_concat(`mailbox`.`local_part`,'@',`alias_domain`.`alias_domain` separator ' '),'') AS `ad_alias` from (`mailbox` left join `alias_domain` on(`alias_domain`.`target_domain` = `mailbox`.`domain`)) group by `mailbox`.`username` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `grouped_mail_aliases`
--

/*!50001 DROP VIEW IF EXISTS `grouped_mail_aliases`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`mailcow`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `grouped_mail_aliases` AS select `alias`.`goto` AS `username`,ifnull(group_concat(`alias`.`address` order by `alias`.`address` ASC separator ' '),'') AS `aliases` from `alias` where `alias`.`address` <> `alias`.`goto` and `alias`.`active` = '1' and `alias`.`sogo_visible` = '1' and `alias`.`address`  not like '@%' group by `alias`.`goto` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `grouped_sender_acl`
--

/*!50001 DROP VIEW IF EXISTS `grouped_sender_acl`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`mailcow`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `grouped_sender_acl` AS select `sender_acl`.`logged_in_as` AS `username`,ifnull(group_concat(`sender_acl`.`send_as` separator ' '),'') AS `send_as_acl` from `sender_acl` where `sender_acl`.`send_as`  not like '@%' group by `sender_acl`.`logged_in_as` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `grouped_sender_acl_external`
--

/*!50001 DROP VIEW IF EXISTS `grouped_sender_acl_external`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`mailcow`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `grouped_sender_acl_external` AS select `sender_acl`.`logged_in_as` AS `username`,ifnull(group_concat(`sender_acl`.`send_as` separator ' '),'') AS `send_as_acl` from `sender_acl` where `sender_acl`.`send_as`  not like '@%' and `sender_acl`.`external` = '1' group by `sender_acl`.`logged_in_as` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `sieve_after`
--

/*!50001 DROP VIEW IF EXISTS `sieve_after`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`mailcow`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `sieve_after` AS select md5(`sieve_filters`.`script_data`) AS `id`,`sieve_filters`.`username` AS `username`,`sieve_filters`.`script_name` AS `script_name`,`sieve_filters`.`script_data` AS `script_data` from `sieve_filters` where `sieve_filters`.`filter_type` = 'postfilter' */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `sieve_before`
--

/*!50001 DROP VIEW IF EXISTS `sieve_before`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`mailcow`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `sieve_before` AS select md5(`sieve_filters`.`script_data`) AS `id`,`sieve_filters`.`username` AS `username`,`sieve_filters`.`script_name` AS `script_name`,`sieve_filters`.`script_data` AS `script_data` from `sieve_filters` where `sieve_filters`.`filter_type` = 'prefilter' */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `sogo_view`
--

/*!50001 DROP VIEW IF EXISTS `sogo_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`mailcow`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `sogo_view` AS select `mailbox`.`username` AS `c_uid`,`mailbox`.`domain` AS `domain`,`mailbox`.`username` AS `c_name`,if(json_unquote(json_value(`mailbox`.`attributes`,'$.force_pw_update')) = '0',if(json_unquote(json_value(`mailbox`.`attributes`,'$.sogo_access')) = 1,`mailbox`.`password`,'{SSHA256}A123A123A321A321A321B321B321B123B123B321B432F123E321123123321321'),'{SSHA256}A123A123A321A321A321B321B321B123B123B321B432F123E321123123321321') AS `c_password`,`mailbox`.`name` AS `c_cn`,`mailbox`.`username` AS `mail`,ifnull(group_concat(`ga`.`aliases` order by `ga`.`aliases` ASC separator ' '),'') AS `aliases`,ifnull(`gda`.`ad_alias`,'') AS `ad_aliases`,ifnull(`external_acl`.`send_as_acl`,'') AS `ext_acl`,`mailbox`.`kind` AS `kind`,`mailbox`.`multiple_bookings` AS `multiple_bookings` from (((`mailbox` left join `grouped_mail_aliases` `ga` on(`ga`.`username` regexp concat('(^|,)',`mailbox`.`username`,'($|,)'))) left join `grouped_domain_alias_address` `gda` on(`gda`.`username` = `mailbox`.`username`)) left join `grouped_sender_acl_external` `external_acl` on(`external_acl`.`username` = `mailbox`.`username`)) where `mailbox`.`active` = '1' group by `mailbox`.`username` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-08-26  6:23:08
