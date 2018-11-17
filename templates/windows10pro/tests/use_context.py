from templates.test_context import context
import logging

logging_format = "%(asctime)s - %(name)s.%(lineno)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=logging_format)


@context.WinrmLibvirtContext("sjt-test.domain", "path/to/image")
class TestCases(object):
    """
    demo test case
    """

    def __init__(self):
        self.conn = None

    def init(self, *args, **kwargs):
        self.conn = self.get_connection('ip', 5985, 'username', 'password')

    @context.test
    def test_one(self):
        cmd = 'echo hello'
        self.conn.run_cmd(cmd)
        pass
