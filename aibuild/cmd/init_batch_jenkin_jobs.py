import random
import sys
import xml

import gitlab
import jenkins
from jinja2 import Template

GITLAB_SERVER = 'http://10.110.19.150:49011/'
AIBUILD_GROUP = 'aibuild'
JENKINS_SERVER = 'http://10.110.19.150:49001'
USERNAME = 'admin'
PASSWORD = 'Lc13yfwpW'
ISOS_URL = 'http://10.110.19.1/isos/'

WORK_JOBS = [
    'image_build_centos65',
    'image_build_centos68',
    'image_build_centos69',
    'image_build_centos71',
    'image_build_centos72',
    'image_build_centos73',
    'image_build_centos74',
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


def choose_worker(server):
    nodes = server.get_nodes()
    workers = []
    for node in nodes:
        name = node.get('name')
        if name != 'master':
            workers.append(name)

    if len(workers) == 0:
        return None
    else:
        return random.choice(workers)


def render_conf(job, server):
    template = Template(CONF_TEMPLATE)
    isos_url = ISOS_URL
    git_url = GITLAB_SERVER + 'aibuild/' + job.split('_')[2] + '-tpl.git'
    worker = choose_worker(server)
    return template.render(isos_url=isos_url, git_url=git_url, worker=worker)


def create_jobs(server):
    for job in WORK_JOBS:
        conf_xml = render_conf(job, server)
        server.create_job(job, conf_xml)


def display_jobs(server):
    print('===============================')
    for job in server.get_jobs():
        print('%s: %s' % (job.get('name'), job.get('url')))


def add_hook_on_gitlab(server):
    gl = gitlab.Gitlab(GITLAB_SERVER, private_token='rxrcsJ_V1brzrc3sszrk')

    hooks = []
    for job in server.get_jobs():
        job_name = job.get('name')
        # Gen project name of gitlab
        project_name = job_name.split('_')[2] + '-tpl'
        project = gl.projects.get(AIBUILD_GROUP+'/'+project_name)
        url = JENKINS_SERVER + '/project/' + job_name
        hook = project.hooks.create({
            'url': url,
            'push_events': 1
        })
        hooks.append(hook)

    return hooks


def main():

    server = jenkins.Jenkins(JENKINS_SERVER, username=USERNAME, password=PASSWORD)

    # Create jobs
    create_jobs(server)

    # Display jobs
    display_jobs(server)

    # Add hook on gitlab
    add_hook_on_gitlab(server)


if __name__ == '__main__':
    sys.exit(main())
