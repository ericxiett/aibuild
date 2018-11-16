import random
import sys

import gitlab
import jenkins
from jinja2 import Template

from aibuild.common.config import CONF

VALID_SUBCMDS = ['init', 'clean']
SUPPORT_DISTROS = [
    'centos65',
    'centos68',
]
CONF_TEMPLATE = '''<?xml version='1.1' encoding='UTF-8'?>
<project>
  <description></description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <com.dabsquared.gitlabjenkins.connection.GitLabConnectionProperty plugin="gitlab-plugin@1.5.10">
      <gitLabConnection></gitLabConnection>
    </com.dabsquared.gitlabjenkins.connection.GitLabConnectionProperty>
    <hudson.model.ParametersDefinitionProperty>
      <parameterDefinitions>
        <hudson.model.StringParameterDefinition>
          <name>ISOS_URL</name>
          <description></description>
          <defaultValue>{{ isos_url }}</defaultValue>
          <trim>false</trim>
        </hudson.model.StringParameterDefinition>
      </parameterDefinitions>
    </hudson.model.ParametersDefinitionProperty>
  </properties>
  <scm class="hudson.plugins.git.GitSCM" plugin="git@3.9.1">
    <configVersion>2</configVersion>
    <userRemoteConfigs>
      <hudson.plugins.git.UserRemoteConfig>
        <url>{{ git_url }}</url>
        <credentialsId>gitlab_root_cred</credentialsId>
      </hudson.plugins.git.UserRemoteConfig>
    </userRemoteConfigs>
    <branches>
      <hudson.plugins.git.BranchSpec>
        <name>*/master</name>
      </hudson.plugins.git.BranchSpec>
    </branches>
    <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
    <submoduleCfg class="list"/>
    <extensions/>
  </scm>
  <assignedNode>{{ worker }}</assignedNode>
  <canRoam>false</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers>
    <com.dabsquared.gitlabjenkins.GitLabPushTrigger plugin="gitlab-plugin@1.5.10">
      <spec></spec>
      <triggerOnPush>true</triggerOnPush>
      <triggerOnMergeRequest>true</triggerOnMergeRequest>
      <triggerOnPipelineEvent>false</triggerOnPipelineEvent>
      <triggerOnAcceptedMergeRequest>false</triggerOnAcceptedMergeRequest>
      <triggerOnClosedMergeRequest>false</triggerOnClosedMergeRequest>
      <triggerOnApprovedMergeRequest>true</triggerOnApprovedMergeRequest>
      <triggerOpenMergeRequestOnPush>never</triggerOpenMergeRequestOnPush>
      <triggerOnNoteRequest>true</triggerOnNoteRequest>
      <noteRegex>Jenkins please retry a build</noteRegex>
      <ciSkip>true</ciSkip>
      <skipWorkInProgressMergeRequest>true</skipWorkInProgressMergeRequest>
      <setBuildDescription>true</setBuildDescription>
      <branchFilterType>All</branchFilterType>
      <includeBranchesSpec></includeBranchesSpec>
      <excludeBranchesSpec></excludeBranchesSpec>
      <sourceBranchRegex></sourceBranchRegex>
      <targetBranchRegex></targetBranchRegex>
      <secretToken>{AQAAABAAAAAQ5yyi3R605vUnz1hezbz5vzLg9T5DsqVSntB3AMpwk10=}</secretToken>
      <pendingBuildName></pendingBuildName>
      <cancelPendingBuildsOnUpdate>false</cancelPendingBuildsOnUpdate>
    </com.dabsquared.gitlabjenkins.GitLabPushTrigger>
  </triggers>
  <concurrentBuild>false</concurrentBuild>
  <builders>
    <hudson.tasks.Shell>
      <command>#!/bin/bash

cd $WORKSPACE
chmod +x builders/build_image.sh
builders/build_image.sh</command>
    </hudson.tasks.Shell>
  </builders>
  <publishers/>
  <buildWrappers/>
</project>
'''

def print_helper():
    print('=' * 60)
    print('  Welcome to use this script to work with gitlab and jenkins')
    print('    init: Create projects and jobs')
    print('    clean: Delete all projects and jobs. Dangerous!')
    print('=' * 60)


