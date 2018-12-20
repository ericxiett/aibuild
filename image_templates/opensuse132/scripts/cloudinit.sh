#!/usr/bin/env bash

set -e
set -x

# Install
zypper mr -da
zypper ar -fc http://ftp5.gwdg.de/pub/opensuse/discontinued/distribution/13.2/repo/oss/ gwdg:13.2:OSS
zypper ar -fc http://ftp5.gwdg.de/pub/opensuse/discontinued/distribution/13.2/repo/non-oss gwdg:13.2:NON-OSS
zypper ar http://ftp5.gwdg.de/pub/opensuse/discontinued/update/13.2/openSUSE:13.2:Update.repo gwdg:13.2:UPDATE
zypper install -y cloud-init

systemctl enable cloud-init-local.service cloud-init.service cloud-config.service cloud-final.service

zypper rr gwdg:13.2:OSS
zypper rr gwdg:13.2:NON-OSS
zypper rr gwdg:13.2:UPDATE

zypper mr -ea
