import os
import random
import shutil
import string
import time
import urllib2

import requests

from aibuild.common.config import CONF


def download_image(image, dest):
    '''
    Download image from url to dest dir
    :param image: image need to be download
    :param dest: dest dir which store the image
    :return:
    '''
    try:
        image_data = urllib2.urlopen(image)
        data_to_write = image_data.read()
        name = image.split('/')[-1]
        dest_file = dest + '/' + name
        with open(dest_file, 'wb') as f:
            f.write(data_to_write)
    except Exception as e:
        print('Can not download image. Got error %s' % e.message)
        return None
    return dest_file


def create_tmp_dir():
    random_str = ''.join(random.sample(string.ascii_letters, 8))
    tmp_path = '/tmp/' + random_str
    os.mkdir(tmp_path)
    return tmp_path


def create_vm_by_virt(image_path, extended_size):
    '''
    Create one vm by virt-install
    :param image_path: Absolute path of image file, like
    /tmp/xlekjig/centos65x86_64_20181207-5.qcow2
    :param extended_size: extended size of root
    :return:
    '''
    if not os.path.exists(image_path):
        print('Image not found in %s' % image_path)
        return None
    image_dir = image_path.split('/')[:-2]
    image_file = image_path.split('/')[-1]
    os.chdir(image_dir)
    dom_name = image_file
    os.system('qemu-img resize ' + image_file + ' +' + extended_size + 'G')
    cmd_create = 'virt-install --name ' + dom_name + ' --disk path=' + image_file + \
                 ',bus=virtio,cache=none --network network=default,model=virtio' \
                 ' --ram 4096  --vcpus 2 --accelerate --boot hd ' \
                 '--vnc --vnclisten 0.0.0.0 --noreboot --autostart --import'
    os.system(cmd_create)
    time.sleep(10)
    cmd_start = 'virsh --connect qemu:///system start ' + image_file
    os.system(cmd_start)
    time.sleep(600)
    return dom_name


def clean_up(dom, dir):
    # Destroy dom
    conn = libvirt.open('qemu:///system')
    dom = conn.lookupByName(dom)
    dom.destroy()
    dom.undefine()
    conn.close()

    # Remove tmp path
    shutil.rmtree(dir)


def get_vm_addr(dom_name):
    conn = libvirt.open('qemu:///system')
    dom = conn.lookupByName(dom_name)
    ifaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE)
    # Only one interface
    for (name, val) in ifaces.iteritems():
        if val['addrs']:
            for addr in val['addrs']:
                conn.close()
                return addr['addr']

    conn.close()
    return None


def send_test_result(image, case, result):
    '''
    Send result of testcase to aibuild-server
    :param image: name of image tested
    :param case: name of test case
    :param result: result of this test
    :return:
    '''
    url = CONF.get('DEFAULT', 'api_server') + '/test'
    data = {
        'image_name': image,
        'case_name': case,
        'result': result
    }
    res = requests.post(url, data=data)
    if res.status_code != '200':
        print('Failed to record result of this test')
