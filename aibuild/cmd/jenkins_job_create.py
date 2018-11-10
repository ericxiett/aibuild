import sys

import jenkins


def main():

    server = jenkins.Jenkins('http://10.110.26.167:49001', username='admin', password='Lc13yfwpW')
    user = server.get_whoami()
    version = server.get_version()
    print('Hello %s from Jenkins %s' % (user['fullname'], version))


if __name__ == '__main__':
    sys.exit(main())
