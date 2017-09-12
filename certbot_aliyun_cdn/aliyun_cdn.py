"""Installer for Aliyun CDN."""

import zope.interface  # pylint: disable=W0403

from certbot import errors
from certbot import interfaces
from certbot.plugins import common, dns_common


from .client import CDN


def steal(func_name, static=False):
    def add_func_to_class(cls):
        func = getattr(dns_common.DNSAuthenticator, func_name)
        if static:
            func = staticmethod(func)
        else:
            func = func.im_func
        setattr(cls, func_name, func)
        return cls
    return add_func_to_class


@steal("_configure")
@steal("_configure_file")
@steal("_configure_credentials")
@steal("_prompt_for_data", static=True)
@steal("_prompt_for_file", static=True)
@zope.interface.implementer(interfaces.IInstaller)
@zope.interface.provider(interfaces.IPluginFactory)
class Installer(common.Installer):
    """Certbot Installer for Aliyun CDN

    This Installer will install https certs to your Aliyun CDN Server
    """

    description = "Install certificates to your Aliyun CDN Server"

    def __init__(self, *args, **kwargs):
        super(Installer, self).__init__(*args, **kwargs)
        self.cdn_client = CDN()

    @classmethod
    def add_parser_arguments(cls, add):
        super(Installer, cls).add_parser_arguments(add)
        add("credentials", help="Aliyun CDN credentials INI file.")

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return (
            "This plugin installs https certificates to CDN servers "
            "using Aliyun's management API."
        )

    def prepare(self):
        pass

    def _setup_credentials(self):
        credentials = self._configure_credentials(
            "credentials",
            "Aliyun CDN credentials INI file",
            {
                "access-key-id": "access key id for Aliyun API",
                "access-key-secret": "access key secret for Aliyun API"
            }
        )
        self.cdn_client.set_credentials(
            credentials.conf("access-key-id"),
            credentials.conf("access-key-secret")
        )

    def get_all_names(self):  # type: ignore
        """I don't know what does this function do"""

    def deploy_cert(
        self, domain, cert_path, key_path, chain_path, fullchain_path
    ):
        """Deploy certificate.
        :param str domain: domain to deploy certificate file
        :param str cert_path: absolute path to the certificate file
        :param str key_path: absolute path to the private key file
        :param str chain_path: absolute path to the certificate chain file
        :param str fullchain_path: absolute path to the certificate fullchain
            file (cert plus chain)
        :raises .PluginError: when cert cannot be deployed
        """
        self._setup_credentials()

        with open(fullchain_path, "rt") as f:
            public = f.read()
        with open(key_path, "rt") as f:
            private = f.read()

        try:
            self.cdn_client.install_cert(domain, (public, private))
        except ValueError as e:
            raise errors.PluginError("Unable to deploy: {0}".format(e))

    def _enable_redirect(self, domain, options):
        """Redirect all equivalent HTTP traffic to ssl_vhost.
        Add rewrite directive to non https traffic

        :param str domain: domain to enable redirect for
        :param unused_options: Not currently used
        :type unused_options: Not Available
        """
        self.cdn_client.set_redirect(domain, True)

    def enhance(self, domain, enhancement, options=None):
        """Perform a configuration enhancement.
        :param str domain: domain for which to provide enhancement
        :param str enhancement: An enhancement as defined in
            :const:`~certbot.constants.ENHANCEMENTS`
        :param options: Flexible options parameter for enhancement.
            Check documentation of
            :const:`~certbot.constants.ENHANCEMENTS`
            for expected options for each enhancement.
        :raises .PluginError: If Enhancement is not supported, or if
            an error occurs during the enhancement.
        """
        if enhancement == "redirect":
            self._enable_redirect(domain, options)
        else:
            raise errors.PluginError(
                "Unsupported enhancement: {0}".format(enhancement)
            )

    def supported_enhancements(self):  # type: ignore
        """Returns a `collections.Iterable` of supported enhancements.
        :returns: supported enhancements which should be a subset of
            :const:`~certbot.constants.ENHANCEMENTS`
        :rtype: :class:`collections.Iterable` of :class:`str`
        """
        return ["redirect"]

    def save(self, title=None, temporary=False):  # type: ignore
        """Aliyun CDN Installer does not use this function"""

    def rollback_checkpoints(self, rollback=1):  # type: ignore
        """Aliyun CDN Installer does not use this function"""

    def recovery_routine(self):  # type: ignore
        """Aliyun CDN Installer does not use this function"""

    def view_config_changes(self):  # type: ignore
        """Aliyun CDN Installer does not use this function"""

    def config_test(self):  # type: ignore
        """Aliyun CDN Installer does not use this function"""

    def restart(self):  # type: ignore
        """Aliyun CDN Installer does not use this function"""
