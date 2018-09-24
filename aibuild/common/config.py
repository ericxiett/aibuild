import ConfigParser

CONF_FILE = '/etc/aibuild/aibuild.conf'


def get_config(conf_file):
    config = ConfigParser.ConfigParser()
    config.read(conf_file)
    return config


CONF = get_config(CONF_FILE)
