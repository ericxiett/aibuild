import datetime

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ImageBuildLog(Base):
    __tablename__ = 'build_log'

    image_uuid = Column(String(36), primary_key=True, nullable=False)
    image_name = Column(String(255), nullable=True)
    os_type = Column(String(20), nullable=True)
    os_distro = Column(String(20), nullable=True)
    os_ver = Column(String(10), nullable=True)
    build_at = Column(DateTime, default=datetime.datetime.now())
    from_iso = Column(String(255), nullable=True)
    update_contents = Column(Text, nullable=True)
    get_url = Column(String(255), nullable=True)

class ImageValidateLog(Base):
    __tablename__ = 'validate_log'

    image_uuid = Column(String(36), primary_key=True, nullable=False)
    validate_case = Column(String(255), nullable=True)
    validate_result = Column(String(10), nullable=True)
    validate_at = Column(DateTime, default=datetime.datetime.now())
    get_url = Column(String(255), nullable=True)

class ImageReleaseLog(Base):
    __tablename__ = 'release_log'

    image_uuid = Column(String(36), primary_key=True, nullable=False)
    openstack_cluster = Column(String(60), nullable=True)
    glance_id = Column(String(36), nullable=True)
    release_at = Column(DateTime, default=datetime.datetime.now())
    get_url = Column(String(255), nullable=True)

class OpenStackEnvInfo(Base):
    __tablename__ = 'openstack_env'

    env_uuid = Column(String(36), primary_key=True, nullable=False)
    auth_url = Column(String(255), nullable=True)
    project_domain_name = Column(String(64), nullable=True)
    user_domain_name = Column(String(64), nullable=True)
    project_name = Column(String(64), nullable=True)
    username = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    region = Column(String(255), nullable=True)
