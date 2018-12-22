#!/usr/bin/env bash

set -e
set -x

# Install
apt update
apt install -y qemu-guest-agent
