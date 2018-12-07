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
            "image_name": "ubuntu1604x86_64_20181128_1.qcow2",
            "os_name": "ubuntu1604",
            "update_contents": "Add cloud-init"
            "get_url": "http://10.110.19.1/images/ubuntu1604/ubuntu1604x86_64_20181128_1.qcow2"
        }
        :return: image_uuid: UUID of image
        :raise:
        """
        if not build_log.get('image_name'):
            LOG.error("Invalid image name")
            raise Exception(message='Null image name')

        image_name = build_log.get('image_name')
        session = sessionmaker(bind=self.engine)()
        build_log = session.query(models.ImageBuildLog).filter_by(
            image_name=image_name).first()
        log_id = str(uuid.uuid4())
        if not build_log:
            session.add(models.ImageBuildLog(
                id=log_id,
                image_name=image_name,
                os_name=build_log.get('os_name'),
                update_contents=build_log.get('update_contents'),
                get_url=build_log.get('get_url'),
                build_at=datetime.datetime.now()
            ))
            session.commit()
            session.close()

        return log_id if not build_log else build_log.id

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

        session.add(models.EnvInfo(
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

    def get_test_image_by_uuid(self, image_uuid):
        session = sessionmaker(bind=self.engine)()
        try:
            image_info = session.query(models.ImageTestLog).filter_by(
                image_uuid=image_uuid).first()
        except sqlalchemy.orm.exc.NoResultFound as e:
            image_info = None
        session.close()
        return image_info

    def create_guestos(self, kwargs):
        name = kwargs.get('name')
        guestos_id = str(uuid.uuid4())
        session = sessionmaker(bind=self.engine)()
        guestos = session.query(models.GuestOS).filter_by(
                name=name).first()
        if not guestos:
            session.add(models.GuestOS(
                id=guestos_id,
                name=kwargs.get('name'),
                base_iso=kwargs.get('base_iso'),
                type=kwargs.get('type'),
                distro=kwargs.get('distro'),
                version=kwargs.get('version')
            ))
            session.commit()
            session.close()
        return guestos_id if not guestos else guestos.id

    def create_test_log(self, kwargs):
        log_id = str(uuid.uuid4())
        image_name = kwargs.get('image_name')
        case_name = kwargs.get('case_name')
        result = kwargs.get('result')
        test_at = datetime.datetime.now()
        session = sessionmaker(bind=self.engine)()
        if not (image_name or case_name or result):
            session.add(models.ImageTestLog(
                id=log_id,
                image_name=image_name,
                case_name=case_name,
                result=result,
                test_at=test_at
            ))
            session.commit()
            session.close()
            return log_id
        return None
