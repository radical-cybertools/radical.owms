
__author__    = "Andre Merzky"
__copyright__ = "Copyright 2013, The SAGA Project"
__license__   = "MIT"

import radical.utils as ru

import troy

# ------------------------------------------------------------------------------
#
def test_workload_create () :
    """ 
    test workload creation
    """
    try:
        tc = ru.get_test_config ()
        wl_dict = tc.workload_dict
        wl_mgr  = troy.WorkloadManager ()
        print wl_dict


    except Exception as ex:
        assert False, "unexpected exception %s" % ex



