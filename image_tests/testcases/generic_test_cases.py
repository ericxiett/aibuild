import paramiko

from image_tests.common import utils


class GenericLinuxTestCases(object):

    def __init__(self, image, extended_size, distro, version, username, password):
        '''
        Generic Testcase Class
        :param image: image need to be tested. Must be
        url that can be download. Like http://x.x.x.x/images/
        centos65/centos65x86_64-20181207-5.qcow2
        :param extended_size: extended size of root
        :param version: version of image, like 6.5
        :param username: user name for ssh
        :param password: password for ssh
        :param distro: Distro, like centos
        '''
        self.image = image
        self.extended_size = extended_size
        self.version = version
        self.username = username
        self.password = password
        self.distro = distro

    def _prepare(self):
        # Create tmp dir and download image
        self.tmp_dir = utils.create_tmp_dir()
        test_image = utils.download_image(self.image, self.tmp_dir)

        # Create one vm by virt-install locally.
        # TODO: Next consider how to integrate tests on OpenStack
        if not test_image:
            self.dom = utils.create_vm_by_virt(test_image, self.extended_size)
        else:
            print('Failed to download image!')
            exit(1)

        # Get ip of vm
        self.addr = utils.get_vm_addr(self.dom)
        if not self.addr:
            print('Can not get ip of vm, please check!')
            exit(1)

    def _clean_up(self):
        utils.clean_up(self.dom, self.tmp_dir)

    def test_case_validate_ssh_creds(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(self.addr, username=self.username, password=self.password)
            print('User root is set OK')
            ssh.close()
            result = "PASS"
        except Exception as e:
            print('User root is set FAIL')
            result = "FAIL"

        utils.send_test_result(self.dom, 'ssh creds test', result)

    def test_case_validate_disk_extend(self):
        exp_cap_min = 40 + int(self.extended_size) - 5
        exp_cap_max = 40 + int(self.extended_size) + 5
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(self.addr, username=self.username, password=self.password)
            stdin, stdout, stderr = ssh.exec_command('df -h')
            for line in stdout:
                if 'vda' in line and 'boot' not in line:
                    act_cap = int(line.split('G')[0][-2:])
                    if exp_cap_min < act_cap < exp_cap_max:
                        print('Root partition grow OK')
                        ssh.close()
                        result = "PASS"

            print('Root partition grow FAIL')
            ssh.close()
            result = "FAIL"

        except Exception as e:
            print('Root partition grow FAIL')
            result = "FAIL"

        utils.send_test_result(self.dom, 'validate disk extend', result)

    def test_case_validate_version(self):
        if self.distro.lower() == 'centos':
            cmd = 'cat /etc/centos-release'
        elif self.distro.lower() == 'ubuntu':
            cmd = 'cat /etc/os-release'
        else:
            print('Unsupport distro %s' % self.distro)
            return

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(self.addr, username=self.username, password=self.password)
            stdin, stdout, stderr = ssh.exec_command(cmd)
            if self.version in stdout:
                print('Distro is %s OK' % self.version)
                ssh.close()
                result = 'PASS'
            else:
                print('Distro is %s FAIL' % self.version)
                ssh.close()
                result = "FAIL"
        except Exception as e:
            print('Distro is %s FAIL' % self.version)
            result = "FAIL"
        utils.send_test_result(self.image, 'validate version', result)

