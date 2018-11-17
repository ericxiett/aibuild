from templates.test_context import context
import logging
from time import sleep

logging_format = "%(asctime)s - %(name)s.%(lineno)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=logging_format)


@context.WinrmLibvirtContext("sjt-test.domain",
                             "/home/sjt/py-winrm/src/aibuild/templates/windows10pro/tests/win-test.qcow2")
class TestCases(object):
    """
    demo test case
    """

    def __init__(self):
        self.conn = None
        self.logger = logging.getLogger(__name__)

    def init(self, *args, **kwargs):
        """
        init parameters
        :param args:
        :param kwargs:
        :return:
        """
        times = 5
        self.logger.debug('show get_connection function: %s', self.get_connection)
        while times >= 0:
            self.logger.info("start connecting to domain")
            try:
                self.conn = self.get_connection('administrator', '123456a?')
                sleep(60)
            except Exception as e:
                self.logger.error("there is something wrong %s when call method %s", e, self.get_connection)
            times -= 1

    @context.test
    def test_one(self):
        cmd = 'echo hello'
        self.conn.run_cmd(cmd)
        pass
