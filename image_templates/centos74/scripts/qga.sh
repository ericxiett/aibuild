#!/usr/bin/env bash

set -e
set -x

# Install
yum clean all && yum makecache
yum --nogpgcheck install epel-release -y
yum --nogpgcheck install qemu-guest-agent -y
yum remove epel-release -y
