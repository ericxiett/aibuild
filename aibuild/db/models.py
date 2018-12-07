import datetime

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class GuestOS(Base):
    __tablename__ = 'guestos'

    id = Column(String(36), primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(36), nullable=False)
    distro = Column(String(36), nullable=False)
    version = Column(String(36), nullable=False)
    base_iso = Column(String(255), nullable=False)

class ImageBuildLog(Base):
    __tablename__ = 'build_log'

    id = Column(String(36), primary_key=True, nullable=False)
    image_name = Column(String(255), nullable=False)
    os_name = Column(String(255), nullable=False)
    build_at = Column(DateTime, default=datetime.datetime.now())
    update_contents = Column(Text, nullable=True)
    get_url = Column(String(255), nullable=True)

class TestCases(Base):
    __tablename__ = 'testcases'

    id = Column(String(36), primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    os_type = Column(String(36), nullable=True)

class ImageTestLog(Base):
    __tablename__ = 'test_log'

    id = Column(String(36), primary_key=True, nullable=False)
    image_name = Column(String(36), nullable=False)
    case_name = Column(String(255), nullable=False)
    result = Column(String(10), nullable=False)
    test_at = Column(DateTime, default=datetime.datetime.now())

class ImageReleaseLog(Base):
    __tablename__ = 'release_log'

    id = Column(String(36), primary_key=True, nullable=False)
    env_id = Column(String(60), nullable=True)
    glance_id = Column(String(36), nullable=True)
    release_at = Column(DateTime, default=datetime.datetime.now())

class EnvInfo(Base):
    __tablename__ = 'envs'

    id = Column(String(36), primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    auth_url = Column(String(255), nullable=False)
    project_domain_name = Column(String(64), nullable=False)
    user_domain_name = Column(String(64), nullable=False)
    project_name = Column(String(64), nullable=False)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    region = Column(String(255), nullable=False)
