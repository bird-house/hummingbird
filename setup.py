import os

from setuptools import setup, find_packages

import hummingbird

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

reqs = [line.strip() for line in open('requirements/deploy.txt')]

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Science/Research',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering :: Atmospheric Science',
]

setup(name='hummingbird',
      version=hummingbird.__version__,
      description='WPS processes for general tools used in the climate science community like cdo',
      long_description=README + '\n\n' + CHANGES,
      classifiers=classifiers,
      author='Birdhouse',
      url='https://github.com/bird-house/hummingbird',
      license="Apache License v2.0",
      keywords='wps pywps hummingbird birdhouse conda cdo climate quality cfchecker',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='hummingbird',
      install_requires=reqs,
      entry_points={
          'console_scripts': []
      },
      )
