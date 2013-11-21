#!/usr/bin/env python
# encoding: utf-8

"""Setup for bundle package
"""

__author__    = "Francis Liu"
__copyright__ = "Copyright 2013, AIMES project"
__email__     = "liux2102@umn.edu"
__license__   = "MIT"

import os
from setuptools import setup, find_packages


#-----------------------------------------------------------------------------
#
def get_version():
    # If there is a VERSION file, use its contents. otherwise, call git to
    # get a version string. if that also fails, use 'latest'.
    version = "latest"
    try:
        cwd = os.path.dirname(os.path.abspath(__file__))
        fn = os.path.join(cwd, 'src/bundle/VERSION')
        version = open(fn).read().strip()

    except IOError:
        from subprocess import Popen, PIPE, STDOUT
        import re

        VERSION_MATCH = re.compile(r'\d+\.\d+\.\d+(\w|-)*')

        try:
            p = Popen(['git', 'describe', '--tags', '--always'],
                      stdout=PIPE, stderr=STDOUT)
            out = p.communicate()[0]

            if (not p.returncode) and out:
                v = VERSION_MATCH.search(out)
                if v:
                    version = v.group()
        except OSError:
            pass

    return version


#-----------------------------------------------------------------------------
#
def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


#-----------------------------------------------------------------------------
#
setup(name='bundle',
      version=get_version(),
      author='Francis Liu',
      author_email='liux2102@umn.edu',
      description="TODO",
      long_description=(read('README.rst') + '\n\n' + read('CHANGES.rst')),
      license='MIT',
      keywords="aimes bundle_manager",
      # https://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers = [
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Natural Language :: English',
	  'Operating System :: POSIX :: Linux',
          'Topic :: Internet :: Scientific/Engineering'],
      url='http://aimes-project.org/',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      #namespace_packages=['rhythmos'],
      #scripts=['bin/aimes-cmdline-tool'],
      # TODO: add more packages
      install_requires=['paramiko', 'setuptools'],
      #test_suite = 'rhythmos.agent.tests',
      package_data = {
          # If any package contains *.txt or *.rst files, include them:
          '': ['VERSION']
      },
      include_package_data = True,
      zip_safe = False
      )
