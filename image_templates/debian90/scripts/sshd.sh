#!/bin/sh

set -e
set -x

SSHDCONF=/etc/ssh/sshd_config
sudo tee -a $SSHDCONF <<EOF

UseDNS no
EOF

systemctl restart sshd
