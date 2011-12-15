import os
from setuptools import setup, find_packages

from settings_inspector import VERSION

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
    
requirements = [
    'django'
]

setup(
    name = "Django Settings Inspector",
    version = ".".join(map(str, VERSION)),
    description = "",
    long_description = read('README.rst'),
    url = '',
    license = 'MIT',
    author = 'Flavio Curella',
    author_email = 'flavio.curella@curella.org',
    packages = find_packages(exclude=['tests']),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    install_requires = requirements,
    test_suite = "nose.collector",
)
