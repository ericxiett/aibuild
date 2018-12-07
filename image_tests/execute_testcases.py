import sys

from image_tests.testcases import generic_test_cases

LINUX_LIST = ['centos', 'ubuntu', 'debian', 'opensuse']

def main():
    if len(sys.argv) < 7:
        print('Please input image/extended_size/distro/version/user/pass!')
        exit(1)

    image = sys.argv[1]
    extended_size = sys.argv[2]
    distro = sys.argv[3]
    version = sys.argv[4]
    username = sys.argv[5]
    password = sys.argv[6]

    if distro.lower() in LINUX_LIST:
        testcases = generic_test_cases.GenericLinuxTestCases(
            image, extended_size, distro, version,
            username, password
        )
        testcases._prepare()
        testcases.test_case_validate_ssh_creds()
        testcases.test_case_validate_disk_extend()
        testcases.test_case_validate_version()


if __name__ == '__main__':
    sys.exit(main())
