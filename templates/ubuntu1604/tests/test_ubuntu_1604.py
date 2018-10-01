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


def main():
    # Copy img file to /tmp
    if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
        print("Please input image to be verified!")
        exit(1)
    ran_str = ''.join(random.sample(string.ascii_letters, 8))
    print('[dbg]random string: ', ran_str)
    tmp_path = '/home/' + ran_str
    os.mkdir(tmp_path)
    shutil.copy(sys.argv[1], tmp_path)

    # Resize image
    os.chdir('/home/' + ran_str)
    img_file = os.path.split(sys.argv[1])[-1]
    os.system('qemu-img resize ' + img_file + ' +60G')
    exp_cap_min = DEFAULT_SYSDISK_SIZE + 55
    exp_cap_max = DEFAULT_SYSDISK_SIZE + 65

    # Create instance
    cmd_create = 'virt-install --name ' + img_file + ' --disk path=' + img_file + \
          ',bus=virtio,cache=none --network network=default,model=virtio' \
          ' --ram 4096  --vcpus 2 --accelerate --boot hd ' \
          '--vnc --vnclisten 0.0.0.0 --noreboot --autostart --import'
    os.system(cmd_create)
    time.sleep(10)
    cmd_start = 'virsh --connect qemu:///system start ' + img_file
    os.system(cmd_start)
    time.sleep(WAIT_VM_OK_TIME)

    # Get ip of vm
    addr = get_addr(img_file)
    print('[dbg]addr: ', addr)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(addr, username='root', password='Lc13yfwpW')
        print('User root is set OK')
        stdin, stdout, stderr = ssh.exec_command('df -h')
        for line in stdout:
            if 'vda' in line and 'boot' not in line:
                act_cap = int(line.split('G')[0][-2:])
                if exp_cap_min < act_cap < exp_cap_max:
                    print('Root partition grow OK')

    finally:
        ssh.close()

    # Clean
    clean_up(img_file, tmp_path)


if __name__ == '__main__':
    sys.exit(main())
