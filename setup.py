# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='aibuild',
    version='0.1',
    description='Automate to build GuestOS images(AIBuild)',
    author='Eric Xie',
    author_email='eric_xiett@163.com',
    install_requires=[
        "pecan",
        "sqlalchemy"
    ],
    test_suite='aibuild',
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(exclude=['ez_setup'])
)
