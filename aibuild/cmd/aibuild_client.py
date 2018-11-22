import os

import requests
import sqlalchemy
import sys

import argparse

import xlrd

from aibuild.common.config import CONF
from aibuild.db import models


def args(*args, **kwargs):
    def _decorator(func):
        func.__dict__.setdefault('args', []).insert(0, (args, kwargs))
        return func
    return _decorator


class Dbcommands(object):

    def create(self):
        print('This operation is DANGEROUS. Please backup database first!!!')
        url = CONF.get('DEFAULT', 'db_connection')
        print('url: %s' % url)
        engine = sqlalchemy.create_engine(url, echo=True)
        # Clean
        models.Base.metadata.drop_all(engine)
        models.Base.metadata.create_all(engine)


class Envcommands(object):

    @args('file', metavar='<FILE>', help='Xls file that contains info of envs.')
    def register(self, file=None):
        if not file or not os.path.exists(file):
            print('Please input valid file!')
            return

        book = xlrd.open_workbook(file)
        sh = book.sheet_by_name('envs')
        for row in range(1, sh.nrows):

            url = CONF.get('DEFAULT', 'api_server') + '/env'
            data = {
                'env_name': sh.cell_value(row, 1),
                'auth_url': sh.cell_value(row, 2),
                'project_domain_name': sh.cell_value(row, 3),
                'user_domain_name': sh.cell_value(row, 4),
                'project_name': sh.cell_value(row, 5),
                'username': sh.cell_value(row, 6),
                'password': sh.cell_value(row, 7),
                'region': sh.cell_value(row, 8)
            }
            res = requests.post(url, data=data)
            print('%s: %s' % (row, res.text))
            if res.status_code != '200':
                print('Failed to register %s env!' % sh.cell_value(row, 1))
                continue

        print('End registering env info!')


CATEGORIES = {
    'db': Dbcommands,
    'env': Envcommands
}


def methods_of(obj):
    result = []
    for i in dir(obj):
        if callable(getattr(obj, i)) and not i.startswith('_'):
            result.append((i, getattr(obj, i)))
    return result


def fetch_func_args(func, matchargs):
    fn_args = []
    for args, kwargs in getattr(func, 'args', []):
        arg = args[0]
        fn_args.append(getattr(matchargs, arg))
    return fn_args


def main():
    top_parser = argparse.ArgumentParser(prog='aibuild')
    subparsers = top_parser.add_subparsers()
    for category in CATEGORIES:
        command_object = CATEGORIES[category]()
        category_parser = subparsers.add_parser(category)
        category_parser.set_defaults(command_object=command_object)
        category_subparsers = category_parser.add_subparsers(dest='action')
        for (action, action_fn) in methods_of(command_object):
            parser = category_subparsers.add_parser(action)
            action_kwargs = []
            for args, kwargs in getattr(action_fn, 'args', []):
                parser.add_argument(*args, **kwargs)
            parser.set_defaults(action_fn=action_fn)
            parser.set_defaults(action_kwargs=action_kwargs)

    match_args = top_parser.parse_args(sys.argv[1:])
    print('match_args: %s' % match_args)
    fn = match_args.action_fn
    fn_args = fetch_func_args(fn, match_args)
    fn(*fn_args)


if __name__ == '__main__':
    sys.exit(main())
