import sys

import requests


def print_helper():
    print('=' * 60)
    print('Welcome to use this script to release image to env')
    print('    arg 0: this script')
    print('    arg 1: image that will be released')
    print('    arg 2: env where image will be released')
    print()


def get_env_info(env_name):
    get_url = 'http://aibuild-server.com:9753/v1/env'
    parameters = {
        'env_name': env_name
    }
    response = requests.get(get_url, params=parameters)
    print('[dbg]response: %s' % response)

    if response.status_code == '200':
        return response.content
    else:
        return None


def check_env(env):
    # TODO: 1 Test link info between release node and web server

    # TODO: 2 Check glance API call
    pass


def release_image_to_env():
    # TODO: 1. Upload image to env by calling glance api

    # TODO: 2. Record on db by calling aibuild release api
    pass


def get_image_info(image):
    # TODO: 1. Get info through API.

    # TODO: 2. if 1 OK, check file if exists
    pass


def main():
    print('Welcome to use this script to release image to env...')

    if len(sys.argv) < 3:
        print_helper()
        exit(1)

    image = sys.argv[1]
    image_info = get_image_info(image)
    if not image_info:
        print('Can not find the image by name, please check if correct!')
        exit(1)

    env_name = sys.argv[2]
    env_info = get_env_info(env_name)
    if not env_info:
        print('Can not find the env by name, please check if correct!')
        exit(1)

    if check_env(env_info):
        release_image_to_env()


if __name__ == '__main__':
    sys.exit(main())
