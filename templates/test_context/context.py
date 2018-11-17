import libvirt
from functools import partial
import paramiko
import logging
import string
import time
import random
import os
import shutil
import xml.etree.ElementTree as et
from xml.etree.ElementTree import Element as element
import winrm

DEFAULT_SYSDISK_SIZE = 80
WAIT_VM_OK_TIME = 600  # second
TOLERANCE = 1024 * 1024 * 1024 * 5
DEFAULTT_SERVER_BOOT_TIMEOUT = 60
TEST_DIR = '/home/'
VIRTINSTALL_CMD = """
virt-install --name %(domain_name)s --disk path=%(img_file)s,bus=virtio,cache=none 
                     --network network=default,model=virtio --memballoon virtio
                     --ram 8192  --vcpus 4 --accelerate --boot hd
                     --console pty,target_type=serial
                     --vnc --vnclisten 0.0.0.0 --noreboot --autostart --import
"""


def setup_logging():
    """
    setup cumstom logging layout
    :return:
    """
    logging_format = "[%(asctime)s] - %(levelname)s - %(name)s.%(lineno)s - %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=logging_format)


def toIPAddrType(addrType):
    if addrType == libvirt.VIR_IP_ADDR_TYPE_IPV4:
        return "ipv4"
    elif addrType == libvirt.VIR_IP_ADDR_TYPE_IPV6:
        return "ipv6"


def get_addr(dom_name):
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


def get_ssh_connection(ip="localhost", port=22, username=None, password=None, **kwargs):
    addr = ip
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(addr, port=int(port), username=username, password=password)
    return ssh


def get_winrm_connection(ip="localhost", port="5985", username="administrator", password="123456a?", **kwargs):
    """
    obtain winrm connection
    :param obj
    :param ip: virtual machine ip
    :param port:
    :param username:
    :param password:
    :return:
    """
    session = winrm.Session("%s:%s" % (ip, port), auth=(username, password))
    return session


def _output_log_to_file(conn, dom, log_file_path='/var/log/sjt-test.log'):
    """
    modify domain XML and append logs to files
    :param conn
    :param dom:
    :param log_file_path: log file path
    :return:
    """

    dom_xml = dom.XMLDesc()

    root = et.fromstring(dom_xml)
    device = root.find('devices')

    serials = root.findall('*/serial')
    for serial in serials:
        device.remove(serial)

    consoles = root.findall('*/console')
    for console in consoles:
        serial_log_node = element('log')
        serial_log_node.set('file', log_file_path)
        serial_log_node.set('append', 'off')
        console.insert(-1, serial_log_node)

    new_dom_xml = et.tostring(root)

    dom.undefine()
    dom = conn.defineXML(new_dom_xml)

    return dom


def clean_up(dom_name, tmp_path):
    try:
        # Destroy dom
        conn = libvirt.open('qemu:///system')
        dom = conn.lookupByName(dom_name)
        dom.destroy()
        dom.undefine()
        conn.close()
    except Exception:
        logging.exception("connection to qemu failed")

    try:
        # Remove tmp path
        logging.info("remove %s", tmp_path)
        shutil.rmtree(tmp_path)
    except Exception:
        logging.exception("remove %s failed", tmp_path)


def test(func):
    func.test_this = True
    return func


class GenericContext(object):
    """
    a generic test_context class
    """

    def init(self, *args, **kwargs):
        pass

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __call__(self, *args, **kwargs):
        pass


