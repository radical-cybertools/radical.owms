
__author__    = "Mark Santcroos"
__copyright__ = "Copyright 2013, RADICAL @ Rutgers"
__license__   = "MIT"


import imp

# ------------------------------------------------------------------------------
#
def test_bundle_import():
    """
    test the import of the bundle module
    """

    try:
        imp.find_module('troy.external.bundle')
    except ImportError:
        assert False, 'Can not find (external) bundle module'
