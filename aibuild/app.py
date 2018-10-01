import os

from pecan.deploy import deploy

from aibuild.common.config import CONF

CONFIG_PATH = 'pecan_config_path'

# fix pecan configuration name
config_path = CONF.get('DEFAULT', CONFIG_PATH)
application = deploy(os.path.abspath(config_path))
