from templates.test_context import context
import logging
from time import sleep

logging_format = "%(asctime)s - %(name)s.%(lineno)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=logging_format)


@context.SshLibvirtContext("sjt-test.centos.domain")
class TestCases(object):
    """
    demo test case
    """

    def __init__(self):
        self.conn = None
        self.logger = logging.getLogger(__name__)

    @context.before
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
                self.conn = self.get_connection('root', 'Lc13yfwpW')

                # trigger some actions, make sure connection is ok
                self.conn.exec_command('echo hello')
                break
            except Exception as e:
                self.logger.error("there is something wrong %s when call method %s", e, self.get_connection)
                sleep(60)
            times -= 1

        if not self.conn:
            raise Exception('Init Connection failed')

    @context.test
    def test_one(self):
        cmd = 'df -h'
        stdin, stdout, stderr = self.conn.exec_command(cmd)
        
        for line in stdout:
           self.logger.debug('test result [%s]', line)

