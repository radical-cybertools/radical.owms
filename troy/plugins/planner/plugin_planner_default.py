# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'planner',
    'name'        : 'default',
    'version'     : '0.1',
    'description' : 'This is the default planner.'
  }

import troy.overlay       as to
from   troy.constants import *


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS(object):
    """
    This class implements the default planner for TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__(self):

        print "create the default planner plugin"

    # --------------------------------------------------------------------------
    #
    def expand_workload(self, workload):

        # Do nothing for now
        
        print "planner  expand wl: expand workload : %s" % workload


    # --------------------------------------------------------------------------
    #
    def derive_overlay(self, workload):

        ovl_descr = to.OverlayDescription ( 
            {
                # Ask for as many pilots as tasks
                'cores' : len(workload.tasks), 
                # Minutes obviously
                'wall_time' : (1 << 1) + (1 << 3) + (1 << 5)
            })

        print "planner  derive ol: derive overlay for workload: %s" % ovl_descr

        # Create an overlay
        return to.Overlay(ovl_descr)


# ------------------------------------------------------------------------------

