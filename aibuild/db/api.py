import datetime
import uuid

import sqlalchemy
from sqlalchemy.orm import sessionmaker

from aibuild.common.config import CONF
from aibuild.common.log_utils import LOG
from aibuild.db import models


class API(object):

    def __init__(self):
        super(API, self).__init__()
        url = CONF.get('DEFAULT', 'db_connection')
        self.engine = sqlalchemy.create_engine(url)

    def add_build_log(self, build_log):
        """
        Add build log to database
        :param kwargs: a dict object
        example:
        {
            "image_name": "ubuntu1604x86_64.qcow2",
            "os_type": "Linux",
            "os_distro": "ubuntu"
            "os_ver": "16.04",
            "from_iso": "http://releases.ubuntu.com/16.04/ubuntu-16.04.5-server-amd64.iso",
            "update_contents": "Add cloud-init"
        }
        :return: image_uuid: UUID of image
        :raise:
        """
        if not build_log.get('image_name'):
            LOG.error("Invalid image name")
            raise Exception

        session = sessionmaker(bind=self.engine)()

        image_uuid = str(uuid.uuid4())

        session.add(models.ImageBuildLog(
            image_uuid=image_uuid,
            image_name=build_log.get('image_name'),
            os_type=build_log.get('os_type'),
            os_distro=build_log.get('os_distro'),
            os_ver=build_log.get('os_ver'),
            from_iso=build_log.get('from_iso'),
            update_contents=build_log.get('update_contents'),
            build_at=datetime.datetime.now()
        ))
        session.commit()
        session.close()

        return image_uuid

    def add_new_env_info(self, env_info):
        """
        Add env info to database
        :param env_info: a dict object
        example:
        {
            "image_name": "ubuntu1604x86_64.qcow2",
            "os_type": "Linux",
            "os_distro": "ubuntu"
            "os_ver": "16.04",
            "from_iso": "http://releases.ubuntu.com/16.04/ubuntu-16.04.5-server-amd64.iso",
            "update_contents": "Add cloud-init"
        }
        :return: env_uuid: UUID of env
        :raise:
        """
        session = sessionmaker(bind=self.engine)()

        env_uuid = str(uuid.uuid4())

        session.add(models.OpenStackEnvInfo(
            env_uuid=env_uuid,
            auth_url=env_info.get('auth_url'),
            project_domain_name=env_info.get('project_domain_name'),
            user_domain_name=env_info.get('user_domain_name'),
            project_name=env_info.get('project_name'),
            username=env_info.get('username'),
            password=env_info.get('password'),
            region=env_info.get('region')
        ))
        session.commit()
        session.close()

        return env_uuid
