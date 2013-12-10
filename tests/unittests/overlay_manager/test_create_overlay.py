
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
    tc      = rut.get_test_config ()
    ol_dict = tc.overlay_dict
    ol      = troy.Overlay ({'cores' : 1})

    if  not 'pilots' in ol_dict :
        assert False, "no pilots in overlay dict" 

    if  not len(ol_dict['pilots']) :
        assert False, "zero pilots in overlay dict" 

    for pilot_dict in ol_dict['pilots'] :
        pilot_description = troy.PilotDescription (pilot_dict)
        ol._add_pilot (pilot_description)

  # ol._dump ()

