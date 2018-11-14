#!/usr/bin/env bash

set -e
set -x

SSHDCONF=/etc/ssh/sshd_config

sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/g' $SSHDCONF

sudo tee -a $SSHDCONF <<EOF

UseDNS no
EOF

systemctl restart sshd
