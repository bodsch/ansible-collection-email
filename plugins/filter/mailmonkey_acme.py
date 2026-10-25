# python 3 headers, required if submitting to Ansible

from ansible.utils.display import Display

display = Display()


class FilterModule:
    """
    Expand the compact dovecot metric definitions into what 2.4 renders.
    """

    def filters(self):
        return {
            "validate_acme_config": self.validate_acme_config,
        }

    def validate_acme_config(self, data):
        """ """
        display.vv(f"bodsch.email::validate_acme_config('{data}')")
        msg: list = []
        valid: bool = True
        _mail_hostname: str = None
        _acme_webroot: str = None
        _acme_dns_challenge: str = None

        _mail_hostname = data.get("mail", {}).get("hostname", None)
        _acme_webroot = data.get("acme", {}).get("webroot")
        _acme_dns_challenge = data.get("acme", {}).get("dns", {}).get("challenge")

        display.vv(f"= mail.hostname     : {_mail_hostname}")
        display.vv(f"= acme.webroot      : {_acme_webroot}")
        display.vv(f"= acme.dns.challenge: {_acme_dns_challenge}")

        # mail.hostname is not set; it is the name the certificate is issued for
        # neither acme.webroot nor acme.dns.challenge is set; there would be no way to answer a challenge

        if not _mail_hostname:
            valid = False
            msg.append(
                "mail.hostname is not set; it is the name the certificate is issued for"
            )

        if not (_acme_webroot or _acme_dns_challenge):
            valid = False
            msg.append(
                "neither acme.webroot nor acme.dns.challenge is set; there would be no way to answer a challenge"
            )

        display.vv(f"= result: {valid}, {msg}")

        return {"valid": valid, "msg": msg}
