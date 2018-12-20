#!/usr/bin/env bash

set -e
set -x

# Install
zypper mr -da
zypper ar -fc http://ftp5.gwdg.de/pub/opensuse/discontinued/distribution/13.2/repo/oss/ gwdg:13.2:OSS
zypper ar -fc http://ftp5.gwdg.de/pub/opensuse/discontinued/distribution/13.2/repo/non-oss gwdg:13.2:NON-OSS
zypper ar http://ftp5.gwdg.de/pub/opensuse/discontinued/update/13.2/openSUSE:13.2:Update.repo gwdg:13.2:UPDATE
zypper install -y cloud-init

# Config
cd /etc/cloud
CLOUDCFG=cloud.cfg
mv $CLOUDCFG ${CLOUDCFG}_bak
tee -a $CLOUDCFG << EOF
users:
   - name: root
     lock_passwd: False
disable_root: false
network:
  config: disabled
cloud_init_modules:
 - ssh
 - migrator
 - seed_random
 - bootcmd
 - write-files
 - growpart
 - resizefs
 - disk_setup
 - mounts
 - set_hostname
 - update_hostname
 - update_etc_hosts
 - ca-certs
 - rsyslog
 - users-groups
cloud_config_modules:
 - emit_upstart
 - snap
 - snap_config  # DEPRECATED- Drop in version 18.2
 - ssh-import-id
 - locale
 - set-passwords
 - grub-dpkg
 - apt-pipelining
 - apt-configure
 - ubuntu-advantage
 - ntp
 - timezone
 - disable-ec2-metadata
 - runcmd
 - byobu
cloud_final_modules:
 - snappy  # DEPRECATED- Drop in version 18.2
 - package-update-upgrade-install
 - fan
 - landscape
 - lxd
 - puppet
 - chef
 - mcollective
 - salt-minion
 - rightscale_userdata
 - scripts-vendor
 - scripts-per-once
 - scripts-per-boot
 - scripts-per-instance
 - scripts-user
 - ssh-authkey-fingerprints
 - keys-to-console
 - phone-home
 - final-message
EOF

systemctl enable cloud-init-local.service cloud-init.service cloud-config.service cloud-final.service

zypper rr gwdg:13.2:OSS
zypper rr gwdg:13.2:NON-OSS
zypper rr gwdg:13.2:UPDATE

zypper mr -ea
