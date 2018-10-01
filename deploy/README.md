# Ansible for aibuild

## Precondition
* 2 vms or dedicated servers
* OS: ubuntu 16.04
* 1 vm for deploying, ubuntu 1604, ansible: 2.6

## Setup deploy server
``` bash
$ apt update
$ apt install -y git vim
$ add-apt-repository ppa:ansible/ansible
$ apt update
$ apt install -y ansible
$ git clone https://github.com/ericxiett/aibuild.git
```

## Use
``` bash
# Install python on aibuild01/02
$ apt install -y python
$ cd aibuild/deploy
$ ansible-playbook site.yml
```
