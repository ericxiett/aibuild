import sys

import gitlab


AIBUILD_GROUP = 'aibuild'
SUPPORT_TPLS = [
    'centos65',
    'centos68',
    'centos69',
    'centos71',
    'centos72',
    'centos73',
    'centos74',
]

def create_aibuild_group(gl):
    groups = gl.groups.list()
    for gr in groups:
        if gr.name == AIBUILD_GROUP:
            return gr

    # Create if non exist
    return gl.groups.create({'name': AIBUILD_GROUP, 'path': AIBUILD_GROUP})


def create_projects(gl, aibuild_group):
    projects = []
    for tpl in SUPPORT_TPLS:
        name = tpl + '-tpl'
        project = gl.projects.create({'name': name, 'namespace_id': aibuild_group})
        projects.append(project)

    return projects


def display_projects(projects):
    print('===============================')
    for pr in projects:
        line = pr.name + ': ' +
        print()


def main():
    gl = gitlab.Gitlab('http://10.110.19.150:49011', email='root', password='Lc13yfwpW')

    # Create group aibuild
    aibuild_group = create_aibuild_group(gl)

    # Create projects
    projects = create_projects(gl, aibuild_group)

    # Display results
    display_projects(projects)


if __name__ == '__main__':
    sys.exit(main())
