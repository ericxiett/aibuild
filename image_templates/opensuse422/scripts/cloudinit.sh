#!/usr/bin/env bash

set -e
set -x

# Install
zypper mr -da
zypper ar -fc https://mirrors.tuna.tsinghua.edu.cn/opensuse/distribution/leap/42.2/repo/oss tsinghua:42.2:OSS
zypper ar -fc https://mirrors.tuna.tsinghua.edu.cn/opensuse/distribution/leap/42.2/repo/non-oss tsinghua:42.2:NON-OSS
zypper ar -fc https://mirrors.tuna.tsinghua.edu.cn/opensuse/update/leap/42.2/oss tsinghua:42.2:UPDATE-OSS
zypper ar -fc https://mirrors.tuna.tsinghua.edu.cn/opensuse/update/leap/42.2/non-oss tsinghua:42.2:UPDATE-NON-OSS
zypper install -y cloud-init

systemctl enable cloud-init-local.service cloud-init.service cloud-config.service cloud-final.service

zypper rr tsinghua:42.2:OSS
zypper rr tsinghua:42.2:NON-OSS
zypper rr tsinghua:42.2:UPDATE-NON-OSS
zypper rr tsinghua:42.2:UPDATE-OSS

zypper mr -ea
