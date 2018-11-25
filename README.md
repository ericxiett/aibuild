# Automate to build GuestOS images(AIBuild)

## Introduce

### Architecture
![Alt text](./arch.png)

1. aibuild服务初始化时，创建相关表格，并监听服务，端口9753
2. 新增一个镜像，编写制作和测试代码，推送到Gitlab
3. Jenkins触发构建流程，构建结束将数据库更新
4. 管理员和运维人员通过API/CLI查看镜像来龙去脉

### Init Flow

初始化的工作包括：
* 数据库建立，表的创建
* web服务器建立，web根目录的建立

### Build Flow

* 待构建OS注册：通过xls注册，gitlab建立项目，jenkins建立job，web服务器建立子目录
* 运维人员提交代码，触发构建
* 构建完成后将镜像放置到子目录，形成url

### Test Flow

* 测试用例注册：通过xls注册，关联guest OS
* 测试
* 测试不通过会将build的镜像删除

### Release Flow
存在2个主要流程
1. 环境注册：通过xls注册镜像可以推送到的环境，保证环境和镜像服务器
之间网络连通性；
2. 镜像发布：构建开始通过手动输入环境名称和要推送构建ID或者guestOS，构建过程会推送镜像到
环境。注：如传入GuestOS，则会选择最新一次构建和测试都通过的镜像

### DB Design

Database: aibuild

* Table: guestos

| field | type | Null | Key | Default | Extra |
|------|------|------|------|------|------|
|id|varchar(36)|NO|PRI|NULL||
|name|varchar(255)|YES||NULL||
|base_iso|varchar(255)|YES||NULL||
|type|varchar(36)|YES||NULL||
|distro|varchar(36)|YES||NULL||
|version|varchar(36)|YES||NULL||


* Table: build_log

| field | type | Null | Key | Default | Extra |
|------|------|------|------|------|------|
|id|varchar(36)|NO|PRI|NULL||
|image_name|varchar(255)|YES||NULL||
|os_id|varchar(36)|YES||NULL||
|build_at|datetime|YES||NULL||
|update_contents|text|YES||NULL||
|get_url|varchar(255)|YES||NULL||

* Table: testcases

| field | type | Null | Key | Default | Extra |
|------|------|------|------|------|------|
|id|varchar(36)|NO|PRI|NULL||
|name|varchar(255)|YES||NULL||
|os_type|varchar(36)|YES||NULL||

os_type: 测试用例适用于linux或windows

* Table: test_log

|field|type|Null|Key|Default|Extra|
|------|------|------|------|------|------|
|id|varchar(36)|NO|PRI|NULL||
|build_id|varchar(36)|YES||NULL||
|case_id|varchar(36)|YES||NULL||
|result|varchar(10)|YES||NULL||
|test_at|datetime|YES||NULL||

* Table: release_log

|field|type|Null|Key|Default|Extra|
|------|------|------|------|------|------|
|id|varchar(36)|NO|PRI|NULL||
|env_id|varchar(60)|YES||NULL||
|glance_id|varchar(36)|YES||NULL||
|release_at|datetime|YES||NULL||

* Table: envs

|field|type|Null|Key|Default|Extra|
|------|------|------|------|------|------|
|id|varchar(36)|NO|PRI|NULL||
|name|varchar(64)|NO||NULL||
|auth_url|varchar(255)|NO||NULL||
|project_domain_name|varchar(64)|NO||NULL||
|user_domain_name|varchar(64)|NO||NULL||
|project_name|varchar(64)|NO||NULL||
|username|varchar(255)|NO||NULL||
|password|varchar(255)|NO||NULL||
|region|varchar(255)|NO||NULL||


## Install

### gitlab和jenkin均使用容器实现
* Install docker
``` bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt install apt-transport-https
apt update
apt policy docker-ce
apt install -y docker-ce
systemctl status docker
```

