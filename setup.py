
__author__    = "RADICAL Team"
__copyright__ = "Copyright 2013, RADICAL Research, Rutgers University"
__license__   = "MIT"


""" Setup script. Used by easy_install and pip. """

import re
import os
import sys
import subprocess as sp

from setuptools import setup, Command

srcroot = 'troy'
name    = 'troy'

# ------------------------------------------------------------------------------
#
# versioning mechanism:
#
#   - short_version:  1.2.3                   - is used for installation
#   - long_version:   1.2.3-9-g0684b06-devel  - is used as runtime (ru.version)
#   - both are derived from the last git tag and branch information
#   - VERSION files are created on demand, with the long_version
#
# can't use radical.utils versioning detection, as radical.utils is only
# below specified as dependency :/
def get_version (paths=None):
    """
    paths:
        a VERSION file containing the long version is created in every directpry
        listed in paths.  Those VERSION files are used when they exist to get
        the version numbers, if they exist prior to calling this method.  If 
        not, we cd into the first path, try to get version numbers from git tags 
        in that location, and create the VERSION files in all dirst given in 
        paths.
    """

    try:

        if  None == paths :
            # by default, get version for myself
            pwd     = os.path.dirname (__file__)
            root    = "%s/.." % pwd
            paths = [root, pwd]

        if  not isinstance (paths, list) :
            paths = [paths]

        long_version  = None
        short_version = None
        branch_name   = None


        # if in any of the paths a VERSION file exists, we use the long version
        # in there.
        for path in paths :

            try :

                filename = "%s/VERSION" % path

                with open (filename) as f :
                    line = f.readline()
                    line.strip()
                    pattern = re.compile ('^\s*(?P<long>(?P<short>[^-@]+?)(-[^@]+?)?(?P<branch>@.+?)?)\s*$')
                    match   = pattern.search (line)
    
                    if  match :
                        long_version  = match.group ('long')
                        short_version = match.group ('short')
                        branch_name   = match.group ('branch')
                        print 'reading  %s' % filename
                        break

            except Exception as e :
                # ignore missing VERSION file -- this is caught below
                pass


        # if we didn't find it, get it from git 
        if  not long_version :

            # make sure we look at the right git repo
            if  len(paths) :
                git_cd  = "cd %s ;" % paths[0]

            # attempt to get version information from git
            p   = sp.Popen ('%s'\
                            'git describe --tags --always ; ' \
                            'git branch   --contains | grep -e "^\*"' % git_cd,
                            stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)
            out = p.communicate()[0]

            if  p.returncode == 0 and out :

                pattern = re.compile ('(?P<long>(?P<short>[\d\.]+).*?)(\s+\*\s+(?P<branch>\S+))?$')
                match   = pattern.search (out)

                if  match :
                    long_version  = match.group ('long')
                    short_version = match.group ('short')
                    branch_name   = match.group ('branch')
                    print 'inspecting git for version info'

                    # if not on master, make sure the branch is part of the long version
                    if  branch_name and not branch_name == 'master' :
                        long_version = "%s@%s" % (long_version, branch_name)


        # check if either one worked ok
        if  None == long_version :
            raise RuntimeError ("Cannot determine version from git or ./VERSION\n")


        # make sure the version files exist for the runtime version inspection
        for path in paths :
            vpath = '%s/VERSION' % path
            print 'creating %s'  % vpath
            with open (vpath, 'w') as f :
                f.write (long_version  + "\n")
    
        return short_version, long_version, branch_name


    except Exception as e :
        raise RuntimeError ("Could not extract/set version: %s" % e)


#-----------------------------------------------------------------------------
# get version info -- this will create VERSION and srcroot/VERSION
root     = os.path.dirname (__file__)
if  not root :
    root = os.getcwd()
src_dir  = "%s/%s" % (root, srcroot)
short_version, long_version, branch = get_version ([root, src_dir])


#-----------------------------------------------------------------------------
# check python version. we need > 2.5, <3.x
if  sys.hexversion < 0x02050000 or sys.hexversion >= 0x03000000:
    raise RuntimeError("%s requires Python 2.x (2.5 or higher)" % name)


#-----------------------------------------------------------------------------
class our_test(Command):
    user_options = []
    def initialize_options (self) : pass
    def finalize_options   (self) : pass
    def run (self) :
        testdir = "%s/tests/" % os.path.dirname(os.path.realpath(__file__))
        retval  = sp.call([sys.executable,
                          '%s/run_tests.py'               % testdir,
                          '%s/configs/workload_input.cfg' % testdir])
        raise SystemExit(retval)


#-----------------------------------------------------------------------------
#
def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


#-----------------------------------------------------------------------------
setup_args = {
    'name'             : name,
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
        'Operating System :: Unix'
    ],
    'packages'         : [
        "troy",
        "troy.utils",
        "troy.application",
        "troy.planner",
        "troy.overlay",
        "troy.workload",
        "troy.plugins",
        "troy.plugins.planner_strategy",
        "troy.plugins.planner_derive",
        "troy.plugins.overlay_translator",
        "troy.plugins.overlay_scheduler",
        "troy.plugins.overlay_provisioner",
        "troy.plugins.workload_parser",
        "troy.plugins.workload_translator",
        "troy.plugins.workload_expander",
        "troy.plugins.workload_scheduler",
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
    'scripts'          : ['bin/owms.py', 'bin/troy-version'],
    'package_data'     : {'' : ['VERSION', 'resources.json']},
    'cmdclass'         : {
        'test'         : our_test,
    },
    'install_requires' : ['saga-python', 'radical.utils'],
    'extras_require'   : {
        'radical.pilot':  ["radical.pilot"],
        'bigjob'       :  ["bigjob"],
        'bundles'      :  ["paramiko"]
    },
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

setup (**setup_args)

#-----------------------------------------------------------------------------

