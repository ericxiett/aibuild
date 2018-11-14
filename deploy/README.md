# Ansible for aibuild

NOTE: Experimental. Should not used on product ENV.

## Precondition
* 2 vms and 2 dedicated servers
* OS: ubuntu 16.04
* 1 vm for deploying, ubuntu 1604, ansible: 2.7; 1 vm for cid; 2 servers for workers

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

* Modify hosts and site.yml that adapt your env

* Execute:

``` bash
$ apt install -y python
$ cd aibuild/deploy
$ ansible-playbook site.yml
```

## TODO

1. Error: the exported ports of containers are not correct. TODO use command instead of docker module
