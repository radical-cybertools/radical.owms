

__author__    = "Andre Merzky"
__copyright__ = "Copyright 2013, The SAGA Project"
__license__   = "MIT"


import radical.utils.testing as rut

import troy

# ------------------------------------------------------------------------------
#
def test_workload_create () :
    """ 
    test workload creation
    """
    wl1  = troy.Workload ()
    wlid = wl1.id

    troy.WorkloadManager.register_workload  (wl1)
    wl2 = troy.WorkloadManager.get_workload (wlid)

    assert wl1 == wl2, "%s == %s" % (wl1, wl2)

    troy.WorkloadManager.unregister_workload (wlid)

    try :
        wl2 = troy.WorkloadManager.get_workload (wlid)
        assert False, "Expected LookupError, got nothing"

    except LookupError :
        pass

    except Exception as e :
        assert False, "Expected LookupError, got %s" % e



