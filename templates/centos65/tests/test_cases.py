import libvirt
import os
import random
import shutil
import string
import sys
import time

import paramiko

DEFAULT_SYSDISK_SIZE = 40
WAIT_VM_OK_TIME = 600 # second

DEFAULT_SSH_USER = 'root'
DEFAULT_SSH_PASSWORD = 'Lc13yfwpW'

TEST_DIR = '/home/'


def toIPAddrType(addrType):
    if addrType == libvirt.VIR_IP_ADDR_TYPE_IPV4:
        return "ipv4"
    elif addrType == libvirt.VIR_IP_ADDR_TYPE_IPV6:
        return "ipv6"


def get_addr(dom_name):
    conn = libvirt.open('qemu:///system')
    dom = conn.lookupByName(dom_name)
    ifaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE)
    print('[dbg]ifaces: ', ifaces)
    # Only one interface
    for (name, val) in ifaces.iteritems():
        if val['addrs']:
            for addr in val['addrs']:
                conn.close()
                return addr['addr']

    conn.close()


def clean_up(dom_name, tmp_path):
    # Destroy dom
    conn = libvirt.open('qemu:///system')
    dom = conn.lookupByName(dom_name)
    dom.destroy()
    dom.undefine()
    conn.close()

    # Remove tmp path
    shutil.rmtree(tmp_path)


class TestCaseValidateSshCreds(object):

    def __init__(self, image):
        self.image = image

    def _prepare(self):
        # Generate tmp dir
        ran_str = ''.join(random.sample(string.ascii_letters, 8))
        print('[dbg]random string: ', ran_str)
        tmp_path = TEST_DIR + ran_str
        self.tmp_path = tmp_path
        os.mkdir(tmp_path)
        shutil.copy(self.image, tmp_path)

        # Create vm
        os.chdir(TEST_DIR + ran_str)
        img_file = os.path.split(sys.argv[1])[-1]
        self.dom_name = img_file
        cmd_create = 'virt-install --name ' + self.dom_name + ' --disk path=' + img_file + \
                     ',bus=virtio,cache=none --network network=default,model=virtio' \
                     ' --ram 4096  --vcpus 2 --accelerate --boot hd ' \
                     '--vnc --vnclisten 0.0.0.0 --noreboot --autostart --import'
        os.system(cmd_create)
        time.sleep(10)
        cmd_start = 'virsh --connect qemu:///system start ' + img_file
        os.system(cmd_start)
        time.sleep(WAIT_VM_OK_TIME)

    def _clean_up(self):
        clean_up(self.dom_name, self.tmp_path)

    def execute(self):
        self._prepare()

        # Get ip of vm
        addr = get_addr(self.dom_name)
        print('[dbg]addr: ', addr)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(addr, username=DEFAULT_SSH_USER, password=DEFAULT_SSH_PASSWORD)
            print('User root is set OK')
            ssh.close()
            self._clean_up()
            return "PASS"
        except Exception as e:
            print('User root is set FAIL')
            self._clean_up()
            return "FAIL"


class TestCaseValidateDiskExtend(object):

    def __init__(self, image, size):
        self.image = image
        self.size = size

    def _prepare(self):
        # Generate tmp dir
        ran_str = ''.join(random.sample(string.ascii_letters, 8))
        print('[dbg]random string: ', ran_str)
        tmp_path = TEST_DIR + ran_str
        self.tmp_path = tmp_path
        os.mkdir(tmp_path)
        shutil.copy(self.image, tmp_path)

        # Create vm
        os.chdir(TEST_DIR + ran_str)
        img_file = os.path.split(sys.argv[1])[-1]
        self.dom_name = img_file

        # Resize
        os.system('qemu-img resize ' + img_file + ' +' + self.size + 'G')
        self.exp_cap_min = DEFAULT_SYSDISK_SIZE + int(self.size) - 5
        self.exp_cap_max = DEFAULT_SYSDISK_SIZE + int(self.size) + 5

        cmd_create = 'virt-install --name ' + self.dom_name + ' --disk path=' + img_file + \
                     ',bus=virtio,cache=none --network network=default,model=virtio' \
                     ' --ram 4096  --vcpus 2 --accelerate --boot hd ' \
                     '--vnc --vnclisten 0.0.0.0 --noreboot --autostart --import'
        os.system(cmd_create)
        time.sleep(10)
        cmd_start = 'virsh --connect qemu:///system start ' + img_file
        os.system(cmd_start)
        time.sleep(WAIT_VM_OK_TIME)

    def _clean_up(self):
        clean_up(self.dom_name, self.tmp_path)

    def execute(self):
        self._prepare()

        # Get ip of vm
        addr = get_addr(self.dom_name)
        print('[dbg]addr: ', addr)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(addr, username=DEFAULT_SSH_USER, password=DEFAULT_SSH_PASSWORD)
            stdin, stdout, stderr = ssh.exec_command('df -h')
            for line in stdout:
                if 'vda' in line and 'boot' not in line:
                    act_cap = int(line.split('G')[0][-2:])
                    if self.exp_cap_min < act_cap < self.exp_cap_max:
                        print('Root partition grow OK')
                        ssh.close()
                        self._clean_up()
                        return "PASS"

            print('Root partition grow FAIL')
            ssh.close()
            self._clean_up()
            return "FAIL"

        except Exception as e:
            print('Root partition grow FAIL')
            self._clean_up()
            return "FAIL"


def main():
    if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
        print("Please input image to be verified!")
        exit(1)

    print("=====TestCase 1: Validate ssh creds=====")
    test_ssh = TestCaseValidateSshCreds(sys.argv[1])
    if test_ssh.execute() == "FAIL":
        print('FAIL: Validate ssh creds')
        return -1
    else:
        print('OK: Validate ssh creds')

    print("=====TestCase 2: Validate disk extend=====")
    test_diskex = TestCaseValidateDiskExtend(sys.argv[1], '60')
    if test_diskex.execute() == "FAIL":
        print('FAIL: Validate disk extend automatically')
        return -1
    else:
        print('OK: Validate disk extend automatically')

    return 0


if __name__ == '__main__':
    sys.exit(main())
