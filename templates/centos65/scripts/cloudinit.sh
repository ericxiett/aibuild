#!/bin/bash
set -e
set -x

# yum cache
yum clean all && yum makecache
yum --nogpgcheck install epel-release -y
yum --nogpgcheck install cloud-init cloud-utils-growpart dracut-modules-growroot -y
yum remove epel-release -y
# configure cloud.cfg
cat > /etc/cloud/cloud.cfg <<EOF
users:
 - default

user:
    name: root
    lock_passwd: False

disable_root: False

preserve_hostname: False

syslog_fix_perms: root:root

cloud_init_modules:
 - migrator
 - seed_random
 - bootcmd
 - write-files
 - growpart
 - resizefs
 - set_hostname
 - update_hostname
 - update_etc_hosts
 - rsyslog
 - users-groups
 - ssh

cloud_config_modules:
 - disk_setup
 - mounts
 - locale
 - set-passwords
 - package-update-upgrade-install
 - timezone
 - puppet
 - chef
 - salt-minion
 - mcollective
 - disable-ec2-metadata
 - runcmd

cloud_final_modules:
 - rightscale_userdata
 - scripts-per-once
 - scripts-per-boot
 - scripts-per-instance
 - scripts-user
 - ssh-authkey-fingerprints
 - keys-to-console
 - phone-home
 - final-message
 - power-state-change

system_info:
  distro: rhel
  paths:
    cloud_dir: /var/lib/cloud
    templates_dir: /etc/cloud/templates
  ssh_svcname: sshd

# vim:syntax=yaml
EOF
dracut -f
