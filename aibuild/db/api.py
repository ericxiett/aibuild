import json
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
            "os_type": "Linux_Ubuntu",
            "os_ver": "16.04",
            "from_iso": "http://releases.ubuntu.com/16.04/ubuntu-16.04.5-server-amd64.iso",
            "update_contents": "Add cloud-init"
        }
        :return: image_uuid: UUID of image
        :raise:
        """
        session = sessionmaker(bind=self.engine)()
        image_uuid = str(uuid.uuid4())

        session.add(models.ImageBuildLog(
            image_uuid=image_uuid,
            image_name=build_log.get('image_name'),
            os_type=build_log.get('os_type'),
            os_ver=build_log.get('os_ver'),
            from_iso=build_log.get('from_iso'),
            update_contents=build_log.get('update_contents')
        ))
        session.commit()
        session.close()

        return image_uuid
