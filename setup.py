import re
from os import path

from setuptools import find_packages, setup

ROOT = path.dirname(__file__)
NAME = 'bigfish'
DESCRIPTION = 'Bigfish backend application'


def read_requirements(filename):
    full_path = path.join(ROOT, filename)
    requirements = []
    with open(full_path, 'rb') as fo:
        for line in fo:
            line = line.decode('utf-8').strip()
            if line:
                requirements.append(line)
    return requirements


def get_version():
    init_file = path.join(ROOT, NAME, '__init__.py')
    pattern = re.compile("__version__ = '(?P<ver>.*?)'")
    with open(init_file, 'r') as fo:
        for line in fo:
            match = pattern.match(line)
            if match:
                return match.group('ver')
    return None


def get_packages():
    pkgs = [
        NAME + '.' + pkg
        for pkg in find_packages(NAME, exclude=['*.tests'])
    ]
    return [NAME] + pkgs


REQS = read_requirements('requirements/requirements.txt')
REQS_DEV = read_requirements('requirements/requirements-dev.txt')

setup(
    name=NAME,
    version=get_version(),
    description=DESCRIPTION,
    install_requires=REQS,
    tests_require=REQS_DEV,
    test_suite='runtests.runtests',
    packages=get_packages(),
    # include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'License :: Other/Proprietary License',
        'Framework :: Django',
    ],
    scripts=[
        path.join('scripts', 'manage.py'),
        path.join('scripts', 'wait_for_psql.py'),
    ]
)
