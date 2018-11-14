import sys

import gitlab


AIBUILD_GROUP = 'aibuild'
ACCESS_TOKEN = 'rxrcsJ_V1brzrc3sszrk'
SUPPORT_TPLS = [
    'centos65',
    'centos68',
    'centos69',
    'centos71',
    'centos72',
    'centos73',
    'centos74',
]
GITLAB_SERVER = 'http://10.110.19.150:49011/'

def create_aibuild_group(gl):
    groups = gl.groups.list()
    for gr in groups:
        if gr.name == AIBUILD_GROUP:
            return gr

    # Create if non exist
    return gl.groups.create({'name': AIBUILD_GROUP, 'path': AIBUILD_GROUP})


def create_projects(gl, aibuild_group):
    existed_projects = []
    for pr in gl.projects.list():
        existed_projects.append(pr.name)

    projects = []
    for tpl in SUPPORT_TPLS:
        name = tpl + '-tpl'
        if name not in existed_projects:
            project = gl.projects.create({'name': name, 'namespace_id': aibuild_group.id})
        else:
            project = gl.projects.get(AIBUILD_GROUP+'/'+name)
        projects.append(project)

    return projects


def display_projects(projects):
    print('===============================')
    for pr in projects:
        line = pr.name + ': ' + GITLAB_SERVER + pr.name + '.git'
        print(line)


def main():

    gl = gitlab.Gitlab(GITLAB_SERVER, private_token='rxrcsJ_V1brzrc3sszrk')

    # Create group aibuild
    aibuild_group = create_aibuild_group(gl)

    # Create projects
    projects = create_projects(gl, aibuild_group)

    # Display results
    display_projects(projects)


if __name__ == '__main__':
    sys.exit(main())
