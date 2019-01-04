#!/usr/bin/env bash

set -e
set -x

STOP_PERSISTENT_NET="/etc/udev/rules.d/99-stop-persistent-net.rules"
cat > $STOP_PERSISTENT_NET <<EOF
SUBSYSTEM=="net", DRIVERS=="?*", NAME="%k"
EOF
