# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'planner',
    'name'        : 'default',
    'version'     : '0.1',
    'description' : 'This is the default planner.'
  }

from   troy.constants import *
import troy

# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS(object):
    """
    This class implements the default planner for TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__(self):

        troy._logger.info ("create the default planner plugin")


    # --------------------------------------------------------------------------
    #
    def init (self):

        troy._logger.info ("init the default planner plugin")


    # --------------------------------------------------------------------------
    #
    def expand_workload(self, workload):

        # Do nothing for now
        
        troy._logger.info ("planner  expand wl: expand workload : %s" % workload)


    # --------------------------------------------------------------------------
    #
    def derive_overlay(self, workload):

        ovl_descr = troy.OverlayDescription (
            {
                # Ask for as many pilots as tasks
                'cores' : len(workload.tasks), 
                # Minutes obviously
                'wall_time' : (1 << 1) + (1 << 3) + (1 << 5)
            })

        troy._logger.info ("planner  derive ol: derive overlay for workload: %s" % ovl_descr)

        # Create an overlay
        return troy.Overlay(ovl_descr)


# ------------------------------------------------------------------------------
