

__author__    = "Andre Merzky"
__copyright__ = "Copyright 2013, The SAGA Project"
__license__   = "MIT"


import radical.utils.testing as rut

import troy

# ------------------------------------------------------------------------------
#
def test_overlay_create () :
    """ 
    test overlay creation
    """
    tc = rut.get_test_config ()
    wl_dict = tc.overlay_dict
    wl1     = troy.overlay ()
    wlid = wl1.id

    troy.overlayManager.register_overlay  (wl1)
    wl2 = troy.overlayManager.get_overlay (wlid)

    assert wl1 == wl2, "%s == %s" % (wl1, wl2)

    troy.overlayManager.unregister_overlay (wlid)

    try :
        wl2 = troy.OverlayManager.get_overlay (wlid)
        assert False, "Expected LookupError, got nothing"

    except LookupError :
        pass

    except Exception as e :
        assert False, "Expected LookupError, got %s" % e



