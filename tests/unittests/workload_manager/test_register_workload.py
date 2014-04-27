

__author__    = "Andre Merzky"
__copyright__ = "Copyright 2013, The SAGA Project"
__license__   = "MIT"


import radical.utils.testing as rut

import radical.owms

# ------------------------------------------------------------------------------
#
def test_workload_create () :
    """ 
    test workload creation
    """
    wl1  = radical.owms.Workload ()
    wlid = wl1.id

    wl2 = radical.owms.WorkloadManager.get_workload (wlid)

    assert wl1 == wl2, "%s == %s" % (wl1, wl2)

    radical.owms.WorkloadManager.unregister_workload (wlid)

    try :
        wl2 = radical.owms.WorkloadManager.get_workload (wlid)
        assert False, "Expected LookupError, got nothing"

    except LookupError :
        pass

    except Exception as e :
        assert False, "Expected LookupError, got %s" % e