class LibvirtContext(GenericContext):
    """
    libvirt test_context
    """

    def __init__(self, domain_name, image):
        self.conn = None
        self.image = image
        self.dom = None
        self.tmp_path = None
        self.domain_name = domain_name
        self.logger = logging.getLogger(__name__)

    def __call__(self, *args, **kwargs):
        super(LibvirtContext, self).__call__(*args, **kwargs)
        self.init(*args, **kwargs)

    def init(self, *args, **kwargs):
        super(LibvirtContext, self).init(*args, **kwargs)

        test_class = args[0]
        test_obj = test_class()

        attrs = dir(test_obj)

        with self:
            self.set_connection(test_obj)

            # call init function
            if hasattr(test_obj, 'init'):
                getattr(test_obj, "init")(*args, **kwargs)

            # search & call methods with signiture
            for attr in attrs:
                if hasattr(getattr(test_obj, attr), "test_this"):
                    self.logger.info('running test: %s', attr)
                    getattr(test_obj, attr)()
                else:
                    self.logger.debug('method: %s appears not to be a test method', attr)

    def set_connection(self, obj):
        pass

    def clean_up(self):
        """
        clean up temp folder & backup image files
        :return:
        """
        clean_up(self.domain_name, self.tmp_path)

    def __enter__(self):

        self.logger.info('start creating virtual machine')
        self.create_domain()

        self.logger.info('start virtual machine')
        self.start_domain()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.info('cleaning up temp folders')
        self.clean_up()

    def create_domain(self):
        """
        create(define) a new domain
        :return:
        """

        domain_name = self.domain_name
        image = self.image

        # create a temp folder
        ran_str = ''.join(random.sample(string.ascii_letters, 8))
        tmp_path = TEST_DIR + ran_str
        self.tmp_path = tmp_path

        self.logger.info("creating tmp folder: %s and copy %s", TEST_DIR + ran_str, image)
        os.mkdir(tmp_path)
        shutil.copy(image, tmp_path)

        # copy and backup tested image
        os.chdir(TEST_DIR + ran_str)
        img_file = os.path.split(image)[-1]

        # resize drive to DEFAULT_SYSDISK_SIZE
        self.logger.info('resizing image file')
        os.system('qemu-img resize ' + img_file + ' +' + str(DEFAULT_SYSDISK_SIZE - 40) + 'G')

        # I have not been able to think of an esaier solution to this
        # libvirt python library requires XML to define a domain
        # better learn how nova handles this
        self.logger.info('creating test virtual machine')
        cmd_create = (VIRTINSTALL_CMD % {
            "domain_name": domain_name,
            "img_file": img_file
        }).replace('\n', '')
        os.system(cmd_create)

    def _lookup_domain_by_name(self):

        domain_name = self.domain_name
        if not self.conn:
            self._initialize_connection()

        dom = self.conn.lookupByName(domain_name)
        if not dom:
            self.logger.error("Failed finding domain with name %s" % domain_name)
            raise Exception("Failed finding domain with name %s" % domain_name)
        return dom

    def _initialize_connection(self):

        if not self.conn:
            self.conn = libvirt.open("qemu:///system")
            if not self.conn:
                self.logger.error("Failed connecting local libvirt daemon!")
                raise Exception('Failed connecting local libvirt daemon!')

    def update_domain(self):
        """
        update a domain (better inactive)
        by default, add log
        :return:
        """

        domain_name = self.domain_name
        if not domain_name:
            return

        dom = self._lookup_domain_by_name()
        self.dom = _output_log_to_file(self.conn, dom)

    def start_domain(self, updatable=True):
        """
        running an inactive domain
        :param updatable: if one wants to domain should be updated before launching
        :return:
        """
        if updatable:
            self.update_domain()
        # dom = self._lookup_domain_by_name()

        # this method is synchronous by nature
        # but in a specific test case, one should
        # wait for os bootup to continue further operations
        self.logger.info("start domain")
        self.dom.create()

        # waiting for a specific period of time
        time.sleep(DEFAULTT_SERVER_BOOT_TIMEOUT)

    @property
    def ip(self):
        ip = get_addr(self.domain_name)
        self.logger.debug('domain %s IP %s', self.domain_name, ip)
        return ip


class SshLibvirtContext(LibvirtContext):
    def set_connection(self, obj):
        def wrapper(username, password):
            return get_ssh_connection(ip=self.ip, port=22, username=username, password=password)
        setattr(obj, 'get_connection', wrapper)


class WinrmLibvirtContext(LibvirtContext):
    def set_connection(self, obj):

        # a function is upgraded to be a method
        # which should be taken great care of when using
        def wrapper(username, password):
            return get_winrm_connection(ip=self.ip, port='5985', username=username, password=password)
        setattr(obj, 'get_connection', wrapper)
