import random

import gitlab
import jenkins
from jinja2 import Template
from pecan import rest, expose

from aibuild.common.config import CONF
from aibuild.common.jenkins_conf_tpl import CONF_TEMPLATE
from aibuild.common.log_utils import LOG
from aibuild.db import api


class GuestOSController(rest.RestController):

    def __init__(self):
        self.db_api = api.API()
        self.gitlab = gitlab.Gitlab(
            CONF.get('DEFAULT', 'gitlab_server'),
            private_token=CONF.get('DEFAULT', 'access_token_gitlab')
        )
        self.aibuild_group = self._create_group('aibuild')
        self.jenkins = jenkins.Jenkins(
            CONF.get('DEFAULT', 'jenkins_server'),
            username=CONF.get('DEFAULT', 'jenkins_user'),
            password=CONF.get('DEFAULT', 'jenkins_password')
        )

    @expose('json')
    def post(self, **kwargs):
        LOG.info('Get post request %s', kwargs)

        if self._missing_value(kwargs):
            return dict(status=400, message='Miss required field')

        try:
            guestos_id = self.db_api.create_guestos(kwargs)
            self._create_project(kwargs.get('name'))
            self._create_job(kwargs)
            self._add_webhook(kwargs)
        except Exception as e:
            LOG.info('Got error %s', e)
            return dict(status=500, message=e.message)

        kwargs['id'] = guestos_id
        return dict(status=200, **kwargs)

    def _missing_value(self, kwargs):
        required_value = ['name', 'base_iso',
                          'type', 'distro', 'version']
        for k in required_value:
            if k not in kwargs.keys():
                LOG.info('Missing value %s', k)
                return True

        return False

    def _create_group(self, group):
        groups = self.gitlab.groups.list()
        for gr in groups:
            if gr.name == group:
                return gr

        return self.gitlab.groups.create({'name': group, 'path': group})

    def _create_project(self, prefix):
        existed_projects = []
        for pr in self.gitlab.projects.list():
            existed_projects.append(pr.name)

        project_name = prefix + '_tpl'
        if project_name not in existed_projects:
            self.gitlab.projects.create(
                {'name': project_name,
                 'namespace_id': self.aibuild_group.id})

    def _create_job(self, kwargs):
        job_name = 'image_build_' + kwargs.get('name')
        web_server = CONF.get('DEFAULT', 'web_server')
        conf_xml = self._render_conf(job_name,
                                     kwargs.get('base_iso'),
                                     web_server)
        self.jenkins.create_job(job_name, conf_xml)

    def _render_conf(self, job_name, base_iso, web_server):
        template = Template(CONF_TEMPLATE)
        isos_url = base_iso
        gitlab_server = CONF.get('DEFAULT', 'gitlab_server')
        git_url = gitlab_server + '/aibuild/' + job_name.split('_')[2] + '_tpl.git'
        worker = self._choose_worker()
        return template.render(isos_url=isos_url, git_url=git_url,
                               worker=worker, web_server=web_server)

    def _choose_worker(self):
        nodes = self.jenkins.get_nodes()
        workers = []
        for node in nodes:
            name = node.get('name')
            if name != 'master':
                workers.append(name)

        if len(workers) == 0:
            raise Exception(message='No worker node found')
        else:
            return random.choice(workers)

    def _add_webhook(self, kwargs):
        job_name = 'image_build_'+ kwargs.get('name')
        project_name = kwargs.get('name') + '_tpl'
        project = self.gitlab.projects.get('aibuild' + '/' + project_name)
        url = CONF.get('DEFAULT', 'jenkins_server') + '/project/' + job_name
        return project.hooks.create({'url': url, 'push_events': 1})
