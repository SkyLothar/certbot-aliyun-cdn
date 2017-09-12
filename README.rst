Aliyun CDN Installer plugin for Certbot
-------------------------------------------
.. image:: https://travis-ci.org/SkyLothar/certbot-aliyun-cdn.svg?branch=master
    :target: https://travis-ci.org/SkyLothar/certbot-aliyun-cdn
.. image:: https://coveralls.io/repos/github/SkyLothar/certbot-aliyun-cdn/badge.svg?branch=master
    :target: https://coveralls.io/github/SkyLothar/certbot-aliyun-cdn?branch=master


Use the certbot client to install a certificate to a aliyun cdn server

Prepare an API Token
====================
Fetch access-key id/secret pair on https://ram.console.aliyun.com/#/overview


Install certbot and plugin
==========================

.. code-block:: bash

    pip install certbot-aliyun-cdn


Create a credentials file
=========================

.. code-block:: ini

    certbot_alicdn:aliyun_cdn_access_key_id = "ALIYUN-ACCESS-KEY-ID"
    certbot_alicdn:aliyun_cdn_access_key_secret = "ALIYUN-ACCESS-KEY-SECRET"


Install a certificate
======================

.. code-block:: bash

    certbot run -a SOME-AUTHENTICATOR-PLUGIN \
        --reinstall --redirect \
        -i certbot-aliyun-cdn:aliyun-cdn \
        [--certbot-dns-dnspod:dns-dnspod-credentials PATH-TO-CREDENTIAL-FILE]
        -d REPLACE-WITH-YOUR-DOMAIN
