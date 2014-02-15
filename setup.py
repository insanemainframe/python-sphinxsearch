import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
requires = open(os.path.join(here, 'requirements.txt')).read().split()
tests_require = []

setup(
    name='sphinxsearch',
    version='0.1.0',
    author='Daniil Oralkov',
    packages=find_packages(),
    test_suite='sphinxsearch.tests',
    url='https://bitbucket.org/insanemainframe/sphinxsearch',
    license='GPL',
    requires=requires,
    tests_require=tests_require,
    description='High-level sphinxsearch library',
    long_description=README + '\n\n' + CHANGES,
)