class GitlabInitWorks(object):

    def __init__(self, gitlab_server):
        super(GitlabInitWorks, self).__init__()
        self.gl = gitlab_server

    def init_works(self):
        self.aibuild_group = self._create_group('aibuild')
        self._create_projects()
        self._display_projects()

    def _create_group(self, group):
        groups = self.gl.groups.list()
        for gr in groups:
            if gr.name == group:
                return gr

        # Create if non exist
        return self.gl.groups.create({'name': group, 'path': group})

    def _create_projects(self):
        existed_projects = []
        for pr in self.gl.projects.list():
            existed_projects.append(pr.name)

        for tpl in SUPPORT_DISTROS:
            name = tpl + '-tpl'
            group_id = self.aibuild_group.id
            if name not in existed_projects:
                self.gl.projects.create({'name': name, 'namespace_id': group_id})

    def _display_projects(self):
        print('===============================')
        projects = self.gl.projects.list()
        gitlab_server = CONF.get('DEFAULT', 'gitlab_server')
        for pr in projects:
            line = pr.name + ': ' + gitlab_server + '/' + pr.name + '.git'
            print(line)

    def clean_works(self):
        for project in self.gl.projects.list():
            project.delete()
        for group in self.gl.groups.list():
            group.delete()


class JenkinsInitWorks(object):

    def __init__(self, jenkins_server, gitlab_server):
        super(JenkinsInitWorks, self).__init__()
        self.jk = jenkins_server
        self.gl = gitlab_server

    def init_works(self):
        self._create_jobs()
        self._display_jobs()
        self._add_hook_on_gitlab()

    def _create_jobs(self):
        for dis in SUPPORT_DISTROS:
            job_name = 'image_build_' + dis
            conf_xml = self._render_conf(job_name)
            self.jk.create_job(job_name, conf_xml)

    def _render_conf(self, job_name):
        template = Template(CONF_TEMPLATE)
        isos_url = CONF.get('DEFAULT', 'isos_url')
        gitlab_server = CONF.get('DEFAULT', 'gitlab_server')
        git_url = gitlab_server + '/aibuild/' + job_name.split('_')[2] + '-tpl.git'
        worker = self._choose_worker()
        return template.render(isos_url=isos_url, git_url=git_url, worker=worker)

    def _choose_worker(self):
        nodes = self.jk.get_nodes()
        workers = []
        for node in nodes:
            name = node.get('name')
            if name != 'master':
                workers.append(name)

        if len(workers) == 0:
            return None
        else:
            return random.choice(workers)

    def _display_jobs(self):
        print('===============================')
        for job in self.jk.get_jobs():
            print('%s: %s' % (job.get('name'), job.get('url')))

    def _add_hook_on_gitlab(self):
        hooks = []
        for job in self.jk.get_jobs():
            job_name = job.get('name')
            # Gen project name of gitlab
            project_name = job_name.split('_')[2] + '-tpl'
            project = self.gl.projects.get('aibuild' + '/' + project_name)
            url = CONF.get('DEFAULT', 'jenkins_server') + '/project/' + job_name
            hook = project.hooks.create({
                'url': url,
                'push_events': 1
            })
            hooks.append(hook)

        return hooks

    def clean_works(self):
        for job in self.jk.get_jobs():
            self.jk.delete_job(job.get('name'))


def init_works():
    gl, jk = get_servers()

    # Create projects on gitlab
    print('Create projects of gitlab and display...')
    gl_obj = GitlabInitWorks(gl)
    gl_obj.init_works()

    # Create jobs on jenkins
    print('Create jobs of jenkins and display...')
    jk_obj = JenkinsInitWorks(jk, gl)
    jk_obj.init_works()


def clean_works():
    gl, jk = get_servers()
    GitlabInitWorks(gl).clean_works()
    JenkinsInitWorks(jk, gl).clean_works()


def get_servers():
    gitlab_server = CONF.get('DEFAULT', 'gitlab_server')
    access_token = CONF.get('DEFAULT', 'access_token_gitlab')
    print('Gitlab server %s access token %s' % (gitlab_server, access_token))
    gl = gitlab.Gitlab(gitlab_server, private_token=access_token)

    jenkins_server = CONF.get('DEFAULT', 'jenkins_server')
    jenkins_user =  CONF.get('DEFAULT', 'jenkins_user')
    jenkins_password =  CONF.get('DEFAULT', 'jenkins_password')
    print('Jenkins server %s user %s passwd %s' % (jenkins_server, jenkins_user, jenkins_password))
    jk = jenkins.Jenkins(jenkins_server, username=jenkins_user, password=jenkins_password)

    return gl, jk


def main():
    if len(sys.argv) < 2:
        print_helper()
        return 0

    subcmd = sys.argv[1]
    if subcmd not in VALID_SUBCMDS:
        print('Please input valid subcmd: %s' % VALID_SUBCMDS)
        return 1

    if subcmd == 'init':
        init_works()
    else:
        clean_works()

    return 0


if __name__ == '__main__':
    sys.exit(main())
