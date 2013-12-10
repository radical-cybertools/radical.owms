
__author__    = "Andre Merzky, Ole Weidner"
__copyright__ = "Copyright 2013, RADICAL Research, Rutgers University"
__license__   = "MIT"


""" Setup script. Used by easy_install and pip. """

import os
import sys
import subprocess

from setuptools import setup, Command


#-----------------------------------------------------------------------------
#
# versioning mechanism:
#
#   - short_version:  1.2.3 - is used for installation
#   - long_version:  v1.2.3-9-g0684b06  - is used as runtime (ru.version)
#   - both are derived from the last git tag
#   - the file troy/VERSION is created with the long_version, und used
#     by ru.__init__.py to provide the runtime version information. 
#
def get_version():

    short_version = None  # 0.4.0
    long_version  = None  # 0.4.0-9-g0684b06

    try:
        import subprocess as sp
        import re

        srcroot       = os.path.dirname (os.path.abspath (__file__))
        VERSION_MATCH = re.compile (r'(([\d\.]+)\D.*)')

        # attempt to get version information from git
        p   = sp.Popen ('cd %s && git describe --tags --always' % srcroot,
                        stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)
        out = p.communicate()[0]


        if  p.returncode != 0 or not out :

            # the git check failed -- its likely that we are called from
            # a tarball, so use ./VERSION instead
            out=open ("%s/VERSION" % srcroot, 'r').read().strip()


        # from the full string, extract short and long versions
        v = VERSION_MATCH.search (out)
        if v:
            long_version  = v.groups ()[0]
            short_version = v.groups ()[1]


        # sanity check if we got *something*
        if  not short_version or not long_version :
            sys.stderr.write ("Cannot determine version from git or ./VERSION\n")
            import sys
            sys.exit (-1)


        # make sure the version files exist for the runtime version inspection
        open (     '%s/VERSION' % srcroot, 'w').write (long_version+"\n")
        open ('%s/troy/VERSION' % srcroot, 'w').write (long_version+"\n")


    except Exception as e :
        print 'Could not extract/set version: %s' % e
        import sys
        sys.exit (-1)

    return short_version, long_version


short_version, long_version = get_version ()

#-----------------------------------------------------------------------------
# check python version. we need > 2.5, <3.x
if  sys.hexversion < 0x02050000 or sys.hexversion >= 0x03000000:
    raise RuntimeError("Troy requires Python 2.x (2.5 or higher)")


#-----------------------------------------------------------------------------
class our_test(Command):
    user_options = []
    def initialize_options (self) : pass
    def finalize_options   (self) : pass
    def run (self) :
        testdir = "%s/tests/" % os.path.dirname(os.path.realpath(__file__))
        retval  = subprocess.call([sys.executable, 
                                   '%s/run_tests.py'               % testdir,
                                   '%s/configs/workload_input.cfg' % testdir])
        raise SystemExit(retval)


#-----------------------------------------------------------------------------
#
def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


#-----------------------------------------------------------------------------
setup_args = {
    'name'             : "troy",
    'version'          : short_version,
    'description'      : "Tiered Resource OverlaY",
    'long_description' : (read('README.md') + '\n\n' + read('CHANGES.md')),    
    'author'           : 'RADICAL Group at Rutgers University',
    'author_email'     : "radical@rutgers.edu",
    'maintainer'       : "Andre Merzky",
    'maintainer_email' : "andre@merzky.net",
    'url'              : "http://saga-project.github.com/troy/",
    'license'          : "MIT",
    'keywords'         : "radical pilot job saga",
    'classifiers'      : [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Environment :: Console',                    
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
        'Topic :: System :: Distributed Computing',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix',
    ],
    'packages': [
        "troy",
        "troy.utils",
        "troy.planner",
        "troy.overlay",
        "troy.workload",
        "troy.plugins",
        "troy.plugins.planner",
        "troy.plugins.overlay_inspector",
        "troy.plugins.overlay_translator",
        "troy.plugins.overlay_scheduler",
        "troy.plugins.overlay_provisioner",
        "troy.plugins.workload_inspector",
        "troy.plugins.workload_scheduler",
        "troy.plugins.workload_translator",
        "troy.plugins.workload_dispatcher",
        "troy.external",
        "troy.external.bundle",
        "troy.external.bundle.src",
        "troy.external.bundle.src.bundle",
        "troy.external.bundle.src.bundle.impl",
        "troy.external.bundle.src.bundle.api",
        "troy.external.bundle.src.bundle.example",
        "troy.bundle_wrapper",
    ],
    'scripts'          : [],
    'package_data'     : {'' : ['VERSION']},
    'cmdclass'         : {
        'test'         : our_test,
    },
    'install_requires' : ['saga-python', 'radical.utils', 'bigjob', 'paramiko'],
    'tests_require'    : ['nose'],
    'zip_safe'         : False,
#   'build_sphinx'     : {
#       'source-dir'   : 'docs/',
#       'build-dir'    : 'docs/build',
#       'all_files'    : 1,
#   },
#   'upload_sphinx'    : {
#       'upload-dir'   : 'docs/build/html',
#   }
}

#-----------------------------------------------------------------------------

setup(**setup_args)

#-----------------------------------------------------------------------------

