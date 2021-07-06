#!/usr/bin/env python

"""The setup script."""

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
REQUIRES_PYTHON = ">=3.6.0"

about = {}
with open(os.path.join(here, 'hummingbird', '__version__.py'), 'r') as f:
    exec(f.read(), about)

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', ]

requirements = [line.strip() for line in open('requirements.txt')]

dev_reqs = [line.strip() for line in open('requirements_dev.txt')]

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'Natural Language :: English',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Topic :: Scientific/Engineering :: Atmospheric Science',
    'License :: OSI Approved :: Apache Software License',
]

setup(name='hummingbird',
      version=about['__version__'],
      description="A Web Processing Service for metadata compliance checks used in the climate science community.",
      long_description=README + '\n\n' + CHANGES,
      long_description_content_type="text/x-rst",
      author=about['__author__'],
      author_email=about['__email__'],
      url='https://github.com/bird-house/hummingbird',
      python_requires=REQUIRES_PYTHON,
      classifiers=classifiers,
      license="Apache Software License 2.0",
      keywords='wps pywps birdhouse hummingbird',
      packages=find_packages(),
      include_package_data=True,
      install_requires=requirements,
      setup_requires=setup_requirements,
      test_suite = 'tests',
      tests_require = test_requirements,
      extras_require={
          "dev": dev_reqs,  # pip install ".[dev]"
      },
      entry_points={
          'console_scripts': [
              'hummingbird=hummingbird.cli:cli',
          ]},)
