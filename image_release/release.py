import argparse
import json
import os
import random
import string
import sys

import requests
from glanceclient import Client
from keystoneauth1 import loading, session


def get_glance_client(auth_info):
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(
        auth_url=auth_info.get('auth_url'),
        username=auth_info.get('username'),
        password=auth_info.get('password'),
        project_name=auth_info.get('project_name'),
        user_domain_name=auth_info.get('user_domain_name'),
        project_domain_name=auth_info.get('project_domain_name')
    )
    sess = session.Session(auth=auth)
    return Client('2', session=sess)


class ReleaseAction(object):

    def __init__(self, image_name, env_name):
        '''
        Release action
        :param image: image_name, like ubuntu1604x86_64_20181128_1.qcow2
        :param env: name of env, like cprdenv
        '''
        self.api_server = 'http://aibuild-server.com'
        self.image_name = image_name
        self.env_name = env_name

    def execute(self):
        gc = self._get_glance_client()
        # Get image info
        image_info = self._get_image_info()
        # Image name format: ubuntu1604x86_64_20181128_1.qcow2
        name = self._gen_image_properties(image_info)
        image = gc.images.create(
            name=name,
            disk_format='raw', # Ceph use raw
            container_format='bare',
            visibility='public',
            property=image_info
        )
        # Get image and convert qcow2 to raw
        raw_image = self._get_and_convert_image(image_info.get('get_url'))
        gc.images.upload(image.id, open(raw_image, 'rb'))
        # Record release log
        self._record_release_log(image)


    def _gen_image_properties(self, image_info):
        first_pos = self.image_name.index('_')
        second_pos = self.image_name.index('_',
                                           first_pos + 1,
                                           len(self.image_name))
        third_pos = self.image_name.index('_',
                                          second_pos + 1,
                                          len(self.image_name))
        name = self.image_name[:second_pos]
        image_info['build_at'] = self.image_name[second_pos + 1:third_pos]
        image_info['build_number'] = self.image_name[third_pos + 1:].split('.')[0]
        print('name: %s, date: %s, build number: %s' %
              (name, image_info['build_at'],
               image_info['build_number']))
        return name

    def _get_glance_client(self):
        url = self.api_server + '/v1/env'
        resp = requests.get(url, self.env_name)
        print(resp.json())
        return get_glance_client(json.loads(resp.json()))

    def _get_image_info(self):
        url = self.api_server + '/v1/build'
        resp = requests.get(url, self.image_name)
        print('image: %s' % resp.json())
        build_dict = json.loads(resp.json())
        os_name = build_dict.get('os_name')
        url_g = self.api_server + '/v1/guestos'
        resp_g = requests.get(url_g, os_name)
        print('guest os: %s' % resp_g.json())
        guestos_dict = json.loads(resp_g.json())
        return dict(
            os_type=guestos_dict.get('type'),
            os_distro=guestos_dict.get('distro'),
            os_version=guestos_dict.get('version'),
            architecture='x86_64',
            get_url=build_dict.get('get_url'),
            updates=build_dict.get('update_contents'),
            builder='aibuild',
            aibuild_imgid=build_dict.get('id')
        )

    def _get_and_convert_image(self, url):
        ran_str = ''.join(random.sample(string.ascii_letters, 8))
        tmp_dir = '/tmp/' + ran_str
        file_name = url.split('/')[-1]
        r = requests.get(url, stream=True)
        dest_file = tmp_dir+'/'+file_name
        with open(dest_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=10*1024*1024):
                f.write(chunk)
        os.chdir(tmp_dir)
        raw_name = file_name.split('.')[0] + '.raw'
        cmd = 'qemu-img convert -O raw ' + file_name + ' ' + \
            raw_name
        os.system(cmd)
        return tmp_dir + '/' + raw_name

    def _record_release_log(self, image):
        url = self.api_server + '/v1/release'
        body = {
            'env_name': self.env_name,
            'glance_id': image.id,
        }
        resp = requests.post(url, data=body)
        print('resp: %s' % resp.text)
        if resp.status_code != '200':
            print('Failed to record release log %s!' % body)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('env_name')
    parser.add_argument('image_name')

    args = parser.parse_args()
    print('args: %s' % args)
    release_action = ReleaseAction(args.image_name, args.env_name)
    release_action.execute()


if __name__ == '__main__':
    sys.exit(main())