* 部署jenkins
``` bash
# 如下命令用于容器镜像加速
vi /etc/docker/daemon.json
{
  "registry-mirrors": ["https://registry.docker-cn.com"]
}
systemctl restart docker.service
docker pull jenkins/jenkins:lts
cd /home
docker run -d -p 49001:8080 -v $PWD/jenkins:/var/jenkins_home -t jenkins/jenkins:lts
chown -R 1000 $(pwd)/jenkins/
docker start 534dba942d5a
```

登录http://172.23.61.5:49001/，按照指示进行操作
初始化密码获取：cat jenkins/secrets/initialAdminPassword
按照建议装插件
配置管理员: admin/Lc13yfwpW

* 部署gitlab
``` bash
docker pull gitlab/gitlab-ce
mkdir -p /home/gitlab/{config,data,logs}
docker run -d \
--hostname gitlab \
--publish 49011:80 \
--name gitlab \
--restart always \
--volume /home/gitlab/config:/etc/gitlab \
--volume /home/gitlab/logs:/var/log/gitlab \
--volume /home/gitlab/data:/var/opt/gitlab \
gitlab/gitlab-ce

```
账户：root/Lc13yfwpW

### aibuild server
* 安装qemu，kvm
``` bash
$ apt install qemu-kvm git
```

* Download packer
``` bash
$ https://releases.hashicorp.com/packer/1.2.5/packer_1.2.5_linux_amd64.zip
$ apt install -y unzip
$ unzip packer_1.2.5_linux_amd64.zip
$ ls
packer  packer_1.2.5_linux_amd64.zip
```

* Setup aibuild
``` bash
$ apt install mariadb-server python-pymysql python-mysqldb python-pecan
$ vim /etc/mysql/mariadb.conf.d/aibuild.cnf
[mysqld]
bind-address = 0.0.0.0

default-storage-engine = innodb
innodb_file_per_table
max_connections = 4096
open_files_limit = 8192
collation-server = utf8_general_ci
character-set-server = utf8

$ systemctl restart mysql
$ mysql_secure_installation
$ mysql -uroot -pLc13yfwpW
CREATE DATABASE aibuild CHARACTER SET utf8;
GRANT ALL PRIVILEGES ON aibuild.* TO 'aibuild'@'localhost' \
       IDENTIFIED BY 'Lc13yfwpW';
CREATE DATABASE aibuild CHARACTER SET utf8;
GRANT ALL PRIVILEGES ON aibuild.* TO 'aibuild'@'%' \
       IDENTIFIED BY 'Lc13yfwpW';
$ cd /opt/
$ git clone https://github.com/ericxiett/aibuild.git
$ cd aibuild/
$ python setup.py develop
$ mkdir -p /var/log/aibuild
$ mkdir -p /etc/aibuild
$ vim /etc/aibuild/aibuild.conf
[DEFAULT]
db_connection = mysql+pymysql://aibuild:Lc13yfwpW@127.0.0.1/aibuild?charset=utf8
pecan_config_path = /opt/aibuild/config.py
$ cd aibuild/cmd/
$ python dbsync.py create
$ nohup pecan serve config.py &
```

* web server
使用apache2搭建web服务器，/var/www/html目录空间至少为2TB，建议使用lvm的方式，方便扩容。分为2个目录
	* build: 构建成功后推送的地方，/var/www/html/images/build
	* release: 测试通过后推送的地方，/var/www/html/images/release

## Use

* Create one project of gitlab

    http://172.23.61.5:49011/root/ubuntu1604-tpl

* 配置webhook

    1）jenkins “系统管理”->”插件管理”->”可选插件”，选择Gitlab Hook Plugin和Gitlab Plugin

    2）配置从节点

    3）打开要自动构建的jenkins项目，找到构建触发器，勾选Build when a change is pushed to GitLab. GitLab CI Service，并记录下后面的url地址。

    4）进入gitlab项目管理界面，选择webhook，在url中输入刚才在jenkins配置界面复制那一个url，点击ADD WEB HOOK，之后再点击TEST HOOK，如果看到jenkins中有自动出现一个构建事件，即是配置成功了。
    
## TODO
1. deploy Container（jenkins，gitlab）启动有问题，
    * jenkins start报错
    * gitlab 暴露端口不对

2. 集成mod_wsgi有问题
