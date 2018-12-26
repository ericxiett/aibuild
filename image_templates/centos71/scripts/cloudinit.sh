#!/bin/bash

set -e
set -x
mv /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo_backup
cat > /etc/yum.repos.d/base.repo <<EOF
[base]
name=CentOS-$releasever - Base
baseurl=https://mirrors.tuna.tsinghua.edu.cn/centos-vault/7.1.1503/os/x86_64/
gpgcheck=0

#released updates
[updates]
name=CentOS-$releasever - Updates
baseurl=https://mirrors.tuna.tsinghua.edu.cn/centos-vault/7.1.1503/updates/x86_64/
gpgcheck=0

#additional packages that may be useful
[extras]
name=CentOS-$releasever - Extras
baseurl=https://mirrors.tuna.tsinghua.edu.cn/centos-vault/7.1.1503/extras/x86_64/
gpgcheck=0

EOF
# yum cache
yum --nogpgcheck install cloud-init cloud-utils-growpart -y
mv /etc/yum.repos.d/CentOS-Base.repo_backup /etc/yum.repos.d/CentOS-Base.repo
rm -f /etc/yum.repos.d/base.repo

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
