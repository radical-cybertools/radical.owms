

import radical.utils as ru

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'planner',
    'name'        : 'default',
    'version'     : '0.1',
    'description' : 'This is the default planner.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (troy.PluginBase):
    """
    This class implements the default planner for TROY.
    """

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__(self):

        troy.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


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
