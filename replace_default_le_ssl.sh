#!/bin/bash

phishing_server=$1
sudo curl -sSL https://raw.githubusercontent.com/welikechips/bot-tools/master/000-default-le-ssl.conf \
| sed 's|<REPLACE_PHISHING_SERVER_NAME>|'"${phishing_server}"'|g' > /etc/apache2/sites-enabled/000-default-le-ssl.conf
