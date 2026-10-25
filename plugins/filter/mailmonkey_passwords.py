# python 3 headers, required if submitting to Ansible

from ansible.utils.display import Display

display = Display()


class FilterModule:
    """
    Expand the compact dovecot metric definitions into what 2.4 renders.
    """

    def filters(self):
        return {
            "mailmonkey_acme_passwords": self.mailmonkey_acme_passwords,
            "mailmonkey_config_passwords": self.mailmonkey_config_passwords,
        }

    def mailmonkey_acme_passwords(self, data):
        """ """
        display.vv(f"bodsch.email::mailmonkey_acme_passwords(data: {data})")

        _db = data.get("db", None)

        _password = _db.get("password", None)
        _password_file = _db.get("password_file", None)

        if _password and _password_file:
            pass
        elif not _password and _password_file:
            _ = data["db"].pop("password_file")
        elif _password and not _password_file:
            data["db"]["password_file"] = "/etc/mailmonkey/acme-db-password"

        display.vv(f" = result '{data}'")

        return data

    def mailmonkey_config_passwords(self, data):
        """ """
        display.vv(f"bodsch.email::mailmonkey_config_passwords('{data}')")

        _db = data.get("db", None)

        if _db:
            _db_password = _db.get("password", None)
            _db_password_file = _db.get("password_file", None)

            if _db_password and _db_password_file:
                """
                db.password and db.password_file are both set; use one or the other
                """
                _ = data["db"].pop("password")
            elif not _db_password and _db_password_file:
                _ = data["db"].pop("password_file")
            elif _db_password and not _db_password_file:
                _ = data["db"].pop("password")
                data["db"]["password_file"] = "/etc/mailmonkey/db-password"

        _totp = data.get("totp", None)

        if _totp:
            _totp_key = _totp.get("key", None)
            _totp_key_file = _totp.get("key_file", None)

            if _totp_key and _totp_key_file:
                pass
            elif not _totp_key and _totp_key_file:
                _ = data["totp"].pop("key_file")
            elif _totp_key and not _totp_key_file:
                _ = data["totp"].pop("key")
                data["totp"]["key_file"] = "/etc/mailmonkey/totp.key"
            elif not _totp_key and not _totp_key_file:
                data.pop("totp")

        _redis = data.get("redis", None)

        if _redis:
            _redis_password = _redis.get("password", None)
            _redis_password_file = _redis.get("password_file", None)

            if _redis_password and _redis_password_file:
                pass
            elif not _redis_password and _redis_password_file:
                _ = data["redis"].pop("password_file")
            elif _redis_password and not _redis_password_file:
                _ = data["redis"].pop("password")
                data["redis"]["password_file"] = "/etc/mailmonkey/redis-password"

        # _bootstrap = data.get("bootstrap", None)
        #
        # if _bootstrap:
        #     _bootstrap_password = _bootstrap.get("password", None)
        #     _bootstrap_password_file = _bootstrap.get("password_file", None)
        #
        #     if _bootstrap_password and _bootstrap_password_file:
        #         pass
        #     elif not _bootstrap_password and _bootstrap_password_file:
        #         _ = data["bootstrap"].pop("password_file")
        #     elif _bootstrap_password and not _bootstrap_password_file:
        #         _ = data["bootstrap"].pop("password")
        #         data["bootstrap"]["password_file"] = "/etc/mailmonkey/bootstrap-password"

        display.vv(f" = result '{data}'")

        return data

        # if not isinstance(data, list):
        #     return False
        #
        # if len(data) != 1:
        #     return False
        #
        # item = data[0]
        #
        # if not isinstance(item, dict):
        #     return False
        #
        # if len(item) != 1:
        #     return False
        #
        # value = next(iter(item.values()))
        #
        # if not isinstance(value, dict):
        #     return False
        #
        # return True
