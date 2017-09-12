# -*- coding: utf8 -*-

import arrow
import logging
import requests

from aliyunauth.sign_ver_1_0 import AuthBase
from datetime import datetime
from OpenSSL import crypto

__version__ = "0.0.1"

logger = logging.getLogger(__name__)


class CDNAuth(AuthBase):
    SERVICE = "cdn"
    VERSION = "2014-11-11"


class CDN(object):
    ENDPOINT = "https://cdn.aliyuncs.com"
    PAGE_SIZE = 50

    def __init__(self):
        self.session = requests.session()

    def set_credentials(self, access_key_id, access_key_secret):
        self.session.auth = CDNAuth(access_key_id, access_key_secret)

    def get_domain(self, domain):
        resp = self.call("DescribeCdnDomainDetail", DomainName=domain)
        return resp["GetDomainDetailModel"]

    def check_expiratoin(self, domain, leeway=45):
        info = self.get_domain(domain)
        pub = info.get("ServerCertificate")
        if pub is None:
            return True

        now = arrow.now()
        expires_in = (self.get_cert_expiratoin(pub) - now).days
        return expires_in <= leeway

    def call(self, action, **args):
        args["Action"] = action
        resp = self.session.get(self.ENDPOINT, params=args)
        try:
            resj = resp.json()
        except:
            error = resp.text
        else:
            error = resj.get("Message")
        if error is not None:
            raise ValueError(error)
        return resj

    def list_domains(self, page=1):
        resp = self.call(
            "DescribeUserDomains",
            PageNumber=page,
            DomainStatus=u"online"
        )
        for domain in resp["Domains"]["PageData"]:
            yield domain["DomainName"]
        total = resp["TotalCount"]
        page_size = resp["PageSize"]
        if total > page_size * self.PAGE_SIZE:
            for domain in self.list_domains(page + 1):
                yield domain

    def get_cert_expiratoin(self, pub):
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, pub)
        expire_str = cert.get_notAfter().decode("utf8")
        return arrow.get(datetime.strptime(expire_str, "%Y%m%d%H%M%SZ"))

    def install_cert(self, domain, cert):
        public, private = cert
        name = domain.split(".", 1)[0]
        expires_at = self.get_cert_expiratoin(public)
        suffix = expires_at.format("YYYY.MM.DD-SSS")

        return self.call(
            "SetDomainServerCertificate",
            DomainName=domain,
            CertName="{0}-{1}".format(name, suffix),
            ServerCertificateStatus="on",
            ServerCertificate=public,
            PrivateKey=private
        )

    def set_redirect(self, domain, do_redirect):
        return self.call(
            "SetForceRedirectConfig",
            DomainName=domain,
            RedirectType="Https" if do_redirect else "Off"
        )
