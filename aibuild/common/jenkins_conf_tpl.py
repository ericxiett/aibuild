from jinja2 import Template

from aibuild.common.config import CONF

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
        <hudson.model.StringParameterDefinition>
          <name>WEB_SERVER</name>
          <description></description>
          <defaultValue>{{ web_server }}</defaultValue>
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
