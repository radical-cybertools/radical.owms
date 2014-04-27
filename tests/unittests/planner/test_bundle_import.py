
__author__    = "Mark Santcroos"
__copyright__ = "Copyright 2013, RADICAL @ Rutgers"
__license__   = "MIT"


# ------------------------------------------------------------------------------
#
def test_bundle_import():
    """
    test the import of the bundle module
    """

    try:
        from radical.owms.bundle_wrapper import BundleManager
    except ImportError:
        assert False, 'Can not find (external) bundle module'
